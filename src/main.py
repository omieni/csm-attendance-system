import cv2
import pandas as pd
from pyzbar import pyzbar
from datetime import datetime
import time
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# 1) LOAD "DATABASE" (test_database.csv)
# -----------------------------
DB_CSV = "test_database.csv"
df = pd.read_csv(DB_CSV, header=None, names=["id", "name", "role"])
user_lookup = {
    row["id"]: {"name": row["name"], "role": row["role"]}
    for idx, row in df.iterrows()
}

# -----------------------------
# 2) CONFIGURATION & GLOBALS
# -----------------------------
# Attendance tracking
attendance_sessions = []
active_ids = set()

# Debouncing
last_scan_time = {}
SCAN_COOLDOWN = 2.0

# Session and logging
session_start = datetime.now()
LOG_CSV = f"attendance_log_{session_start.strftime('%Y%m%d_%H%M%S')}.csv"

# Welcome message
welcome_message = ""
welcome_timer = 0
WELCOME_DURATION = 3.0

# CSM Theme Colors
CSM_PRIMARY_COLOR = (40, 31, 140)  # BGR format for OpenCV
CSM_PRIMARY_COLOR_RGB = (140, 31, 40)  # RGB format for PIL
CSM_LOGO_PATH = "assets/csm-logo.png"

# Logo cache
csm_logo_pil = None

# Font paths - Inter fonts only
INTER_BOLD_PATH = "assets/Fonts/Inter/Inter_18pt-Bold.ttf"
INTER_REGULAR_PATH = "assets/Fonts/Inter/Inter_18pt-Regular.ttf"

# Pre-loaded fonts
TITLE_FONT = None
SUBTITLE_FONT = None
HEADER_FONT = None
ENTRY_FONT = None
ROLE_FONT = None
FOOTER_FONT = None
WELCOME_FONT = None
QR_TEXT_FONT = None

# -----------------------------
# 3) FONT MANAGEMENT
# -----------------------------
def load_inter_font(bold=False):
    """Load Inter font from specified paths only."""
    font_path = INTER_BOLD_PATH if bold else INTER_REGULAR_PATH
    
    try:
        font = ImageFont.truetype(font_path, 18)
        print(f"[INFO] Loaded Inter font: {font_path}")
        return font
    except Exception as e:
        print(f"[ERROR] Failed to load Inter font {font_path}: {e}")
        return None

# -----------------------------
# 4) LOGO MANAGEMENT
# -----------------------------
def load_logo():
    """Load CSM logo using PIL for high quality"""
    global csm_logo_pil
    try:
        csm_logo_pil = Image.open(CSM_LOGO_PATH).convert("RGBA")
        height = 120
        aspect_ratio = csm_logo_pil.width / csm_logo_pil.height
        width = int(height * aspect_ratio)
        csm_logo_pil = csm_logo_pil.resize((width, height), Image.Resampling.LANCZOS)
        print(f"[INFO] CSM logo loaded: {width}x{height}")
    except Exception as e:
        print(f"[WARNING] Error loading logo: {e}")
        csm_logo_pil = None

