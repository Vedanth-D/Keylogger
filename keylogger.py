# consent_recorder_v2.py
"""
Consent-first recorder + stego embed/extract (SAFE educational demo)
- Records ONLY text typed into the app's Text widget after explicit consent.
- Save & Encrypt: encrypts log with Fernet and saves to disk.
- Embed into PNG: embeds encrypted bytes into PNG using LSB per RGB channel with a 32-bit length header.
- Extract from PNG: reads header + payload, attempts to decrypt (requires same key file).
This is intended for educational purposes only.
Dependencies: cryptography, pillow
Install: pip install cryptography pillow
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from cryptography.fernet import Fernet
from PIL import Image
import struct
import os

KEYFILE = "fernet.key"

def generate_key(path=KEYFILE):
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key

def load_key(path=KEYFILE):
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return generate_key(path)

def bytes_to_bits(b: bytes) -> str:
    return ''.join(f"{byte:08b}" for byte in b)

def bits_to_bytes(bits: str) -> bytes:
    # pad to full bytes if needed
    if len(bits) % 8 != 0:
        bits = bits + ('0' * (8 - (len(bits) % 8)))
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def embed_bytes_in_image(img: Image.Image, data: bytes) -> Image.Image:
    """
    Embed length header (32-bit unsigned int, network order) + data bytes into image LSBs.
    Uses R,G,B channels (3 bits per pixel). Keeps alpha untouched.
    """
    header = struct.pack("!I", len(data))  # 4 bytes
    payload = header + data
    bits = bytes_to_bits(payload)
    pixels = list(img.getdata())
    capacity = len(pixels) * 3  # bits available
    if len(bits) > capacity:
        raise ValueError(f"Data too large for image. Need {len(bits)} bits, capacity {capacity} bits.")
    new_pixels = []
    bit_idx = 0
    for px in pixels:
        r,g,b,a = px if len(px) == 4 else (px[0], px[1], px[2], 255)
        if bit_idx < len(bits):
            r = (r & ~1) | int(bits[bit_idx]); bit_idx += 1
        if bit_idx < len(bits):
            g = (g & ~1) | int(bits[bit_idx]); bit_idx += 1
        if bit_idx < len(bits):
            b = (b & ~1) | int(bits[bit_idx]); bit_idx += 1
        new_pixels.append((r,g,b,a))
    # append remaining pixels unchanged
    if bit_idx < len(bits):
        # this should not happen due to capacity check
        raise RuntimeError("Ran out of pixels while embedding.")
    img_out = Image.new("RGBA", img.size)
    img_out.putdata(new_pixels)
    return img_out

def extract_bytes_from_image(img: Image.Image) -> bytes:
    """
    Extract first 32-bit length header, then read that many bytes.
    Returns the extracted raw bytes (header removed).
    """
    pixels = list(img.convert("RGBA").getdata())
    bits = []
    for r,g,b,a in pixels:
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))
    bitstr = ''.join(bits)
    # first 32 bits = length
    if len(bitstr) < 32:
        raise ValueError("Image does not contain a valid header (too small).")
    header_bits = bitstr[:32]
    length = int(header_bits, 2)
    total_bits_needed = 32 + length * 8
    if len(bitstr) < total_bits_needed:
        # maybe trailing zeros were trimmed; handle gracefully
        raise ValueError(f"Image does not contain enough bits for declared length ({length} bytes).")
    payload_bits = bitstr[32:32 + length * 8]
    return bits_to_bytes(payload_bits)

class ConsentRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consent Recorder (Educational Demo v2)")
        self.recording = False
        self.log = []
        self.key_path = KEYFILE
        self.key = load_key(self.key_path)
        self.cipher = Fernet(self.key)
        self._build_ui()

    def _build_ui(self):
        frm = tk.Frame(self.root, padx=10, pady=10)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Type ONLY in the box below. This app records text you consent to provide.",
                 wraplength=480).pack(anchor="w", pady=(0,6))

        self.text = tk.Text(frm, height=12, width=72)
        self.text.pack()

        btn_frame = tk.Frame(frm)
        btn_frame.pack(pady=8, fill="x")

        self.start_btn = tk.Button(btn_frame, text="Start Recording", command=self.start_record)
        self.start_btn.pack(side="left", padx=4)

        self.stop_btn = tk.Button(btn_frame, text="Stop Recording", command=self.stop_record, state="disabled")
        self.stop_btn.pack(side="left", padx=4)

        tk.Button(btn_frame, text="Save & Encrypt Log", command=self.save_encrypted).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Embed Encrypted Log into PNG", command=self.embed_stego).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Extract & Decrypt from PNG", command=self.extract_from_png).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Show Key Path", command=self.show_key_info).pack(side="left", padx=4)

    def start_record(self):
        if messagebox.askyesno("Consent", "Do you consent to record what you type into this box?"):
            self.recording = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.text.bind("<Key>", self._on_key)
            self.log.append(f"--- Recording started at {datetime.now().isoformat()} ---")
            messagebox.showinfo("Recording", "Recording started (app-only). Type into the box.")
        else:
            messagebox.showinfo("Consent", "Recording cancelled.")

    def stop_record(self):
        if self.recording:
            self.recording = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.text.unbind("<Key>")
            self.log.append(f"--- Recording stopped at {datetime.now().isoformat()} ---")
            messagebox.showinfo("Stopped", "Recording stopped.")
        else:
            messagebox.showinfo("Not recording", "Recorder was not running.")

    def _on_key(self, event):
        # Only triggered when typing inside our Text widget
        if not self.recording:
            return
        ts = datetime.now().isoformat()
        char = event.char
        if char and char.isprintable():
            entry = f"{ts} CHAR {char}"
        else:
            entry = f"{ts} SPECIAL {event.keysym}"
        self.log.append(entry)

    def save_encrypted(self):
        if not self.log:
            messagebox.showwarning("No Data", "No recorded entries to save.")
            return
        data = "\n".join(self.log).encode("utf-8")
        token = self.cipher.encrypt(data)
        path = filedialog.asksaveasfilename(defaultextension=".log.enc",
                                            filetypes=[("Encrypted log","*.enc;*.log.enc")],
                                            title="Save encrypted log as")
        if path:
            with open(path, "wb") as f:
                f.write(token)
            messagebox.showinfo("Saved", f"Encrypted log saved to {path}")

    def embed_stego(self):
        if not self.log:
            messagebox.showwarning("No Data", "No recorded entries to embed.")
            return
        img_path = filedialog.askopenfilename(title="Select PNG image to embed into",
                                              filetypes=[("PNG images","*.png")])
        if not img_path:
            return
        out_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")],
                                                title="Save stego image as")
        if not out_path:
            return
        try:
            img = Image.open(img_path)
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            data = "\n".join(self.log).encode("utf-8")
            enc = self.cipher.encrypt(data)
            img_out = embed_bytes_in_image(img, enc)
            img_out.save(out_path, "PNG")
            messagebox.showinfo("Saved", f"Stego image saved to {out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to embed data: {e}")

    def extract_from_png(self):
        png_path = filedialog.askopenfilename(title="Select stego PNG to extract from",
                                              filetypes=[("PNG images","*.png")])
        if not png_path:
            return
        try:
            img = Image.open(png_path)
            raw = extract_bytes_from_image(img)
            # attempt to decrypt using loaded key
            try:
                dec = self.cipher.decrypt(raw)
                # show in a small viewer (not stored unless user saves)
                top = tk.Toplevel(self.root)
                top.title("Extracted & Decrypted Log (read-only)")
                txt = tk.Text(top, height=20, width=80)
                txt.pack()
                txt.insert("1.0", dec.decode("utf-8"))
                txt.config(state="disabled")
            except Exception as e:
                # decryption failed
                messagebox.showerror("Decrypt failed", f"Could not decrypt extracted bytes with loaded key: {e}\n"
                                                       "Ensure you're using the same key file that was used to encrypt.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract data: {e}")

    def show_key_info(self):
        abs_path = os.path.abspath(self.key_path)
        messagebox.showinfo("Key info", f"Fernet key file path: {abs_path}\n"
                                        f"If you move the key file, re-run the app to generate/load a new one.\n"
                                        f"Keep this key secret to decrypt logs.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsentRecorderApp(root)
    root.mainloop()
