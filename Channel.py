import numpy as np
import random

# Probability of introducing an error
error_probability = 0.02

# Open the input file
with open("encoded.bin", "rb") as f:
    data = np.frombuffer(f.read(), dtype=np.uint8)

# Convert the data to binary string
input_bits = np.unpackbits(data)

# Introduce random errors with the specified probability
errors = np.random.choice([0, 1], size=input_bits.shape, p=[1 - error_probability, error_probability])

# Apply errors to the input bits
received_bits = np.logical_xor(input_bits, errors).astype(int)


# Convert the received bits back to bytes
received_bytes = np.packbits(received_bits)

# Write the received bytes to the output file
with open("received.bin", "wb") as f:
    f.write(received_bytes)

print("Errors introduced and written to 'received.bin'.")