# State and Score Broadcast Sequence Diagram

This diagram illustrates the intended message flow for client connections, move validation, turn changes, and score updates. Message names are provisional and must be aligned with the project's actual protocol.

```mermaid
sequenceDiagram
    autonumber
    actor C1 as Client 1 (Player X)
    participant S as Game Server
    actor C2 as Client 2 (Player O)

    C1->>S: CONNECT
    S-->>C1: WAITING_FOR_OPPONENT

    C2->>S: CONNECT
    S-->>C1: GAME_START (Board, Active Turn)
    S-->>C2: GAME_START (Board, Active Turn)

    C1->>S: MOVE (Position)
    Note over S: Validate player, turn, and position

    alt Valid Move
        Note over S: Lock state, apply move, switch turn, unlock
        S-->>C1: STATE_UPDATE (Board, Active Turn)
        S-->>C2: STATE_UPDATE (Board, Active Turn)

        alt Round Completed
            Note over S: Calculate and store round result
            S-->>C1: SCORE_UPDATE (Scores)
            S-->>C2: SCORE_UPDATE (Scores)
            S-->>C1: ROUND_END (Result)
            S-->>C2: ROUND_END (Result)
        end
    else Invalid Move or Out of Turn
        S-->>C1: ERROR (Reason)
    end

    C2->>S: MOVE (Position)
    Note over S: Apply the same validation rules

    alt Valid Move
        Note over S: Update authoritative game state
        S-->>C1: STATE_UPDATE (Board, Active Turn)
        S-->>C2: STATE_UPDATE (Board, Active Turn)
    else Invalid Move or Out of Turn
        S-->>C2: ERROR (Reason)
    end
```

## Protocol Alignment Checklist

- [ ] Replace provisional message names with the actual protocol names.
- [ ] Include every message type used by the game.
- [ ] Confirm how clients are assigned player identities.
- [ ] Confirm how the server handles a waiting player and a newly joined opponent.
- [ ] Include the actual round-completion and game-over behavior.
- [ ] Include the defined disconnection behavior.
- [ ] Verify that score updates reach both clients after score changes.
