# extract_and_decrypt_png.py
# Usage: python extract_and_decrypt_png.py
# Requires: pillow, cryptography

from pathlib import Path
from PIL import Image
from cryptography.fernet import Fernet
import struct

def bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8 != 0:
        bits += '0' * (8 - len(bits) % 8)
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def extract_bytes_from_image(img_path: Path) -> bytes:
    img = Image.open(img_path).convert("RGBA")
    pixels = list(img.getdata())
    bits = []
    for r,g,b,a in pixels:
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))
    bitstr = ''.join(bits)
    # read 32-bit header
    header_bits = bitstr[:32]
    length = int(header_bits, 2)
    total_bits = 32 + length * 8
    if len(bitstr) < total_bits:
        raise ValueError("Image does not contain enough bits for declared length.")
    payload_bits = bitstr[32:32 + length * 8]
    return bits_to_bytes(payload_bits)

def main():
    png_path = Path(input("Path to stego PNG: ").strip())
    key_path = Path(input("Path to fernet.key: ").strip())
    try:
        raw = extract_bytes_from_image(png_path)
        key = key_path.read_bytes()
        f = Fernet(key)
        dec = f.decrypt(raw)
        print("\n--- Decrypted extracted log ---\n")
        print(dec.decode("utf-8"))
        print("\n--- end ---\n")
    except Exception as e:
        print("Failed to extract/decrypt:", e)

if __name__ == "__main__":
    main()
