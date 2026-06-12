# Smart Face Recognition Attendance System

**Computer Vision Project — 6th Semester**

| Field | Detail |
|---|---|
| Submitted By | Muhammad Sami (F23BDOCS1E02139), Abdul Samad (F23BDOCS1E02198) |
| Submitted To | Sir Abdullah Soomro |
| Section | 2-E |

---

## Project Files

```
attendance_system/
├── attendance_system.py   ← Main system (train + real-time recognition)
├── register_student.py    ← Register new students via webcam
├── view_reports.py        ← View & summarise attendance records
├── requirements.txt       ← Python dependencies
├── known_faces/           ← Student image folders (auto-created)
│   └── AhmedKhan_F23001/  ← Example: Name_RollNo folder
│       ├── img_000.jpg
│       └── ...
├── attendance_records/    ← Daily CSV files (auto-created)
│   └── 2025-01-15_attendance.csv
└── models/
    └── encodings.pkl      ← Trained face encodings (auto-generated)
```

---

## Installation

### Step 1 — Install Python 3.10+
Download from https://python.org

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `dlib` and `face-recognition` may require CMake and Visual Studio Build Tools on Windows.
> On Linux: `sudo apt-get install cmake build-essential`

---

## How to Use

### Step 1 — Register Students
Run this **once for each student**:
```bash
python register_student.py
```
- Enter student name and roll number
- Webcam opens — look at camera
- 30 images are captured automatically
- Repeat for all students

### Step 2 — Train the Model
```bash
python attendance_system.py
```
Choose option **1** (Train encodings) the first time.
After adding new students, choose option **1** again to retrain.

### Step 3 — Run Attendance
```bash
python attendance_system.py
```
Choose option **2** (Start attendance) or **3** (Train + Start).
- Webcam opens and recognises faces in real-time
- Attendance is marked automatically in a CSV file
- Press **Q** to stop

### Step 4 — View Reports
```bash
python view_reports.py
```
- View today's attendance
- View any previous date
- Monthly summary with attendance percentage

---

## CSV Output Format

Each day creates a file like `2025-01-15_attendance.csv`:

```
Roll No,Name,Date,Time,Status
F23BDOCS1E02139,MuhammadSami,2025-01-15,09:03:47,Present
F23BDOCS1E02198,AbdulSamad,2025-01-15,09:04:12,Present
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Webcam not found | Check USB connection; change `cv2.VideoCapture(0)` to `(1)` |
| Low accuracy | Add more images per student (increase `IMAGES_PER_STUDENT`) |
| dlib install fails | Install CMake first; use Python 3.10 not 3.12 |
| Face not detected | Improve lighting; face must be clearly visible |
| Wrong person detected | Lower `TOLERANCE` in `attendance_system.py` (e.g. 0.45) |

---

## System Requirements

- Python 3.10+
- Webcam (USB or built-in)
- RAM: 4GB+ recommended
- OS: Windows 10/11, Ubuntu 20+, macOS 12+
