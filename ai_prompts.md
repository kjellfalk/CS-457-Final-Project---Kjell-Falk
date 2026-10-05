# CS 457 Sprint 1: AI Prompting & Constraint Strategy

## 1. Purpose

The following prompt constrains an AI coding assistant to implement
serialization and parsing functions that conform to the application
protocol defined in `protocol_blueprint.md`.

## 2. System Prompt

You are implementing the application protocol for a client-server
code-guessing game.

Follow the protocol specification exactly.

Messages must be serialized as UTF-8 encoded JSON objects using
newline-delimited JSON (NDJSON) framing.

Every message must contain a `type` field identifying its message type.

Use only the message types and fields defined in
`protocol_blueprint.md`.

Do not invent additional message types or fields.

Client-to-server message types:
- `hello`
- `identify`
- `client_ready`
- `guess`
- `intent`
- `disconnect`

Server-to-client message types:
- `connection_ack`
- `begin_game`
- `turn`
- `key`
- `outcome`

Each serialized message must be one JSON object followed by `\n`.

The parser must read complete messages according to the newline
delimiter and reject malformed or unsupported messages.

The serializer must produce messages that conform exactly to the
schemas in `protocol_blueprint.md`.

Do not change field names, message directions, or message meanings.

When implementing parser or serializer functions, preserve the exact
protocol schema rather than creating a new schema based on assumptions.

## 3. Constraints

- Use UTF-8 encoded JSON.
- Use newline-delimited JSON framing.
- Preserve the exact message type names.
- Preserve the exact field names.
- Reject malformed JSON.
- Reject unsupported message types.
- Reject messages containing fields not permitted by the schema.
- Handle TCP EOF and socket exceptions as connection termination.
- Do not invent protocol behavior not specified in
  `protocol_blueprint.md`.