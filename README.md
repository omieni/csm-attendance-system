# CSM Attendance System

CSM (Computer Science & Mathematics) Attendance System is a Python-based application designed to track attendance using QR codes. It utilizes a webcam to scan QR codes, logs attendance in a CSV file, and displays a real-time attendance panel.

## Features

- QR Code Scanning: Uses `pyzbar` to detect and decode QR codes from a live webcam feed.
- Attendance Logging: Records check-in and check-out times for users in a CSV file.
- Real-time Display: Shows a live feed from the webcam alongside a panel displaying recent attendance activity.
- User Database: Loads user information (ID, name, role) from a CSV file (`test_database.csv`).
- Custom Fonts & Styling: Uses the Inter font and custom colors for a branded UI.
- Debouncing: Prevents multiple scans of the same QR code in rapid succession.
- Welcome Messages: Displays a temporary welcome/goodbye message upon successful scan.

## Project Structure

```
.csm_attendance_system/
├── src/
│   ├── assets/
│   │   ├── csm-logo.png
│   │   └── Fonts/
│   │       └── Inter/
│   │           ├── Inter_18pt-Bold.ttf
│   │           └── Inter_18pt-Regular.ttf
│   ├── main.py                     # Main application script
│   ├── test_database.csv           # Sample user database
│   └── attendance_log_YYYYMMDD_HHMMSS.csv # Generated attendance logs
├── .gitignore
├── README.md
└── docs/
    └── setup_guide.md
```

## Setup and Installation

See the [Setup Guide](docs/setup_guide.md) for detailed instructions on how to set up the environment and run the application.

## Usage

1. Ensure `test_database.csv` is populated with user data.
2. Run `main.py`.
3. The application will open a fullscreen window with the webcam feed and attendance panel.
4. Present QR codes to the webcam for check-in/out.
5. Press 'f' to toggle fullscreen mode (if not already active).
6. Press 'q' to quit the application.

Attendance logs will be saved in the `src` directory with a timestamped filename.
