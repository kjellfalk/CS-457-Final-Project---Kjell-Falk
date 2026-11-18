
import threading
import time

from game_state import GameState


game = GameState()

# Register both players.
game.add_player("P1")
game.add_player("P2")

# Submit their secret codes.
game.submit_secret_code("P1", "RGBY")
game.submit_secret_code("P2", "WUUB")

# Mark both players ready.
game.mark_ready("P1")
game.mark_ready("P2")

# Start the game.
print("Game started:", game.try_start())

results = {}
p1_waiting = threading.Event()


def submit_p1_guess():
    """Submit P1's guess and wait for P2."""

    p1_waiting.set()

    results["P1"] = game.submit_guess(
        "P1",
        1,
        "WUUB"
    )


def submit_p2_guess():
    """Submit P2's guess."""

    results["P2"] = game.submit_guess(
        "P2",
        1,
        "RYGB"
    )


# Start P1's worker first.
p1_thread = threading.Thread(target=submit_p1_guess)
p1_thread.start()

# Wait until P1 is about to submit.
p1_waiting.wait()

# Give P1 time to enter the waiting state.
time.sleep(0.2)

print("\nResults before P2 submits:")
print(results)

# Now start P2's worker.
p2_thread = threading.Thread(target=submit_p2_guess)
p2_thread.start()

# Wait for both workers to finish.
p1_thread.join()
p2_thread.join()

print("\nResults after both submissions:")
print(results)
