# Keylogger

 A consent-first, educational keylogger-style demo that records only text typed into the app for learning input capture, storage, and hiding techniques.

 Implemented in Python using Tkinter (GUI), cryptography (Fernet) for encryption, and Pillow for PNG steganography.

 App-level recorder — users must click Start Recording and consent; only text typed inside the app’s text box is recorded.

 Entries include ISO timestamps and simple tags (CHAR for printable characters, SPECIAL for non-printable keys) stored in-memory before export.

 Logs are encrypted with Fernet symmetric encryption; a fernet.key file is generated/used to decrypt saved .enc files.

 Encrypted log bytes are embedded into a PNG using an LSB scheme with a 32-bit length header so extraction is reliable and decryptable.

 Project emphasizes explicit consent, secure storage, and defensive testing; deliverables include source code, demo screenshots, encrypted logs, stego images, and an ethics chapter.

<img width="739" height="470" alt="Screenshot 2025-10-24 122857" src="https://github.com/user-attachments/assets/9a27bfc8-4b29-427d-9e90-2ca2887163f9" />
 After starting the keylogger the GUI app will ON.In that we should start recording and type the message and save that. 
<img width="997" height="401" alt="Screenshot 2025-10-24 122945" src="https://github.com/user-attachments/assets/424e2ab8-15a6-41e6-9e68-6e6ed0b6abf4" />
After this we can see the message using the fernet key and showing the path where we saved the file.
<img width="515" height="413" alt="Screenshot 2025-10-24 123009" src="https://github.com/user-attachments/assets/b4effa0a-f4de-40a4-8b86-ab4a4723af3a" />
This is for png files inside we can store the message so that no one knows what is their.
<img width="460" height="374" alt="Screenshot 2025-10-24 123022" src="https://github.com/user-attachments/assets/86d34983-520c-4e5e-9fab-66a453f8e890" />
<img width="196" height="571" alt="Screenshot 2025-10-24 123044" src="https://github.com/user-attachments/assets/fe255a06-f16e-475c-849b-c1efd60dc44c" />
                                                                             THANK YOU !





