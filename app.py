# app.py (MAIN APPLICATION)
# Fast YOLO + Encryption + Dashboard + Auto Evidence
# Windows-safe version (NO c10.dll crash)

import os

# 🔥 CRITICAL FIX (must be FIRST)
os.environ["QT_OPENGL"] = "software"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

import sys, cv2, time
from datetime import datetime

import torch                     # load torch FIRST
from ultralytics import YOLO     # then YOLO

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

from cryptography.fernet import Fernet
from fpdf import FPDF
from playsound import playsound
# ---------------- CONFIG ----------------
MODEL = "yolov8n.pt"     # fast & stable
CONF = 0.35
SAVE_GAP = 6
KEY_FILE = "secret.key"
SOUND_PATH = "alert.mp3"

os.makedirs("evidence/encrypted", exist_ok=True)
os.makedirs("evidence/decrypted", exist_ok=True)

# ---------------- ENCRYPTION ----------------
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())

fernet = Fernet(open(KEY_FILE, "rb").read())

# ---------------- YOLO MODEL ----------------
model = YOLO(MODEL)

# ---------------- APP ----------------
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Mobile Detection")
        self.setGeometry(100, 100, 1000, 700)

        self.cam = QLabel()
        self.cam.setFixedSize(800, 500)

        self.btn = QPushButton("START DETECTION")
        self.btn.clicked.connect(self.start)

        self.web = QWebEngineView()
        dash = os.path.abspath("dashboard.html")
        if os.path.exists(dash):
            self.web.load(QUrl.fromLocalFile(dash))

        layout = QVBoxLayout()
        layout.addWidget(self.cam)
        layout.addWidget(self.btn)
        layout.addWidget(self.web)
        self.setLayout(layout)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.last_saved = 0
        self.saved_images = []

    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        detected = False
        results = model.predict(frame, conf=CONF, verbose=False)[0]

        for box in results.boxes:
            name = model.names[int(box.cls[0])].lower()
            if "phone" in name:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
                detected = True

        if detected and time.time() - self.last_saved > SAVE_GAP:
            count = len(os.listdir("evidence/decrypted"))
            raw = f"evidence/decrypted/{count}.jpg"
            enc = f"evidence/encrypted/{count}.enc"

            cv2.imwrite(raw, frame)
            with open(enc, "wb") as f:
                f.write(fernet.encrypt(open(raw, "rb").read()))

            self.saved_images.append(raw)
            with open("evidence_list.txt", "w") as f:
                f.write("\n".join(self.saved_images))

            self.last_saved = time.time()

            try:
                playsound(SOUND_PATH)
            except:
                pass

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = rgb.shape
        self.cam.setPixmap(QPixmap.fromImage(
            QImage(rgb.data, w, h, c*w, QImage.Format_RGB888)
        ))

    def closeEvent(self, e):
        if self.saved_images:
            pdf = FPDF()
            for img in self.saved_images:
                pdf.add_page()
                pdf.image(img, 10, 10, 180)
            pdf.output("evidence_report.pdf")

        if self.cap:
            self.cap.release()
        e.accept()

# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = App()
    win.show()
    sys.exit(app.exec_())
