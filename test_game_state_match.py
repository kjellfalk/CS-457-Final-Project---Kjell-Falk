
import threading

from game_state import GameState


game = GameState()

game.add_player("P1")
game.add_player("P2")

game.submit_secret_code("P1", "RGBY")
game.submit_secret_code("P2", "WUUB")

game.mark_ready("P1")
game.mark_ready("P2")

print("Game started:", game.try_start())


def play_turn(round_number):
    """Submit one synchronized pair of guesses."""

    results = {}

    def submit_p1():
        results["P1"] = game.submit_guess(
            "P1",
            round_number,
            1,
            "WUUB"
        )

    def submit_p2():
        results["P2"] = game.submit_guess(
            "P2",
            round_number,
            1,
            "RRRR"
        )

    p1_thread = threading.Thread(target=submit_p1)
    p2_thread = threading.Thread(target=submit_p2)

    p1_thread.start()
    p2_thread.start()

    p1_thread.join()
    p2_thread.join()

    return results


# Play all three rounds.
for round_number in range(1, 4):

    print(f"\n--- Round {round_number} ---")

    results = play_turn(round_number)

    print("P1 feedback:", results["P1"])
    print("P2 feedback:", results["P2"])

    print("Current scores:", game.scores)


print("\n--- Match complete ---")
print("Final scores:", game.scores)
print("Match results:", game.match_result)
print("Match over:", game.match_over)
