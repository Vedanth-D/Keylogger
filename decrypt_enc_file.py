# decrypt_enc_file.py
# Usage (interactive): python decrypt_enc_file.py
# Or: python decrypt_enc_file.py <path_to_enc_file> <path_to_key_file>

import sys
from cryptography.fernet import Fernet
from pathlib import Path

def decrypt_file(enc_path: Path, key_path: Path):
    key = key_path.read_bytes()
    f = Fernet(key)
    token = enc_path.read_bytes()
    plaintext = f.decrypt(token)
    return plaintext.decode("utf-8")

def main():
    if len(sys.argv) >= 3:
        enc_path = Path(sys.argv[1])
        key_path = Path(sys.argv[2])
    else:
        enc_path = Path(input("Path to encrypted file (.enc): ").strip())
        key_path = Path(input("Path to key file (fernet.key): ").strip())

    try:
        text = decrypt_file(enc_path, key_path)
        print("\n--- Decrypted content ---\n")
        print(text)
        print("\n--- end ---\n")
    except Exception as e:
        print("Failed to decrypt:", e)

if __name__ == "__main__":
    main()
