
import json


class ProtocolError(Exception):
    """Raised when a protocol message is invalid."""


def encode_message(message):
    """Convert a message dictionary into newline-terminated JSON bytes."""

    if not isinstance(message, dict):
        raise ProtocolError("Message must be a dictionary.")

    if not isinstance(message.get("type"), str):
        raise ProtocolError("Message must contain a string 'type' field.")

    try:
        json_text = json.dumps(message)
        return (json_text + "\n").encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ProtocolError("Message could not be serialized.") from error


def decode_message(data):
    """Convert one complete JSON message from bytes into a dictionary."""

    try:
        message = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtocolError("Received invalid JSON message.") from error

    if not isinstance(message, dict):
        raise ProtocolError("Received message must be a JSON object.")

    if not isinstance(message.get("type"), str):
        raise ProtocolError("Received message has no valid 'type' field.")

    return message


class MessageBuffer:
    """Accumulate TCP data and extract complete NDJSON messages."""

    def __init__(self):
        self.buffer = bytearray()

    def receive_data(self, data):
        """Add received bytes and return all complete messages."""

        self.buffer.extend(data)
        messages = []

        while b"\n" in self.buffer:
            line, _, remainder = self.buffer.partition(b"\n")
            self.buffer = bytearray(remainder)

            if not line:
                continue

            messages.append(decode_message(line))

        return messages
