"""
============================================================
  Smart Face Recognition Attendance System
  Muhammad Sami (F23BDOCS1E02139)
  Abdul Samad  (F23BDOCS1E02198)
  Submitted To: Sir Abdullah Soomro
============================================================
"""

import cv2
import os
import csv
import time
import pickle
import numpy as np
from datetime import datetime, date
import face_recognition

KNOWN_FACES_DIR   = "known_faces"
ATTENDANCE_DIR    = "attendance_records"
ENCODINGS_FILE    = "models/encodings.pkl"
TOLERANCE         = 0.50
FRAME_SCALE       = 0.5
MARK_COOLDOWN_SEC = 30


def ensure_dirs():
    for d in [KNOWN_FACES_DIR, ATTENDANCE_DIR, "models"]:
        os.makedirs(d, exist_ok=True)


def get_today_csv():
    filename = date.today().strftime("%Y-%m-%d") + "_attendance.csv"
    return os.path.join(ATTENDANCE_DIR, filename)


def load_attendance(csv_path):
    marked = {}
    if os.path.exists(csv_path):
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                marked[row["Name"]] = row["Time"]
    return marked


def write_attendance(csv_path, name, timestamp):
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Roll No", "Name", "Date", "Time", "Status"])
        if not file_exists:
            writer.writeheader()
        parts = name.split("_", 1)
        student_name = parts[0]
        roll_no = parts[1] if len(parts) > 1 else "N/A"
        writer.writerow({
            "Roll No": roll_no,
            "Name"   : student_name,
            "Date"   : date.today().strftime("%Y-%m-%d"),
            "Time"   : timestamp,
            "Status" : "Present"
        })


def load_image_rgb(img_path):
    """Load any image and safely convert to uint8 RGB."""
    try:
        from PIL import Image
        img = Image.open(img_path).convert('RGB')
        return np.ascontiguousarray(np.array(img, dtype=np.uint8))
    except Exception:
        return None


def encode_known_faces(force_retrain=False):
    if os.path.exists(ENCODINGS_FILE) and not force_retrain:
        print("[INFO] Loading existing encodings...")
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)

    print("[INFO] Training face encodings — please wait...")
    known_encodings = []
    known_names     = []

    for student_folder in os.listdir(KNOWN_FACES_DIR):
        folder_path = os.path.join(KNOWN_FACES_DIR, student_folder)
        if not os.path.isdir(folder_path):
            continue

        image_count = 0
        for img_file in os.listdir(folder_path):
            if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            img_path = os.path.join(folder_path, img_file)
            image = load_image_rgb(img_path)
            if image is None:
                print(f"  [SKIP] Could not read: {img_file}")
                continue

            try:
                encs = face_recognition.face_encodings(image)
                if encs:
                    known_encodings.append(encs[0])
                    known_names.append(student_folder)
                    image_count += 1
            except Exception as e:
                print(f"  [SKIP] Error: {img_file}: {e}")
                continue

        print(f"  OK  {student_folder}: {image_count} image(s) encoded")

    data = {"encodings": known_encodings, "names": known_names}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)

    print(f"[INFO] Done — {len(known_names)} face(s) stored.\n")
    return data


def run_attendance(data):
    known_encodings = data["encodings"]
    known_names     = data["names"]

    if not known_encodings:
        print("[ERROR] No encodings found. Register students first.")
        return

    csv_path     = get_today_csv()
    marked_today = load_attendance(csv_path)
    last_marked  = {}

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot access webcam.")
        return

    print("\n[SYSTEM] Running — press Q to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        for enc, loc in zip(encodings, locations):
            matches   = face_recognition.compare_faces(known_encodings, enc, TOLERANCE)
            distances = face_recognition.face_distance(known_encodings, enc)
            name  = "Unknown"
            color = (0, 0, 220)

            if True in matches:
                best_idx = int(np.argmin(distances))
                if matches[best_idx]:
                    name  = known_names[best_idx]
                    color = (0, 200, 50)

            scale = int(1 / FRAME_SCALE)
            top, right, bottom, left = [v * scale for v in loc]

            ts      = datetime.now().strftime("%H:%M:%S")
            display = name.split("_")[0]

            if name != "Unknown":
                elapsed = time.time() - last_marked.get(name, 0)
                if name not in marked_today and elapsed > MARK_COOLDOWN_SEC:
                    write_attendance(csv_path, name, ts)
                    marked_today[name] = ts
                    last_marked[name]  = time.time()
                    print(f"  Marked: {display}  @ {ts}")

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            label_y = bottom + 35 if bottom + 35 < frame.shape[0] else top - 10
            cv2.rectangle(frame, (left, bottom), (right, label_y), color, cv2.FILLED)
            cv2.putText(frame, display, (left + 6, bottom + 24),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)

            if name in marked_today:
                cv2.putText(frame, "PRESENT", (left + 6, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 100), 2)

        info = f"Smart Attendance  |  {date.today()}  |  Present: {len(marked_today)}"
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 36), (30, 30, 30), cv2.FILLED)
        cv2.putText(frame, info, (10, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (200, 230, 255), 1)

        cv2.imshow("Smart Face Recognition Attendance System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[DONE] Saved to: {csv_path}")
    print(f"       Total present: {len(marked_today)}\n")


if __name__ == "__main__":
    ensure_dirs()
    print("=" * 60)
    print("   Smart Face Recognition Attendance System")
    print("   Muhammad Sami | Abdul Samad | 6th Semester")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Train / Retrain face encodings")
    print("  2. Start attendance (use existing encodings)")
    print("  3. Train then start attendance")
    print("  4. Exit")
    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        encode_known_faces(force_retrain=True)
    elif choice == "2":
        data = encode_known_faces(force_retrain=False)
        run_attendance(data)
    elif choice == "3":
        data = encode_known_faces(force_retrain=True)
        run_attendance(data)
    else:
        print("Goodbye!")