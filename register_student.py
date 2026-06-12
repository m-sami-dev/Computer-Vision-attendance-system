"""
============================================================
  Student Face Registration Tool
  Capture webcam images for each new student.
  Run this ONCE per student before running the main system.
============================================================
"""

import cv2
import os

KNOWN_FACES_DIR = "known_faces"
IMAGES_PER_STUDENT = 30      # Number of snapshots to capture


def register_student():
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

    print("=" * 55)
    print("  Student Face Registration")
    print("=" * 55)
    student_name = input("\nEnter Student Full Name : ").strip().replace(" ", "_")
    roll_no      = input("Enter Roll Number       : ").strip().replace(" ", "_")

    # Folder format: FirstName_LastName_RollNo
    folder_name = f"{student_name}_{roll_no}"
    save_path   = os.path.join(KNOWN_FACES_DIR, folder_name)
    os.makedirs(save_path, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot access webcam.")
        return

    print(f"\n[INFO] Capturing {IMAGES_PER_STUDENT} images for {student_name}.")
    print("[INFO] Look at the camera. Press  S  to save, or wait for auto-capture.")
    print("[INFO] Press  Q  to finish early.\n")

    count    = 0
    auto_cap = 0   # frames since last auto-capture

    while count < IMAGES_PER_STUDENT:
        ret, frame = cap.read()
        if not ret:
            break

        auto_cap += 1
        display = frame.copy()

        # ── Status bar ───────────────────────────────────
        cv2.rectangle(display, (0, 0), (display.shape[1], 40), (20, 20, 20), cv2.FILLED)
        cv2.putText(display,
                    f"Student: {student_name}  |  Captured: {count}/{IMAGES_PER_STUDENT}",
                    (10, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 220, 255), 1)

        # ── Auto-capture every 15 frames ─────────────────
        if auto_cap >= 15:
            filename = os.path.join(save_path, f"{folder_name}_{count:03d}.jpg")
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            count   += 1
            auto_cap = 0
            print(f"  📷  Saved image {count}/{IMAGES_PER_STUDENT}")

        cv2.imshow("Student Registration", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):           # Manual save
            filename = os.path.join(save_path, f"{folder_name}_{count:03d}.jpg")
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            count += 1
            print(f"  📷  Manually saved image {count}/{IMAGES_PER_STUDENT}")
        elif key == ord("q"):
            print("[INFO] Registration stopped early.")
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n[DONE] {count} images saved for {student_name} in '{save_path}'")
    print("[NEXT] Run attendance_system.py and choose option 1 to retrain encodings.\n")


if __name__ == "__main__":
    while True:
        register_student()
        again = input("Register another student? (y/n): ").strip().lower()
        if again != "y":
            break
    print("Registration complete. Goodbye!")
