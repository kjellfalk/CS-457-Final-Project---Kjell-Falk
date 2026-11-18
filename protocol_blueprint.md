# CS 457 Sprint 1: Application Protocol Blueprint

## 1. Protocol Overview

This protocol defines the application-layer communication between two clients and a server for a symmetrical Mastermind game.

Both players independently submit a secret four-character code and attempt to guess their opponent's code. The server maintains both secret codes, collects guesses from both players during each round, evaluates the guesses, and distributes feedback.

The protocol uses structured JSON messages exchanged over a TCP connection. Each message identifies its semantic type and carries any additional information required for that message.

The protocol covers connection establishment, player identification, secret-code submission, readiness, synchronized gameplay, feedback distribution, game completion, and connection termination.

## 2. Transport and Serialization

### Transport

The protocol uses TCP for client-server communication.

TCP provides a reliable byte stream between the client and server, but does not preserve application-level message boundaries.

### Serialization

Protocol messages are serialized as UTF-8 encoded JSON objects.

Each JSON object represents one application-level message and contains a 'type' field identifying the semantic message type.

## 3. Game Rules and Validation

### Code Structure

Each player independently submits a four-character secret code. Each player must also submit a four-character guess during every round.

### Permitted Elements

The game uses six distinct elements, represented by the following characters:

| Element | Character |
|---|---|
| Red | `R` |
| Green | `G` |
| Blue | `U` |
| Yellow | `Y` |
| Black | `B` |
| White | `W` |

### Code Validation

- Codes must contain exactly four characters.
- Only the six permitted characters may be used.
- Uppercase and lowercase input are both accepted.
- All codes are converted to uppercase internally.
- Repeated characters are permitted.
- Invalid codes must be rejected.

### Feedback

The server evaluates each guess against the opponent's secret code and returns:

- `exact_matches`: The number of elements that match both the value and position.
- `misplaced_matches`: The number of elements that match in value but occupy an incorrect position.

Each character may contribute to only one feedback count. Exact matches are counted first, and remaining characters are evaluated for misplaced matches without counting any character more than once.

Both players' guesses must be received before either guess is evaluated or feedback is distributed.

### Round Completion and Scoring

- Each player may submit a maximum of ten guesses per round.
- Each turn consists of one guess submitted by each player.
- Both guesses must be received before either guess is evaluated.
- A round ends immediately after a turn in which at least one player correctly guesses the opponent's secret code, or after both players have exhausted their ten guesses.
- If only one player correctly guesses the opponent's code, that player receives one round point.
- If both players correctly guess the opponent's code during the same turn, each player receives one round point.
- If neither player solves the opponent's code within ten guesses, neither player receives a round point.

### Match Completion

- Each match consists of exactly three rounds.
- The server maintains each player's accumulated round points throughout the match.
- After the third round, the server compares the players' accumulated points and declares the match winner.
- The player with the higher point total wins the match.
- If both players have equal point totals, the match ends in a draw.
- Either player may terminate the match before its normal completion.
- If a player disconnects during a round, the server terminates the match, notifies the remaining player when possible, and releases the associated session resources.
- If a player declines to continue between rounds, the server terminates the match gracefully.

## 4. Message Types

| Message Type | Direction | Purpose |
|---|---|---|
| `hello` | Client → Server | Initiate application-level communication |
| `connection_ack` | Server → Client | Acknowledge the client's connection |
| `identify` | Client → Server | Identify the player |
| `code_commit` | Client → Server | Submit the player's secret code to the server |
| `client_ready` | Client → Server | Indicate that the player has submitted a secret code and is ready |
| `begin_game` | Server → Client | Indicate that both players are ready and gameplay is beginning |
| `round_start` | Server → Client | Indicate that a new symmetrical round is beginning |
| `guess` | Client → Server | Submit a guess against the opponent's secret code |
| `feedback` | Server → Client | Return feedback evaluating the player's guess |
| `round_outcome` | Server → Client | Communicate the final game result |
| `match_outcome` | Server → Client | Communicate the final result of the three-round match to each player |
| `rematch_intent` | Client → Server | Indicate whether the player wants to play again |
| `disconnect` | Client → Server | Indicate intentional termination |

## 5. Message Schemas

### 'hello'

	**Direction:** Client → Server

	**Purpose:** Initiate application-level communication

	**Required information:**
	- Message type

	**Fields:**
	- `type`

	**Example:**
	```json
	{
		"type": "hello"
	}
	```

