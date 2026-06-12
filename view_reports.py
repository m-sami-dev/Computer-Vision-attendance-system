"""
============================================================
  Attendance Report Viewer & Summary Generator
  View, filter, and export attendance records.
============================================================
"""

import os
import csv
import glob
from datetime import datetime, date


ATTENDANCE_DIR = "attendance_records"


def list_records():
    """List all CSV attendance files."""
    files = sorted(glob.glob(os.path.join(ATTENDANCE_DIR, "*.csv")))
    if not files:
        print("\n[INFO] No attendance records found yet.\n")
        return []
    print("\nAvailable Attendance Records:")
    print("-" * 40)
    for i, f in enumerate(files, 1):
        print(f"  {i}. {os.path.basename(f)}")
    print()
    return files


def load_csv(path: str) -> list[dict]:
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def print_table(rows: list[dict]):
    if not rows:
        print("  [No records]\n")
        return
    headers = list(rows[0].keys())
    widths  = {h: max(len(h), max(len(r.get(h, "")) for r in rows)) for h in headers}
    sep     = "+-" + "-+-".join("-" * widths[h] for h in headers) + "-+"
    header  = "| " + " | ".join(h.ljust(widths[h]) for h in headers) + " |"
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "| " + " | ".join(row.get(h, "").ljust(widths[h]) for h in headers) + " |"
        print(line)
    print(sep)
    print()


def monthly_summary():
    """Print a summary: how many days each student was present."""
    files = sorted(glob.glob(os.path.join(ATTENDANCE_DIR, "*.csv")))
    if not files:
        print("\n[INFO] No records to summarise.\n")
        return

    total_days  = len(files)
    student_days: dict[str, set] = {}

    for fpath in files:
        day = os.path.basename(fpath).replace("_attendance.csv", "")
        rows = load_csv(fpath)
        for row in rows:
            name = f"{row['Name']} ({row['Roll No']})"
            student_days.setdefault(name, set()).add(day)

    print("\n" + "=" * 55)
    print("  MONTHLY ATTENDANCE SUMMARY")
    print(f"  Total class days on record: {total_days}")
    print("=" * 55)
    print(f"  {'Student':<35} {'Days Present':>12}  {'%':>6}")
    print("-" * 55)
    for name, days in sorted(student_days.items()):
        pct = (len(days) / total_days) * 100
        flag = " ⚠️ " if pct < 75 else ""
        print(f"  {name:<35} {len(days):>12}  {pct:>5.1f}%{flag}")
    print("=" * 55 + "\n")


def main():
    print("=" * 55)
    print("  Smart Attendance — Report Viewer")
    print("=" * 55)

    while True:
        print("\nOptions:")
        print("  1. View today's attendance")
        print("  2. View a specific date's attendance")
        print("  3. Monthly summary (all students)")
        print("  4. Exit")
        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            today_file = os.path.join(
                ATTENDANCE_DIR,
                date.today().strftime("%Y-%m-%d") + "_attendance.csv"
            )
            if not os.path.exists(today_file):
                print("\n[INFO] No attendance recorded today yet.\n")
            else:
                rows = load_csv(today_file)
                print(f"\n--- Attendance for {date.today()} ---\n")
                print_table(rows)
                print(f"  Total present: {len(rows)}")

        elif choice == "2":
            files = list_records()
            if files:
                idx = input("Enter record number: ").strip()
                try:
                    selected = files[int(idx) - 1]
                    rows     = load_csv(selected)
                    print(f"\n--- {os.path.basename(selected)} ---\n")
                    print_table(rows)
                    print(f"  Total present: {len(rows)}")
                except (ValueError, IndexError):
                    print("[ERROR] Invalid selection.")

        elif choice == "3":
            monthly_summary()

        elif choice == "4":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
