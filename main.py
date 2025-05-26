from PIL import Image
import numpy as np
from bitarray import bitarray
import subprocess

# -------------------------------
# Hamming(12,8) Error Correction
# -------------------------------

def calculate_parity_bits(data_bits):
    """
    Calculates parity bits for 8 data bits using Hamming(12,8).
    Parity positions: 1, 2, 4, 8 (1-based indexing).
    """
    code = [0] * 13  # index 0 is unused to keep positions 1-based
    data_positions = [3, 5, 6, 7, 9, 10, 11, 12]

    # Place data bits in correct positions
    for i, pos in enumerate(data_positions):
        code[pos] = data_bits[i]

    # Even parity calculations
    code[1] = code[3] ^ code[5] ^ code[7] ^ code[9] ^ code[11]
    code[2] = code[3] ^ code[6] ^ code[7] ^ code[10] ^ code[11]
    code[4] = code[5] ^ code[6] ^ code[7] ^ code[12]
    code[8] = code[9] ^ code[10] ^ code[11] ^ code[12]

    return code[1:]  # drop the dummy index 0

def hamming_encode_byte(byte):
    """
    Takes a single byte and encodes it into 12 bits using Hamming(12,8).
    """
    bits = [(byte >> i) & 1 for i in reversed(range(8))]  # MSB to LSB
    return calculate_parity_bits(bits)

def hamming_decode_block(block):
    """
    Decodes and corrects a 12-bit Hamming block.
    Returns the original 8-bit data.
    """
    code = [0] + block  # padding index 0 for 1-based indexing

    # Syndrome bits help locate any single-bit error
    s1 = code[1] ^ code[3] ^ code[5] ^ code[7] ^ code[9] ^ code[11]
    s2 = code[2] ^ code[3] ^ code[6] ^ code[7] ^ code[10] ^ code[11]
    s4 = code[4] ^ code[5] ^ code[6] ^ code[7] ^ code[12]
    s8 = code[8] ^ code[9] ^ code[10] ^ code[11] ^ code[12]

    error_pos = s1 + (s2 << 1) + (s4 << 2) + (s8 << 3)

    if 1 <= error_pos <= 12:
        code[error_pos] ^= 1  # flip the error bit

    data_positions = [3, 5, 6, 7, 9, 10, 11, 12]
    data_bits = [code[pos] for pos in data_positions]

    # Convert data bits to a single byte
    byte = 0
    for bit in data_bits:
        byte = (byte << 1) | bit

    return byte

# -------------------------------
# Image Preprocessing
# -------------------------------

def preprocess_image(image_path):
    """
    Loads the image, converts to grayscale, resizes it,
    and flattens it to a 1D array of pixels.
    """
    img = Image.open(image_path).convert('L')
    img = img.resize((1000, 500))  # Keeping it small but readable
    flat = np.array(img, dtype=np.uint8).flatten()
    return flat, (500, 1000)

# -------------------------------
# Hamming Encode/Decode
# -------------------------------

def hamming_encode_all(pixels):
    """
    Encodes all pixel bytes using Hamming(12,8).
    Returns a bitarray of encoded bits.
    """
    bits = bitarray()
    for byte in pixels:
        bits.extend(hamming_encode_byte(byte))
    return bits

def hamming_decode_all(encoded_bits):
    """
    Decodes a bitarray of 12-bit Hamming blocks into original bytes.
    """
    decoded = []
    for i in range(0, len(encoded_bits), 12):
        block = encoded_bits[i:i+12]
        if len(block) < 12:
            break
        decoded.append(hamming_decode_block(list(block)))
    return np.array(decoded, dtype=np.uint8)

# -------------------------------
# XOR Logic
# -------------------------------

def xor_with_curse(decoded_bytes, curse_path):
    """
    Performs byte-wise XOR with Geto's cursed file.
    This reveals the hidden image.
    """
    curse_bytes = np.frombuffer(open(curse_path, 'rb').read(), dtype=np.uint8)

    if len(decoded_bytes) != len(curse_bytes):
        raise ValueError("Mismatch between image and curse file sizes.")

    return np.bitwise_xor(decoded_bytes, curse_bytes)

# -------------------------------
# Image Output
# -------------------------------

def save_image(data, shape, out_path):
    """
    Saves a 1D byte array back to a grayscale image.
    """
    img = Image.fromarray(data.reshape(shape), mode='L')
    img.save(out_path)

# -------------------------------
# Main Logic
# -------------------------------

def main():
    print("🔹 Step 1: Preprocessing image...")
    pixels, shape = preprocess_image('Input_image.png')
    print(f"    Image resized and flattened. Total pixels: {len(pixels)}")

    print("🔹 Step 2: Encoding using Hamming(12,8)...")
    encoded_bits = hamming_encode_all(pixels)
    print(f"    Encoding done. Total bits: {len(encoded_bits)}")

    print("🔹 Step 3: Saving encoded bits to 'encoded.bin'...")
    with open('encoded.bin', 'wb') as f:
        encoded_bits.tofile(f)

    print("🔹 Step 4: Simulating corruption via 'Channel.py'...")
    subprocess.run(['python', 'Channel.py'], check=True)
    print("    Corrupted data saved to 'received.bin'")

    print("🔹 Step 5: Decoding and correcting errors...")
    with open('received.bin', 'rb') as f:
        received_bits = bitarray()
        received_bits.fromfile(f)

    decoded_bytes = hamming_decode_all(received_bits)
    print(f"    Decoded {len(decoded_bytes)} bytes successfully")


    print("🔹 Step 5.5: Saving recovered image before XOR (should match original)...")
    save_image(decoded_bytes, shape, 'recovered.png')
    print("    Recovered image saved as 'recovered.png'")

  

    print("🔹 Step 6: XORing with cursed array...")
    revealed = xor_with_curse(decoded_bytes, 'Array_to_be_Xored.bin')

    print("🔹 Step 7: Saving final revealed image as 'revealed.png'...")
    save_image(revealed, shape, 'revealed.png')
    print(" Done! Gojo’s hidden message has been revealed. YAYYYYYYY")

if __name__ == '__main__':
    main()