### `connection_ack`

	**Direction:** Server → Client

	**Purpose:** Acknowledge the client's connection

	**Required information:**
	- Message type

	**Fields:**
	- `type`

	**Example:**
	```json
	{
		"type": "connection_ack"
	}
	```

### `identify`

	**Direction:** Client → Server

	**Purpose:** Identify the player and selected game

	**Required information:**
	- Client/player identity
	- Game selection

	**Fields:**
	- `type`
	- `player`
	- `game`

	**Example:**
	```json
	{
		"type": "identify",
		"player": "...",
		"game": "..."
	}
	```

### `code_commit`

	**Direction:** Client → Server

	**Purpose:** Submit the player's secret four-character code to the server.

	**Required information:**
	- The player's secret code

	**Fields:**
	- `type`
	- `code`

	**Example:**
	```json
	{
		"type": "code_commit",
		"code": "ABCD"
	}
	```

	**Server behavior:**
	- Associate the submitted code with the player who sent it.
	- Store the code privately on the server.
	- Do not disclose the code to the opposing player.
	- Reject invalid code submissions.

### `client_ready`

	**Direction:** Client → Server

	**Purpose:** Indicate that the player has submitted a valid secret code and is ready to begin the game.

	**Required information:**
	- Message type

	**Fields:**
	- `type`

	**Example:**
	```json
	{
		"type": "client_ready"
	}
	```

	**Server behavior:**
	- Confirm that the player has already submitted a valid secret code.
	- Mark that player as ready.
	- Wait until both players have submitted valid secret codes and indicated that they are ready.
	- Do not begin gameplay until both players are ready.

### `begin_game`

	**Direction:** Server → Client

	**Purpose:** Notify both players that the initial readiness requirements have been satisfied and the game is beginning.

	**Required information:**
	- Message type

	**Fields:**
	- `type`

	**Example:**
	```json
	{
		"type": "begin_game"
	}
	```

	**Server behavior:**
	- Send this message to both connected players after both have submitted valid secret codes and indicated that they are ready.
	- Do not send this message until both players have satisfied the readiness requirements.
	- Begin the first round after notifying both players.

### `round_start`

	**Direction:** Server → Client

	**Purpose:** Notify both players that a new round is beginning and that they may independently submit their guesses.

	**Required information:**
	- Round number

	**Fields:**
	- `type`
	- `round`

	**Example:**
	```json
	{
		"type": "round_start",
		"round": 1
	}
	```

	**Server behavior:**
	- Send this message to both connected players at the beginning of each round.
	- Include the current round number.
	- Allow both players to submit one guess for the round.
	- Collect both guesses before evaluating either guess.

### `guess`

	**Direction:** Client → Server

	**Purpose:** Submit the player's guess of the opponent's secret code for the current round.

	**Required information:**
	- Round number
	- Player's four-character guess

	**Fields:**
	- `type`
	- `round`
	- `turn`
	- `guess_code`

	**Example:**
	```json
	{
		"type": "guess",
		"round": 1,
		"turn": 1,
		"guess_code": "RGBY"
	}
	```

	**Server behavior:**
	- Associate the guess with the player who submitted it.
	- Verify that the submitted round number matches the current round.
	- Validate that the guess contains exactly four permitted characters.
	- Accept no more than one guess from each player per turn.
	- Store the guess without evaluating it immediately.
	- Wait until both players have submitted their guesses.
	- Once both guesses are received, evaluate each guess against the opponent's secret code.

### `feedback`

	**Direction:** Server → Client

	**Purpose:** Return the server's evaluation of the player's guess against the opponent's secret code.

	**Required information:**
	- Round number
	- Number of correct characters in the correct positions
	- Number of correct characters in incorrect positions

	**Fields:**
	- `type`
	- `round`
	- `turn`
	- `exact_matches`
	- `misplaced_matches`

	**Example:**
	```json
	{
		"type": "feedback",
		"round": 1,
		"turn": 1,
		"exact_matches": 2,
		"misplaced_matches": 1
	}
	```

	**Server behavior:**
	- Send feedback individually to each player after both players have submitted their guesses.
	- Evaluate each player's guess against the opposing player's secret code.
	- Report the number of exact matches and misplaced matches.
	- Do not disclose the opponent's complete secret code.
	- Ensure that feedback corresponds to the correct round.

