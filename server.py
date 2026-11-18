
import socket
import threading

from protocol import encode_message, MessageBuffer
from game_state import GameState


HOST = "127.0.0.1"
PORT = 5000

# Shared connection registry.
connected_players = {}
players_lock = threading.Lock()

# Shared authoritative game state.
game = GameState()


def handle_client(connection, address):
    """Handle communication with one connected client."""

    print(f"Connected to client: {address}")

    receiver = MessageBuffer()
    player_id = None

    try:
        while True:
            data = connection.recv(1024)

            if not data:
                print(f"Client disconnected: {address}")
                break

            messages = receiver.receive_data(data)

            for message in messages:
                message_type = message["type"]

                print(f"Received from {address}: {message}")

                if message_type == "hello":
                    response = {"type": "connection_ack"}
                    connection.sendall(encode_message(response))

                    print(f"Sent acknowledgment to {address}.")

                elif message_type == "identify":
                    requested_player = message.get("player")
                    requested_game = message.get("game")

                    if requested_game != "mastermind":
                        print("Unsupported game selection.")
                        return

                    if requested_player not in ("P1", "P2"):
                        print("Invalid player identification.")
                        return

                    with players_lock:
                        if requested_player in connected_players:
                            print(
                                f"{requested_player} is already connected."
                            )
                            return

                        game.add_player(requested_player)

                        connected_players[requested_player] = connection
                        player_id = requested_player

                    print(f"{player_id} successfully identified.")

                elif message_type == "code_commit":
                    if player_id is None:
                        print("Player must identify before submitting a code.")
                        return

                    code = message.get("code")

                    try:
                        game.submit_secret_code(player_id, code)
                    except ValueError as error:
                        print(f"Invalid code from {player_id}: {error}")
                        return

                    print(f"{player_id} submitted a valid secret code.")

                elif message_type == "client_ready":
                    if player_id is None:
                        print("Player must identify before indicating readiness.")
                        return

                    try:
                        game.mark_ready(player_id)
                    except ValueError as error:
                        print(f"Readiness rejected for {player_id}: {error}")
                        return

                    print(f"{player_id} is ready.")

                    # Only one worker can successfully start the game.
                    if game.try_start():
                        print("Both players are ready. Starting game.")

                        with players_lock:
                            player_connections = list(
                                connected_players.values()
                            )

                        begin_message = {
                            "type": "begin_game"
                        }

                        for player_connection in player_connections:
                            try:
                                player_connection.sendall(
                                    encode_message(begin_message)
                                )
                            except OSError as error:
                                print(f"Could not notify a player: {error}")

                elif message_type == "guess":
                    if player_id is None:
                        print("Player must identify before guessing.")
                        return

                    round_number = message.get("round")
                    turn_number = message.get("turn")
                    guess_code = message.get("guess_code")

                    try:
                        feedback = game.submit_guess(
                            player_id,
                            round_number,
                            turn_number,
                            guess_code
                        )

                    except ValueError as error:
                        print(f"Guess rejected for {player_id}: {error}")
                        return

                    feedback_message = {
                        "type": "feedback",
                        **feedback
                    }

                    connection.sendall(encode_message(feedback_message))

                    print(
                        f"Sent feedback to {player_id} "
                        f"for round {round_number}, turn {turn_number}."
                    )

                    if feedback["round_result"] is not None:
                        print(
                            f"Round {round_number} completed: "
                            f"{feedback['round_result']} for {player_id}."
                        )

                    if feedback["match_result"] is not None:
                        print(
                            f"Match completed: "
                            f"{feedback['match_result']} for {player_id}."
                        )

                    connection.sendall(encode_message(feedback_message))

                    print(f"Sent private feedback to {player_id}.")


                elif message_type == "disconnect":
                    print(f"{player_id or address} requested disconnection.")
                    return

                else:
                    print(f"Unrecognized message type: {message_type}")

    except ConnectionError as error:
        print(f"Connection error with {address}: {error}")

    finally:
        if player_id is not None:
            with players_lock:
                if connected_players.get(player_id) is connection:
                    del connected_players[player_id]
                    game.remove_player(player_id)

            print(f"Removed {player_id} from connected players.")

        connection.close()
        print(f"Connection closed: {address}")


def main():
    """Start the concurrent TCP server."""

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()

    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            connection, address = server.accept()

            worker = threading.Thread(
                target=handle_client,
                args=(connection, address)
            )

            worker.start()

            print(f"Started worker thread for {address}.")

    except KeyboardInterrupt:
        print("\nServer shutting down.")

    finally:
        server.close()


if __name__ == "__main__":
    main()
