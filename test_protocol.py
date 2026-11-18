
from protocol import encode_message, MessageBuffer


# Create two application messages.
hello = {"type": "hello"}
identify = {"type": "identify", "player": "P1", "game": "mastermind"}

# Serialize them as if they were being transmitted.
outgoing = encode_message(hello) + encode_message(identify)

# Create a receiver.
receiver = MessageBuffer()

# Simulate TCP splitting the data into two chunks.
first_chunk = outgoing[:12]
second_chunk = outgoing[12:]

# Feed the chunks into the receiver.
print(receiver.receive_data(first_chunk))
print(receiver.receive_data(second_chunk))