### `round_outcome`

	**Direction:** Server → Client

	**Purpose:** Communicate the result of the completed round to each player.

	**Required information:**
	- Round number
	- Round result from the receiving player's perspective

	**Fields:**
	- `type`
	- `result`
	- `round`

	**Example (Player 1 wins the round):**
	```json
	{
		"type": "round_outcome",
		"result": "win",
		"round": 1
	}
	```

	**Example (Player 2 loses the round):**
	```json
	{
		"type": "round_outcome",
		"result": "loss",
		"round": 1
	}
	```

	**Example (Round ends in a draw):**
	```json
	{
		"type": "round_outcome",
		"result": "draw",
		"round": 1
	}
	```

	**Server behavior:**
	- Determine the round result after evaluating both players' guesses.
	- If exactly one player solves the opponent's code, declare that player the round winner and award one round point.
	- If both players solve the opponent's code during the same turn, award each player one round point.
	- If neither player solves the opponent's code within ten turns, neither player receives a point.
	- Send an individualized round outcome message to each connected player.
	- Do not begin another round until the current round has been resolved.

### `match_outcome`

	**Direction:** Server → Client

	**Purpose:** Communicate the final result of the three-round match to each player.

	**Required information:**
	- Final match result from the receiving player's perspective
	- Receiving player's accumulated points
	- Opponent's accumulated points

	**Fields:**
	- `type`
	- `result`
	- `player_score`
	- `opponent_score`

	**Example (Player 1 wins the match):**
	```json
	{
		"type": "match_outcome",
		"result": "win",
		"player_score": 2,
		"opponent_score": 1
	}
	```

	**Example (Player 2 loses the match):**
	```json
	{
		"type": "match_outcome",
		"result": "loss",
		"player_score": 1,
		"opponent_score": 2
	}
	```

	**Example (Match ends in a draw):**
	```json
	{
		"type": "match_outcome",
		"result": "draw",
		"player_score": 1,
		"opponent_score": 1
	}
	```

	**Server behavior:**
	- Determine the final match result after all three rounds have been completed.
	- Compare the accumulated points of both players.
	- If one player has more points, declare that player the match winner.
	- If both players have equal points, declare the match a draw.
	- Send an individualized match outcome message to each connected player.
	- Do not begin another round after the match has ended.

### `rematch_intent`

	**Direction:** Client → Server

	**Purpose:** Indicate whether the player wants to participate in another game.

	**Required information:**
	- Player's rematch decision

	**Fields:**
	- `type`
	- `rematch`

	**Example (Player wants another game):**
	```json
	{
		"type": "rematch_intent",
		"rematch": true
	}
	```

	**Example (Player declines another game):**
	```json
	{
		"type": "rematch_intent",
		"rematch": false
	}
	```

	**Server behavior:**
	- Record the rematch decision independently for each player.
	- Wait until both players have submitted their decisions.
	- If both players accept, prepare a new game.
	- If either player declines, terminate the current session gracefully.
	- Do not begin another game until both players have accepted.

### `disconnect`

	**Direction:** Client → Server

	**Purpose:** Notify the server that a client intends to terminate its connection.

	**Required information:**
	- Reason for disconnection

	**Fields:**
	- `type`
	- `reason`

	**Example (Player quits):**
	```json
	{
		"type": "disconnect",
		"reason": "quit"
	}
	```

	**Example (Player exits after declining a rematch):**
	```json
	{
		"type": "disconnect",
		"reason": "session_complete"
	}
	```

	**Server behavior:**
	- Recognize the client's intention to disconnect.
	- Notify the remaining connected player that their opponent has disconnected.
	- Remove the disconnected player from the active game session.
	- Release resources associated with the client's connection.
	- Close the client's TCP connection gracefully.

## 6. Framing Rule

The protocol uses newline-delimited JSON (NDJSON) for message framing.

Each application message consists of one complete JSON object followed by a newline character (`\n`).

The receiver reads incoming bytes until a newline is encountered, then treats the preceding bytes as one complete JSON message and parses the JSON object.

Each message must be sent as a single-line JSON object. JSON objects must not contain unescaped newline characters.

Example:

```text
{"type":"hello"}\n
{"type":"connection_ack"}\n
```

## 7. Connection Termination and Disconnection Handling

The client may intentionally terminate the game/session by sending a `disconnect` message to the server.

Example:

```json
{
    "type": "disconnect",
    "reason": "quit"
}
```

The server should also detect an unexpected client disconnect through TCP EOF or a socket exception.

A graceful termination occurs when the client sends a `disconnect` message before closing the connection.

An abrupt termination occurs when the TCP connection closes without a `disconnect` message, or when a socket error indicates that the connection was lost unexpectedly.

In either case, the receiving endpoint should transition to a disconnected/terminated state and release the associated connection resources.