# CSM Attendance System - Setup Guide

This guide provides step-by-step instructions to set up and run the CSM Attendance System.

## Prerequisites

- Python 3.7 or higher
- Pip (Python package installer)
- A webcam connected to your computer

## 1. Clone the Repository (if applicable)

If you have the project in a Git repository, clone it to your local machine:

```bash
git clone <repository_url>
cd csm_attendance_system
```

If you have the files locally, navigate to the project's root directory (`csm_attendance_system`).

## 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

Open your terminal or command prompt in the project's root directory and run:

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows (PowerShell/CMD):**
  ```powershell
  .\venv\Scripts\Activate.ps1 
  ```
  or
  ```cmd
  venv\Scripts\activate.bat
  ```

- **macOS/Linux (Bash/Zsh):**
  ```bash
source venv/bin/activate
  ```

You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

## 3. Install Dependencies

Install the required Python packages using the `requirements.txt` file. If this file is not yet present, you can create it based on the imports in `src/main.py`.

**Create `requirements.txt` (if it doesn't exist):**

Manually create a file named `requirements.txt` in the project's root directory (`csm_attendance_system`) with the following content:

```txt
opencv-python
pandas
pyzbar
Pillow
numpy
```

**Install from `requirements.txt`:**

With your virtual environment activated, run:

```bash
pip install -r requirements.txt
```

This will install:
- `opencv-python`: For camera access and image processing.
- `pandas`: For data manipulation, especially with CSV files.
- `pyzbar`: For QR code decoding.
- `Pillow`: For advanced image manipulation and text rendering.
- `numpy`: For numerical operations, often a dependency for OpenCV.

## 4. Prepare User Database

The application loads user information from `src/test_database.csv`. Ensure this file exists and is correctly formatted. Each line should represent a user with their ID, name, and role, separated by commas, without a header row.

**Example `src/test_database.csv`:**

```csv
USER001,Alice Wonderland,student
USER002,Bob The Builder,staff
USER003,Charlie Brown,student
```

## 5. Prepare Assets

- Ensure the CSM logo is present at `src/assets/csm-logo.png`.
- Ensure the Inter font file is present at `src/assets/Inter/Inter-VariableFont_opsz,wght.ttf`.

## 6. Running the Application

Once the setup is complete:

1. Navigate to the `src` directory if you are not already there:
   ```bash
   cd src
   ```
2. Run the main script:
   ```bash
   python main.py
   ```

The application window should appear, displaying the webcam feed and the attendance panel.

## 7. Troubleshooting

- **Webcam Not Detected:** 
    - Ensure your webcam is properly connected and drivers are installed.
    - If you have multiple cameras, OpenCV might default to the wrong one. You might need to change `cv2.VideoCapture(0)` in `main.py` to `cv2.VideoCapture(1)` (or another index).
- **Font Issues:**
    - If the Inter font doesn't load, the application will attempt to use system fallbacks (Segoe UI, Arial, etc.). Check the console output for messages related to font loading.
    - Ensure the path `src/assets/Inter/Inter-VariableFont_opsz,wght.ttf` is correct.
- **Module Not Found Errors:** 
    - Make sure your virtual environment is activated (`(venv)` should be in your prompt).
    - Ensure all packages from `requirements.txt` were installed successfully.
- **QR Code Scanning Issues:**
    - Ensure QR codes are clear, well-lit, and not too small or too far from the camera.

## 8. Deactivating the Virtual Environment

When you're done working on the project, you can deactivate the virtual environment:

```bash
deactivate
```
