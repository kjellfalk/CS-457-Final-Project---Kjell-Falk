
from game_state import GameState


game = GameState()

# Register both players.
game.add_player("P1")
game.add_player("P2")

print("Initial status:")
print(game.get_player_status())

# Submit secret codes.
game.submit_secret_code("P1", "RGBY")
game.submit_secret_code("P2", "WUUB")

print("\nAfter code submission:")
print(game.get_player_status())

# Mark the first player ready.
game.mark_ready("P1")

print("\nAfter P1 is ready:")
print(game.get_player_status())
print("Both ready:", game.both_players_ready())

# Mark the second player ready.
game.mark_ready("P2")

print("\nAfter P2 is ready:")
print(game.get_player_status())
print("Both ready:", game.both_players_ready())

print("\nTesting invalid code:")

try:
    game.submit_secret_code("P1", "ABCD")
except ValueError as error:
    print(f"Correctly rejected: {error}")