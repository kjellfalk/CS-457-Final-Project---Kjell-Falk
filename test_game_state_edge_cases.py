
import threading

from game_state import GameState


def create_ready_game():
    """Create a fresh game with two registered, ready players."""

    game = GameState()

    game.add_player("P1")
    game.add_player("P2")

    game.submit_secret_code("P1", "RGBY")
    game.submit_secret_code("P2", "WUUB")

    game.mark_ready("P1")
    game.mark_ready("P2")

    game.try_start()

    return game


def submit_turn(game, round_number, turn_number,
                p1_guess, p2_guess):
    """Submit both players' guesses concurrently."""

    results = {}

    def submit_p1():
        results["P1"] = game.submit_guess(
            "P1", round_number, turn_number, p1_guess
        )

    def submit_p2():
        results["P2"] = game.submit_guess(
            "P2", round_number, turn_number, p2_guess
        )

    p1_thread = threading.Thread(target=submit_p1)
    p2_thread = threading.Thread(target=submit_p2)

    p1_thread.start()
    p2_thread.start()

    p1_thread.join()
    p2_thread.join()

    return results


# --------------------------------------------------
# Test 1: Ten-turn exhaustion
# --------------------------------------------------

game = create_ready_game()

print("\n--- Test 1: Ten-turn exhaustion ---")

for turn in range(1, 11):

    results = submit_turn(
        game,
        1,
        turn,
        "RRRR",
        "GGGG"
    )

    print(f"Turn {turn}:")
    print("P1 feedback:", results["P1"])
    print("P2 feedback:", results["P2"])


print("\nFinal round state:")
print("Round over:", game.round_over)
print("Current round:", game.current_round)
print("Current turn:", game.current_turn)
print("Scores:", game.scores)
print("Round results:", game.round_result)

assert results["P1"]["round_result"] == "draw"
assert results["P2"]["round_result"] == "draw"

assert game.current_round == 2
assert game.current_turn == 1

assert game.scores == {
    "P1": 0,
    "P2": 0
}

assert game.round_over is False

print("\nTest 1 passed!")

# --------------------------------------------------
# Test 2: Simultaneous solution
# --------------------------------------------------

game = create_ready_game()

print("\n--- Test 2: Simultaneous solution ---")

results = submit_turn(
    game,
    1,
    1,
    "WUUB",
    "RGBY"
)

print("P1 feedback:", results["P1"])
print("P2 feedback:", results["P2"])

print("\nFinal round state:")
print("Round over:", game.round_over)
print("Scores:", game.scores)
print("Round results:", game.round_result)

assert results["P1"]["exact_matches"] == 4
assert results["P2"]["exact_matches"] == 4

assert results["P1"]["round_result"] == "draw"
assert results["P2"]["round_result"] == "draw"

assert results["P1"]["player_score"] == 1
assert results["P2"]["player_score"] == 1

assert game.scores == {
    "P1": 1,
    "P2": 1
}

assert game.current_round == 2
assert game.current_turn == 1

print("\nTest 2 passed!")