# -----------------------------
# 5) UI PANEL CREATION
# -----------------------------
def create_high_quality_panel(width, height):
    """Create attendance panel using PIL for crisp rendering"""
    panel = Image.new('RGB', (width, height), (250, 250, 250))
    draw = ImageDraw.Draw(panel)
    
    # Header
    header_height = 140
    draw.rectangle([0, 0, width, header_height], fill=CSM_PRIMARY_COLOR_RGB)
    
    # Add logo and title
    text_x = 10
    if csm_logo_pil is not None:
        logo_x, logo_y = 10, 10
        panel.paste(csm_logo_pil, (logo_x, logo_y), csm_logo_pil)
        text_x = logo_x + csm_logo_pil.width + 20
    
    draw.text((text_x, 25), "CSM ATTENDANCE", font=TITLE_FONT, fill=(255, 255, 255))
    draw.text((text_x, 60), "SYSTEM", font=SUBTITLE_FONT, fill=(255, 255, 255))
    
    # Column headers
    time_col_x = 10
    status_col_x = 80
    name_role_col_x = 150
    header_y = header_height + 15
    
    draw.text((time_col_x, header_y), "TIME", font=HEADER_FONT, fill=CSM_PRIMARY_COLOR_RGB)
    draw.text((status_col_x, header_y), "STATUS", font=HEADER_FONT, fill=CSM_PRIMARY_COLOR_RGB)
    draw.text((name_role_col_x, header_y), "NAME (ROLE)", font=HEADER_FONT, fill=CSM_PRIMARY_COLOR_RGB)
    
    # Separator line
    line_y = header_y + 30
    draw.line([10, line_y, width - 10, line_y], fill=CSM_PRIMARY_COLOR_RGB, width=2)
    
    # Attendance entries
    y_offset = line_y + 25
    line_height = 30
    recent_entries = attendance_sessions[-10:] if len(attendance_sessions) > 10 else attendance_sessions
    
    for entry in reversed(recent_entries):
        if y_offset > height - 50:
            break
            
        status_color = (0, 150, 0) if entry["status"] == "IN" else (150, 0, 0)
        role_color = (128, 0, 128) if entry["role"] == "student" else (255, 140, 0)
        
        time_text = entry["time"]
        status_text = entry["status"]
        name_text = entry['name']
        role_text = f"({entry['role'].upper()})"
        
        # Draw entry data
        draw.text((time_col_x, y_offset), time_text, font=ENTRY_FONT, fill=(0, 0, 0))
        draw.text((status_col_x, y_offset), status_text, font=ENTRY_FONT, fill=status_color)
        draw.text((name_role_col_x, y_offset), name_text, font=ENTRY_FONT, fill=(0, 0, 0))
        
        # Role with spacing
        name_bbox = draw.textbbox((0, 0), name_text, font=ENTRY_FONT)
        name_width = name_bbox[2] - name_bbox[0]
        role_x = name_role_col_x + name_width + 10
        draw.text((role_x, y_offset), role_text, font=ROLE_FONT, fill=role_color)
        
        y_offset += line_height
    
    # Footer
    footer_y = height - 25
    footer_text = f"Session: {session_start.strftime('%Y-%m-%d')}"
    draw.text((10, footer_y), footer_text, font=FOOTER_FONT, fill=CSM_PRIMARY_COLOR_RGB)
    
    return panel

def build_attendance_panel(width, height):
    """Create attendance panel and convert to OpenCV format"""
    pil_panel = create_high_quality_panel(width, height)
    opencv_panel = cv2.cvtColor(np.array(pil_panel), cv2.COLOR_RGB2BGR)
    return opencv_panel

# -----------------------------
# 6) WELCOME MESSAGE
# -----------------------------
def draw_welcome_message(frame, message):
    """Draw welcome message with better quality using PIL overlay"""
    frame_h, frame_w = frame.shape[:2]
    
    bg_height = 80
    welcome_img = Image.new('RGBA', (frame_w, bg_height), (*CSM_PRIMARY_COLOR_RGB, 255))
    draw = ImageDraw.Draw(welcome_img)
    
    bbox = draw.textbbox((0, 0), message, font=WELCOME_FONT)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (frame_w - text_width) // 2
    text_y = (bg_height - text_height) // 2
    
    draw.text((text_x, text_y), message, font=WELCOME_FONT, fill=(255, 255, 255))
    
    welcome_cv = cv2.cvtColor(np.array(welcome_img), cv2.COLOR_RGBA2BGR)
    frame[frame_h - bg_height:frame_h, 0:frame_w] = welcome_cv

