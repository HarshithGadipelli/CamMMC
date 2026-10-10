
# decrypt_all.py
# Decrypt ALL evidence at once using password key

from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"
fernet = Fernet(open(KEY_FILE,"rb").read())

enc_dir = "evidence/encrypted"
out_dir = "evidence/decrypted"

os.makedirs(out_dir, exist_ok=True)

for f in os.listdir(enc_dir):
    if f.endswith(".enc"):
        data = open(enc_dir+"/"+f,"rb").read()
        dec = fernet.decrypt(data)
        open(out_dir+"/"+f.replace(".enc",".jpg"),"wb").write(dec)

print("All evidence decrypted successfully")
