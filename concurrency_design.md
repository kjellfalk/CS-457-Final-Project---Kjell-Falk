# Server Concurrency Architecture Design

## 1. Overview

This document describes the server concurrency model, shared-state synchronization strategy, turn-validation rules, and score-broadcasting mechanism for the CS 457 final project.

The server must support two simultaneous client connections while maintaining a consistent game state. The server is authoritative: clients submit requests, but the server validates those requests and determines the resulting state.

## 2. Concurrency Model Selection

### 2.1 Chosen Model: Multi-Threading

The server will use Python's `socketserver.ThreadingTCPServer` (or an equivalent threaded TCP server implementation) to handle multiple client connections.

Each connected client is handled by a dedicated worker thread. This allows the server to process one client's connection without requiring the main server loop to wait for another client to finish sending data.

The server maintains shared game state, including:

- The game board.
- The identity of the active player.
- The connected clients and their player assignments.
- The current round status and scores.

**Implementation note:** Confirm the actual server class used by the project before finalizing this section.

### 2.2 Thread Safety and Locking Strategy

Because multiple worker threads may access shared game state, the server must prevent race conditions.

A race condition occurs when the result of an operation depends on the unpredictable timing of concurrent operations.

The server will use a `threading.Lock` to protect critical sections that read and modify shared game state.

A critical section is a portion of code that accesses shared state and must not execute concurrently with another conflicting operation.

The server will acquire the lock when it:

1. Validates the active player and proposed move.
2. Checks whether the target board position is available.
3. Applies a valid move and changes the active player.
4. Updates round results and scores.

The lock will be released after the relevant state transition is complete. Network operations, including sending messages to clients, should generally occur outside the lock to avoid holding it during potentially blocking I/O.

### 2.3 Client Connection Handling

Each client connection is handled independently by a worker thread. The server must support both clients being connected at the same time.

The server will handle connection termination by removing or marking the disconnected client and updating the game state according to the project's disconnection policy.

**Project-specific decision:** Document what happens when a player disconnects during a round.

## 3. Game-State and Turn Synchronization

### 3.1 Authoritative Game State

The server is the authoritative source of game state. Clients send requests, but clients do not independently determine whether a move is valid.

For each move request, the server will:

1. Identify the requesting client and its assigned player.
2. Check whether the game is accepting moves.
3. Verify that the requesting player owns the active turn.
4. Verify that the requested move satisfies the game's board rules.
5. Apply the move and update the active turn under the state lock.
6. Determine whether the move ends the round or game.
7. Notify the relevant clients of the resulting state.

### 3.2 Invalid-Move Handling

The server rejects moves that are out of turn, target an unavailable position, or otherwise violate the game's rules.

A rejected move must not modify the board, active player, or score. The server returns an error message to the requesting client.

### 3.3 State Broadcasting

After accepting a move, the server sends the resulting game state to both clients. The update should include the information necessary for both clients to display a consistent board and identify the active player.

The server must also communicate relevant state transitions, such as a player joining, a round ending, or the game ending.

**Protocol decision:** Confirm the exact message names and fields against the project's client-server protocol before finalizing the design.

## 4. Score and Leaderboard Synchronization

### 4.1 Score Storage

Scores are maintained on the server so that clients cannot independently determine or overwrite authoritative results.

The server updates the score when a round reaches its defined completion condition. The exact scoring rules depend on the game's design.

**Project-specific decision:** Document the scoring rules, when scores are updated, and whether scores persist across multiple rounds or sessions.

### 4.2 Score Broadcasting

After updating a score, the server constructs a score update containing the relevant results and broadcasts it to both connected clients.

Both clients should receive the same authoritative score data. If a client disconnects or a send fails, the server should handle the failure according to the project's connection and recovery policy.

## 5. Error Handling and Disconnection

The server should handle malformed requests, invalid moves, and disconnected clients without corrupting shared game state.

Worker threads must release acquired locks even when an exception occurs. Python's `with lock:` construct is recommended because it releases the lock when execution leaves the protected block.

The server should also define how it handles a client that disconnects while a round is in progress.

## 6. Design Decisions to Confirm

- [ ] Confirm the server's actual concurrency implementation.
- [ ] Confirm the game's board rules and valid-move conditions.
- [ ] Confirm the client-server message names and message fields.
- [ ] Define the scoring and round-completion rules.
- [ ] Define the client-disconnection policy.
- [ ] Verify that both clients receive authoritative state and score updates.

## 7. Related Documentation

See [`sequence_diagram.md`](sequence_diagram.md) for the client-server message flow and turn-synchronization sequence.