# -----------------------------
# 7) QR CODE PROCESSING
# -----------------------------
def decode_qr_codes(frame):
    """Returns decoded QR-text strings and draws bounding boxes on frame"""
    decoded_objects = pyzbar.decode(frame)
    ids_found = []

    for obj in decoded_objects:
        qr_text = obj.data.decode("utf-8")
        ids_found.append(qr_text)

        # Draw bounding box
        (x, y, w, h) = obj.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Draw QR text with PIL for better quality
        text_img = Image.new('RGBA', (w + 40, 30), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((5, 5), qr_text, font=QR_TEXT_FONT, fill=(0, 255, 0))
        
        text_cv = cv2.cvtColor(np.array(text_img), cv2.COLOR_RGBA2BGR)
        overlay_y = max(0, y - 35)
        overlay_x = max(0, x)
        
        overlay_h, overlay_w = text_cv.shape[:2]
        if overlay_y + overlay_h <= frame.shape[0] and overlay_x + overlay_w <= frame.shape[1]:
            mask = text_cv.sum(axis=2) > 0
            frame[overlay_y:overlay_y+overlay_h, overlay_x:overlay_x+overlay_w][mask] = text_cv[mask]

    return ids_found

# -----------------------------
# 8) ATTENDANCE TRACKING
# -----------------------------
def mark_time(qr_data: str):
    """Toggle check-in/check-out with debouncing"""
    global welcome_message, welcome_timer

    current_time = time.time()

    # Debouncing check
    if qr_data in last_scan_time:
        if current_time - last_scan_time[qr_data] < SCAN_COOLDOWN:
            return

    last_scan_time[qr_data] = current_time

    if qr_data not in user_lookup:
        print(f"[WARNING] Unknown ID: {qr_data}")
        return

    info = user_lookup[qr_data]
    now = datetime.now()
    time_str = now.strftime("%H:%M")

    # Check-in or check-out
    if qr_data not in active_ids:
        entry = {
            "id": qr_data,
            "name": info["name"],
            "role": info["role"],
            "time": time_str,
            "status": "IN",
            "timestamp": now
        }
        attendance_sessions.append(entry)
        active_ids.add(qr_data)
        welcome_message = f"Welcome, {info['name']}!"
        welcome_timer = current_time
        print(f"[INFO] Checked in {info['name']} at {time_str}")
        export_to_csv(entry)
    else:
        entry = {
            "id": qr_data,
            "name": info["name"],
            "role": info["role"],
            "time": time_str,
            "status": "OUT",
            "timestamp": now
        }
        attendance_sessions.append(entry)
        active_ids.remove(qr_data)
        welcome_message = f"Goodbye, {info['name']}!"
        welcome_timer = current_time
        print(f"[INFO] Checked out {info['name']} at {time_str}")
        export_to_csv(entry)

def export_to_csv(entry):
    """Export attendance entry to CSV in real time"""
    file_exists = os.path.isfile(LOG_CSV)

    df_entry = pd.DataFrame([{
        'id': entry['id'],
        'name': entry['name'],
        'role': entry['role'],
        'status': entry['status'],
        'time': entry['time'],
        'timestamp': entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
    }])

    df_entry.to_csv(LOG_CSV, mode='a', header=not file_exists, index=False)

# -----------------------------
# 9) MAIN APPLICATION
# -----------------------------
def main():
    global welcome_message, welcome_timer
    global TITLE_FONT, SUBTITLE_FONT, HEADER_FONT, ENTRY_FONT, ROLE_FONT, FOOTER_FONT, WELCOME_FONT, QR_TEXT_FONT

    # Initialize
    load_logo()
    
    # Load Inter fonts only
    print("[INFO] Loading Inter fonts...")
    TITLE_FONT = load_inter_font(bold=True)
    SUBTITLE_FONT = load_inter_font(bold=True)
    HEADER_FONT = load_inter_font(bold=True)
    ENTRY_FONT = load_inter_font(bold=False)
    ROLE_FONT = load_inter_font(bold=False)
    FOOTER_FONT = load_inter_font(bold=False)
    WELCOME_FONT = load_inter_font(bold=True)
    QR_TEXT_FONT = load_inter_font(bold=True)
    print("[INFO] Inter fonts loaded.")

    print(f"[INFO] CSM Attendance System - Session started at: {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] Creating attendance log: {LOG_CSV}")

    # Create log file with header
    with open(LOG_CSV, 'w') as f:
        f.write(f"# CSM Attendance Session Started: {session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("id,name,role,status,time,timestamp\n")

    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Could not read from webcam.")
        return

    frame_h, frame_w = frame.shape[:2]
    panel_w = 450
    window_name = "CSM Attendance System"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    print("[INFO] System started. Press 'f' for fullscreen, 'q' to quit")

    # Main loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Process QR codes
        ids = decode_qr_codes(frame)
        for qr_data in ids:
            mark_time(qr_data)

        # Draw welcome message
        current_time = time.time()
        if welcome_message and (current_time - welcome_timer < WELCOME_DURATION):
            draw_welcome_message(frame, welcome_message)
        elif current_time - welcome_timer >= WELCOME_DURATION:
            welcome_message = ""

        # Create combined display
        panel = build_attendance_panel(panel_w, frame_h)
        combined = np.zeros((frame_h, frame_w + panel_w, 3), dtype=np.uint8)
        combined[0:frame_h, 0:frame_w] = frame
        combined[0:frame_h, frame_w:frame_w + panel_w] = panel

        cv2.imshow(window_name, combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("f"):
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Cleanup
    session_end = datetime.now()
    session_duration = session_end - session_start

    with open(LOG_CSV, 'a') as f:
        f.write(f"# Session ended: {session_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Session duration: {session_duration}\n")
        f.write(f"# Total entries: {len(attendance_sessions)}\n")

    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] CSM Attendance System - Session ended")
    print(f"[INFO] Attendance log saved to: {LOG_CSV}")

if __name__ == "__main__":
    main()