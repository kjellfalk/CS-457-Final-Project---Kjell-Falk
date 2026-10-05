# CS 457 Sprint 1: Application Protocol Blueprint

## 1. Protocol Overview

This protocol defines the application-layer communication between a client and server for my code-guessing game.

The protocol uses structured JSON messages exchanged over a TCP connection. Each message identifies its semantic type and carries any additional information required for that message.

The protocol covers establishment of connection, player identification, game readiness, gameplay, game completion, and connection termination.

## 2. Transport and Serialization

### Transport

The protocol uses TCP for client-server communication.

TCP provides a reliable byte stream between the client and server, but does not preserve application-level message boundaries.

### Serialization

Protocol messages are serialized as UTF-8 encoded JSON objects.

Each JSON object represents one application-level message and contains a 'type' field identifying the semantic message type.

## 3. Message Types

| Message Type | Direction | Purpose |
|---|---|---|
| `hello` | Client → Server | Initiate application-level communication |
| `connection_ack` | Server → Client | Acknowledge the client's connection |
| `identify` | Client → Server | Identify the player and selected game |
| `client_ready` | Client → Server | Indicate that the client/player is ready |
| `begin_game` | Server → Client | Indicate that the game is beginning |
| `turn` | Server → Client | Indicate that the client has the turn |
| `guess` | Client → Server | Submit a guess |
| `key` | Server → Client | Return the server's evaluation of the guess |
| `outcome` | Server → Client | Communicate the game outcome |
| `intent` | Client → Server | Indicate whether the client wants to play again or terminate |
| `disconnect` | Client → Server | Indicate intentional termination |

## 4. Message Schemas

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
	
### `client_ready`

	**Direction:** Client → Server

	**Purpose:** Indicate that the client/player is ready

	**Required information:**
	- Client readiness

	**Fields:**
	- `type`
	- `readiness`

	**Example:**
	```json
	{
		"type": "client_ready",
		"readiness": true
	}
	```
	
### `begin_game`

	**Direction:** Server → Client

	**Purpose:** Indicate that the game is beginning

	**Required information:**
	- Game-start indication
	- Correct "code" pattern

	**Fields:**
	- `type`
	- `correct_code`

	**Example:**
	```json
	{
		"type": "begin_game",
		"correct_code": "..."
	}
	```
	
### `turn`

	**Direction:** Server → Client

	**Purpose:** Indicate that the client has the turn

	**Required information:**
	- Turn

	**Fields:**
	- `type`

	**Example:**
	```json
	{
		"type": "turn"
	}
	```
	
### `guess`

	**Direction:** Client → Server

	**Purpose:** Submit a guess

	**Required information:**
	- Client's guess

	**Fields:**
	- `type`
	- `guess_code`

	**Example:**
	```json
	{
		"type": "guess",
		"guess_code": "..."
	}
	```
	
### `key`

	**Direction:** Server → Client

	**Purpose:** Return the server's evaluation of the guess

	**Required information:**
	- The results of the evaluation of the client's guess

	**Fields:**
	- `type`
	- `key_code`

	**Example:**
	```json
	{
		"type": "key",
		"key_code": "..."
	}
	```
	
### `outcome`

	**Direction:** Server → Client

	**Purpose:** Communicate the game outcome

	**Required information:**
	- The outcome of the game

	**Fields:**
	- `type`
	- `outcome`

	**Example:**
	```json
	{
		"type": "outcome",
		"outcome": "win"
	}
	```
	
### `intent`

	**Direction:** Client → Server

	**Purpose:** Indicate whether the client wants to play again or terminate

	**Required information:**
	- Client intent

	**Fields:**
	- `type`
	- `intent`

	**Example:**
	```json
	{
		"type": "intent",
		"intent": "play again"
	}
	```
	
### `disconnect`

	**Direction:** Client → Server

	**Purpose:** Indicate intentional termination

	**Required information:**
	- That the client intends to terminate the game/session

	**Fields:**
	- `type`
	- `reason`

	**Example:**
	```json
	{
		"type": "disconnect",
		"reason": "quit"
	}
	```

## 5. Framing Rule

The protocol uses newline-delimited JSON (NDJSON) for message framing.

Each application message consists of one complete JSON object followed by a newline character (`\n`).

The receiver reads incoming bytes until a newline is encountered, then treats the preceding bytes as one complete JSON message and parses the JSON object.

Each message must be sent as a single-line JSON object. JSON objects must not contain unescaped newline characters.

Example:

```text
{"type":"hello"}\n
{"type":"connection_ack"}\n
```

## 6. Connection Termination and Disconnection Handling

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