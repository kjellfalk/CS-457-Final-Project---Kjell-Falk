
import socket

from protocol import encode_message, MessageBuffer


HOST = "127.0.0.1"
PORT = 5000


def main():
    """Connect to the server and play one synchronized turn."""

    player_id = input("Enter player ID (P1 or P2): ").upper()
    secret_code = input("Enter your four-character secret code: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver = MessageBuffer()

    try:
        client.connect((HOST, PORT))

        print(f"Connected to server at {HOST}:{PORT}")

        hello = {"type": "hello"}
        client.sendall(encode_message(hello))

        print("Sent hello message.")

        game_started = False
        awaiting_guess = False

        current_round = 1
        current_turn = 1

        while True:
            if game_started and awaiting_guess:

                guess_code = input(
                    f"{player_id}, Round {current_round}, "
                    f"Turn {current_turn} — enter your guess: "
                )

                guess_message = {
                    "type": "guess",
                    "round": current_round,
                    "turn": current_turn,
                    "guess_code": guess_code
                }

                client.sendall(encode_message(guess_message))

                awaiting_guess = False

                print("Guess submitted. Waiting for opponent...")

            data = client.recv(1024)

            if not data:
                print("Server disconnected.")
                break

            messages = receiver.receive_data(data)

            for message in messages:
                message_type = message["type"]

                print(f"Received: {message}")

                if message_type == "connection_ack":
                    identify = {
                        "type": "identify",
                        "player": player_id,
                        "game": "mastermind"
                    }

                    client.sendall(encode_message(identify))

                    code_commit = {
                        "type": "code_commit",
                        "code": secret_code
                    }

                    client.sendall(encode_message(code_commit))

                    client_ready = {
                        "type": "client_ready"
                    }

                    client.sendall(encode_message(client_ready))

                    print("Submitted code and indicated readiness.")

                elif message_type == "begin_game":
                    print("Both players are ready. Game begins!")
                    game_started = True
                    awaiting_guess = True

                elif message_type == "feedback":

                    print(f"\nRound {message['round']}, Turn {message['turn']}")
                    print(f"Exact matches: {message['exact_matches']}")
                    print(f"Misplaced matches: {message['misplaced_matches']}")

                    print(
                        f"Your score: {message['player_score']} | "
                        f"Opponent score: {message['opponent_score']}"
                    )

                    if message["round_result"] is not None:
                        print(f"Round result: {message['round_result']}")

                    if message["match_result"] is not None:
                        print(f"Match result: {message['match_result']}")
                        print("Match complete!")
                        return

                    if message["round_result"] is not None:
                        current_round += 1
                        current_turn = 1
                        print(f"\nStarting round {current_round}.")

                    else:
                        current_turn += 1

                    awaiting_guess = True

    except ConnectionError as error:
        print(f"Connection error: {error}")

    finally:
        client.close()
        print("Client connection closed.")

if __name__ == "__main__":
    main()
