
import threading

from mastermind import VALID_SYMBOLS, evaluate_guess, validate_code


class PlayerState:
    """Represent the server-side state of one player."""

    def __init__(self, player_id):
        self.player_id = player_id
        self.secret_code = None
        self.ready = False


class GameState:
    """Maintain the authoritative state of a two-player game."""

    def __init__(self):
        self.players = {}
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

        self.game_started = False

        self.current_turn = 1
        self.guesses = {}
        self.turn_feedback = None
        self.feedback_delivered = set()

        self.current_round = 1
        self.max_rounds = 3
        self.max_turns = 10

        self.scores = {
            "P1": 0,
            "P2": 0
        }

        self.round_over = False
        self.match_over = False

        self.round_result = None
        self.match_result = None

    def add_player(self, player_id):
        """Register a player in the game state."""

        if player_id not in ("P1", "P2"):
            raise ValueError("Invalid player ID.")

        with self.lock:
            if player_id in self.players:
                raise ValueError("Player is already registered.")

            self.players[player_id] = PlayerState(player_id)

    def remove_player(self, player_id):
        """Remove a player and notify any waiting threads."""

        with self.condition:
            self.players.pop(player_id, None)
            self.condition.notify_all()

    def submit_secret_code(self, player_id, code):
        """Validate and store a player's secret code."""

        if not isinstance(code, str):
            raise ValueError("Code must be a string.")

        code = code.upper()

        if len(code) != 4:
            raise ValueError("Code must contain exactly four characters.")

        if any(symbol not in VALID_SYMBOLS for symbol in code):
            raise ValueError("Code contains an invalid symbol.")

        with self.lock:
            if player_id not in self.players:
                raise ValueError("Player is not registered.")

            player = self.players[player_id]

            player.secret_code = code
            player.ready = False

    def mark_ready(self, player_id):
        """Mark a player as ready after code submission."""

        with self.lock:
            if player_id not in self.players:
                raise ValueError("Player is not registered.")

            player = self.players[player_id]

            if player.secret_code is None:
                raise ValueError("Player must submit a code first.")

            player.ready = True

    def both_players_ready(self):
        """Determine whether both players are ready."""

        with self.lock:
            if len(self.players) != 2:
                return False

            return all(
                player.ready and player.secret_code is not None
                for player in self.players.values()
            )

    def get_player_status(self):
        """Return player readiness without exposing secret codes."""

        with self.lock:
            return {
                player_id: {
                    "has_code": player.secret_code is not None,
                    "ready": player.ready
                }
                for player_id, player in self.players.items()
            }

    def try_start(self):
        """Start the game once, if both players are ready."""

        with self.lock:
            if self.game_started:
                return False

            if len(self.players) != 2:
                return False

            if not all(
                player.ready and player.secret_code is not None
                for player in self.players.values()
            ):
                return False

            self.game_started = True
            return True

    

    def submit_guess(self, player_id, round_number, turn, guess_code):
        """Collect both guesses, evaluate them, and manage game progression."""

        guess_code = validate_code(guess_code)

        if not isinstance(round_number, int) or not isinstance(turn, int):
            raise ValueError("Round and turn must be integers.")

        with self.condition:

            if player_id not in self.players:
                raise ValueError("Player is not registered.")

            if not self.game_started:
                raise ValueError("The game has not started.")

            if self.match_over:
                raise ValueError("The match has already ended.")

            if not 1 <= round_number <= self.max_rounds:
                raise ValueError("Invalid round number.")

            if not 1 <= turn <= self.max_turns:
                raise ValueError("Invalid turn number.")

            # Wait for an earlier turn or round to finish.
            while (round_number, turn) > (
                self.current_round, self.current_turn
            ):
                if self.match_over:
                    raise ValueError("The match has already ended.")

                if player_id not in self.players or len(self.players) != 2:
                    raise ValueError("A player disconnected.")

                self.condition.wait()

            if (round_number, turn) < (
                self.current_round, self.current_turn
            ):
                raise ValueError("This turn has already been completed.")

            if self.round_over:
                raise ValueError("The round has already ended.")

            if player_id in self.guesses:
                raise ValueError("Player already submitted a guess this turn.")

            # Store the guess.
            self.guesses[player_id] = guess_code

            print(
                f"{player_id} submitted a guess "
                f"for round {round_number}, turn {turn}."
            )

            # Evaluate only after both guesses arrive.
            if len(self.guesses) == 2:

                p1_feedback = evaluate_guess(
                    self.players["P2"].secret_code,
                    self.guesses["P1"]
                )

                p2_feedback = evaluate_guess(
                    self.players["P1"].secret_code,
                    self.guesses["P2"]
                )

                self.turn_feedback = {
                    "P1": {
                        "turn": turn,
                        "exact_matches": p1_feedback[0],
                        "misplaced_matches": p1_feedback[1]
                    },
                    "P2": {
                        "turn": turn,
                        "exact_matches": p2_feedback[0],
                        "misplaced_matches": p2_feedback[1]
                    }
                }

                # Resolve a round if someone solved or ten turns elapsed.
                self.resolve_round()

                print(
                    f"Both guesses received for round "
                    f"{round_number}, turn {turn}."
                )

                self.condition.notify_all()

            # Wait for both guesses to be evaluated.
            while self.turn_feedback is None:
                if player_id not in self.players or len(self.players) != 2:
                    raise ValueError("A player disconnected.")

                self.condition.wait()

            # Build this player's private response.
            feedback = dict(self.turn_feedback[player_id])

            feedback["round"] = self.current_round
            feedback["round_result"] = (
                self.round_result[player_id]
                if self.round_over else None
            )

            feedback["player_score"] = self.scores[player_id]
            feedback["opponent_score"] = self.scores[
                "P2" if player_id == "P1" else "P1"
            ]

            feedback["match_result"] = (
                self.match_result[player_id]
                if self.match_over else None
            )

            self.feedback_delivered.add(player_id)

            # Advance only after both players receive their feedback.
            if len(self.feedback_delivered) == 2:

                self.guesses.clear()
                self.turn_feedback = None
                self.feedback_delivered.clear()

                if self.round_over:
                    if not self.match_over:
                        self.current_round += 1
                        self.current_turn = 1
                        self.round_over = False
                        self.round_result = None
                else:
                    self.current_turn += 1

                self.condition.notify_all()

            return feedback

    def resolve_round(self):
        """Determine the round result and update player scores."""

        p1_solved = (
            self.turn_feedback["P1"]["exact_matches"] == 4
        )

        p2_solved = (
            self.turn_feedback["P2"]["exact_matches"] == 4
        )

        if p1_solved and p2_solved:
            self.scores["P1"] += 1
            self.scores["P2"] += 1

            self.round_result = {
                "P1": "draw",
                "P2": "draw"
            }

            self.round_over = True

        elif p1_solved:
            self.scores["P1"] += 1

            self.round_result = {
                "P1": "win",
                "P2": "loss"
            }

            self.round_over = True

        elif p2_solved:
            self.scores["P2"] += 1

            self.round_result = {
                "P1": "loss",
                "P2": "win"
            }

            self.round_over = True

        elif self.current_turn == self.max_turns:
            self.round_result = {
                "P1": "draw",
                "P2": "draw"
            }

            self.round_over = True

        else:
            self.round_result = None

        if self.round_over and self.current_round == self.max_rounds:
            self.match_over = True

            if self.scores["P1"] > self.scores["P2"]:
                self.match_result = {
                    "P1": "win",
                    "P2": "loss"
                }

            elif self.scores["P2"] > self.scores["P1"]:
                self.match_result = {
                    "P1": "loss",
                    "P2": "win"
                }

            else:
                self.match_result = {
                    "P1": "draw",
                    "P2": "draw"
                }
