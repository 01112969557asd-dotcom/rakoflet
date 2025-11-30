1# -*- coding: utf-8 -*-
import tkinter as tk
import serial
import time

# ================== SERIAL CONFIG ==================
PORT = "COM4"   # غيّرها للبورت الحقيقي (COM3 مثلاً)
BAUD = 9600

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ Connected to", PORT)
except Exception as e:
    print("❌ Serial error:", e)
    ser = None

# ============ RECORDING & LOOP PLAYBACK ============
is_recording = False
recording = []              # list of (time_offset_sec, cmd)
record_start_time = 0.0

loop_playback = False       # لو True → التشغيل يعيد نفسه

def send_raw(cmd: str):
    """إرسال أمر للآردوينو بدون تسجيل."""
    if ser is None or not ser.is_open:
        status_var.set("❌ Serial not connected")
        print("Serial not open")
        return
    try:
        ser.write((cmd + "\n").encode("utf-8"))
        print(">>", cmd)
    except Exception as e:
        print("Send error:", e)

def send_servo_cmd(cmd: str):
    """إرسال أمر للسيرفو + تسجيل لو record شغال."""
    global recording
    send_raw(cmd)
    if is_recording and len(cmd) == 2 and cmd[0] in "UuDd":
        t = time.time() - record_start_time
        recording.append((t, cmd))
        status_var.set(f"Recording... {len(recording)} events")

def start_record():
    global is_recording, recording, record_start_time
    recording = []
    record_start_time = time.time()
    is_recording = True
    status_var.set("⏺ Recording...")

def stop_record():
    global is_recording
    is_recording = False
    status_var.set(f"Record stopped ({len(recording)} events).")

def _play_record_once():
    """تشغيل sequence مرة واحدة (داخلي)."""
    if not recording:
        status_var.set("No recording saved.")
        return

    status_var.set("▶ Playing recorded motion...")
    for t_offset, cmd in recording:
        delay_ms = int(t_offset * 1000)
        root.after(delay_ms, lambda c=cmd: send_raw(c))

def play_record():
    """تشغيل التسجيل + لو loop_on يشغّل نفسه تاني."""
    if not recording:
        status_var.set("No recording saved.")
        return

    total_time = int((recording[-1][0] * 1000) + 500)
    _play_record_once()

    if loop_playback:
        root.after(total_time, play_record)

def toggle_loop():
    global loop_playback
    loop_playback = not loop_playback
    loop_btn_text = "Loop: ON" if loop_playback else "Loop: OFF"
    btn_loop.config(text=loop_btn_text)
    status_var.set(f"Loop playback = {'ON' if loop_playback else 'OFF'}")

def home_all():
    send_raw("H")
    status_var.set("Sent HOME (90° on all axes).")

# ===================== DEMOS (10+) =====================
def run_demo_sequence(demo_id: int):
    """مجموعة رقصات جاهزة."""
    demos = {}

    # كل ديمو: list of (delay_ms, [cmds])
    demos[1] = [
        (0,   ["U0"]), (350, ["u0"]),
        (0,   ["D0"]), (350, ["d0"]),
        (0,   ["U3"]), (250, ["u3"]),
        (0,   ["D3"]), (250, ["d3"]),
        (0,   ["U5"]), (250, ["u5"]),
        (0,   ["D5"]), (250, ["d5"]),
    ]

    demos[2] = [
        (0,   ["U1","U2"]), (300, ["u1","u2"]),
        (0,   ["D1","D2"]), (300, ["d1","d2"]),
        (0,   ["U4"]),      (250, ["u4"]),
        (0,   ["D4"]),      (250, ["d4"]),
    ]

    demos[3] = [
        (0,   ["U0","U1"]), (250, ["u1"]),
        (0,   ["U2"]),      (250, ["u2"]),
        (0,   ["D1","D2"]), (300, ["d1","d2"]),
        (0,   ["U5"]),      (250, ["u5"]),
    ]

    demos[4] = [
        (0,   ["U3","U4"]), (250, ["u3","u4"]),
        (0,   ["D3","D4"]), (250, ["d3","d4"]),
        (0,   ["U5"]),      (250, ["u5"]),
        (0,   ["D5"]),      (250, ["d5"]),
    ]

    demos[5] = [
        (0,   ["U0","U3"]), (300, ["u0","u3"]),
        (0,   ["D0","D3"]), (300, ["d0","d3"]),
        (0,   ["U1","U2"]), (300, ["u1","u2"]),
    ]

    demos[6] = [
        (0,   ["U2"]), (250, ["u2"]),
        (0,   ["D2"]), (250, ["d2"]),
        (0,   ["U1"]), (250, ["u1"]),
        (0,   ["D1"]), (250, ["d1"]),
        (0,   ["U5"]), (200, ["u5"]),
        (0,   ["D5"]), (200, ["d5"]),
    ]

    demos[7] = [
        (0,   ["U0","U4"]), (250, ["u4"]),
        (0,   ["D4"]),      (250, ["d4"]),
        (0,   ["D0"]),      (250, ["d0"]),
        (0,   ["U3"]),      (200, ["u3"]),
        (0,   ["D3"]),      (200, ["d3"]),
    ]

    demos[8] = [
        (0,   ["U1","U3","U5"]), (300, ["u1","u3","u5"]),
        (0,   ["D1","D3","D5"]), (300, ["d1","d3","d5"]),
        (0,   ["U2","U4"]),      (250, ["u2","u4"]),
        (0,   ["D2","D4"]),      (250, ["d2","d4"]),
    ]

    demos[9] = [
        (0,   ["U0","U1","U2"]), (300, ["u1","u2"]),
        (0,   ["D1","D2"]),      (300, ["d1","d2"]),
        (0,   ["D0"]),           (300, ["d0"]),
        (0,   ["U5"]),           (200, ["u5"]),
    ]

    demos[10] = [
        (0,   ["U0","U2","U4"]), (250, ["u0","u2","u4"]),
        (0,   ["D0","D2","D4"]), (250, ["d0","d2","d4"]),
        (0,   ["U3","U5"]),      (250, ["u3","u5"]),
        (0,   ["D3","D5"]),      (250, ["d3","d5"]),
    ]

    seq = demos.get(demo_id)
    if not seq:
        status_var.set("No such demo.")
        return

    status_var.set(f"Running Demo {demo_id}...")

    t_acc = 0
    for delay_ms, cmds in seq:
        t_acc += delay_ms
        root.after(
            t_acc,
            lambda cs=list(cmds): [send_raw(c) for c in cs]
        )

def on_close():
    if ser is not None and ser.is_open:
        ser.close()
    root.destroy()

# ===================== UI / THEME =====================
BG_MAIN       = "#f3f4f7"   # رمادي فاتح
CARD_BG       = "#ffffff"
BTN_ORANGE    = "#ff7a1a"
BTN_ORANGE_DK = "#e06710"
TEXT_DARK     = "#222222"
TEXT_MUTED    = "#777777"

root = tk.Tk()
root.title("6-DOF Robot Arm")
root.geometry("560x750")
root.configure(bg=BG_MAIN)
root.resizable(False, False)

def card_frame(parent, title):
    outer = tk.Frame(parent, bg=BG_MAIN)
    outer.pack(padx=12, pady=6, fill="x")

    lbl = tk.Label(
        outer, text=title,
        bg=BG_MAIN, fg=TEXT_DARK,
        font=("Segoe UI", 10, "bold")
    )
    lbl.pack(anchor="w", pady=(0, 2))

    inner = tk.Frame(
        outer,
        bg=CARD_BG,
        bd=1,
        relief="solid"
    )
    inner.pack(fill="x", padx=0, pady=(0, 2))
    return inner

def create_button(parent, text, cmd=None, width=12, font_size=10):
    btn = tk.Button(
        parent,
        text=text,
        command=cmd,
        width=width,
        font=("Segoe UI", font_size, "bold"),
        bg=BTN_ORANGE,
        fg="black",
        activebackground=BTN_ORANGE_DK,
        activeforeground="black",
        bd=0,
        relief="flat",
        cursor="hand2"
    )
    return btn

# ===== Title =====
title_lbl = tk.Label(
    root,
    text="6-DOF ROBOT ARM CONTROLLER",
    font=("Segoe UI", 14, "bold"),
    bg=BG_MAIN,
    fg=TEXT_DARK
)
title_lbl.pack(pady=(10, 2))

subtitle = tk.Label(
    root,
    text="Manual • Crane-style control • Record & Replay • Demos",
    font=("Segoe UI", 9),
    bg=BG_MAIN,
    fg=TEXT_MUTED
)
subtitle.pack(pady=(0, 6))

# ===== Record & Loop card =====
rec_frame = card_frame(root, "Record • Replay • Home")

btn_rec_start = create_button(rec_frame, "⏺ Start Record", start_record, width=14)
btn_rec_stop  = create_button(rec_frame, "⏹ Stop Record",  stop_record,  width=14)
btn_play      = create_button(rec_frame, "▶ Play",         play_record,  width=10)
btn_home      = create_button(rec_frame, "HOME 90°",       home_all,     width=10)

btn_rec_start.grid(row=0, column=0, padx=6, pady=6)
btn_rec_stop.grid( row=0, column=1, padx=6, pady=6)
btn_play.grid(     row=0, column=2, padx=6, pady=6)
btn_home.grid(     row=0, column=3, padx=6, pady=6)

btn_loop = create_button(rec_frame, "Loop: OFF", toggle_loop, width=12, font_size=9)
btn_loop.grid(row=1, column=0, columnspan=2, padx=6, pady=(0, 6))

# ===== Demo card =====
demo_frame = card_frame(root, "Demos (Fun / Testing)")

for i in range(1, 11):
    btn = create_button(
        demo_frame,
        f"Demo {i}",
        cmd=lambda d=i: run_demo_sequence(d),
        width=10,
        font_size=9
    )
    r = (i - 1) // 5
    c = (i - 1) % 5
    btn.grid(row=r, column=c, padx=4, pady=4)

# ===== High-level controls (crane style) =====
macro_frame = card_frame(root, "Crane-style controls")

# Base (A0)
btn_base_left  = create_button(macro_frame, "Base Left (A0)",  width=16)
btn_base_right = create_button(macro_frame, "Base Right (A0)", width=16)
btn_base_left.grid( row=0, column=0, padx=6, pady=6)
btn_base_right.grid(row=0, column=1, padx=6, pady=6)
btn_base_left.bind("<ButtonPress>",   lambda e: send_servo_cmd("D0"))
btn_base_left.bind("<ButtonRelease>", lambda e: send_servo_cmd("d0"))
btn_base_right.bind("<ButtonPress>",   lambda e: send_servo_cmd("U0"))
btn_base_right.bind("<ButtonRelease>", lambda e: send_servo_cmd("u0"))

# Columns (A1 + A2)
btn_cols_up   = create_button(macro_frame, "Arm Up (A1+A2)",   width=16)
btn_cols_down = create_button(macro_frame, "Arm Down (A1+A2)", width=16)
btn_cols_up.grid(  row=1, column=0, padx=6, pady=6)
btn_cols_down.grid(row=1, column=1, padx=6, pady=6)
btn_cols_up.bind("<ButtonPress>",
                 lambda e: (send_servo_cmd("U1"), send_servo_cmd("U2")))
btn_cols_up.bind("<ButtonRelease>",
                 lambda e: (send_servo_cmd("u1"), send_servo_cmd("u2")))
btn_cols_down.bind("<ButtonPress>",
                   lambda e: (send_servo_cmd("D1"), send_servo_cmd("D2")))
btn_cols_down.bind("<ButtonRelease>",
                   lambda e: (send_servo_cmd("d1"), send_servo_cmd("d2")))

# Head L/R (A3)
btn_head_left  = create_button(macro_frame, "Head Left (A3)",  width=16)
btn_head_right = create_button(macro_frame, "Head Right (A3)", width=16)
btn_head_left.grid( row=2, column=0, padx=6, pady=6)
btn_head_right.grid(row=2, column=1, padx=6, pady=6)
btn_head_left.bind("<ButtonPress>",   lambda e: send_servo_cmd("D3"))
btn_head_left.bind("<ButtonRelease>", lambda e: send_servo_cmd("d3"))
btn_head_right.bind("<ButtonPress>",   lambda e: send_servo_cmd("U3"))
btn_head_right.bind("<ButtonRelease>", lambda e: send_servo_cmd("u3"))

# Head Up/Down (A4)
btn_head_up   = create_button(macro_frame, "Head Up (A4)",   width=16)
btn_head_down = create_button(macro_frame, "Head Down (A4)", width=16)
btn_head_up.grid(  row=3, column=0, padx=6, pady=6)
btn_head_down.grid(row=3, column=1, padx=6, pady=6)
btn_head_up.bind("<ButtonPress>",   lambda e: send_servo_cmd("U4"))
btn_head_up.bind("<ButtonRelease>", lambda e: send_servo_cmd("u4"))
btn_head_down.bind("<ButtonPress>",   lambda e: send_servo_cmd("D4"))
btn_head_down.bind("<ButtonRelease>", lambda e: send_servo_cmd("d4"))

# Gripper (A5)
btn_grip_close = create_button(macro_frame, "Grip Close (A5)", width=16)
btn_grip_open  = create_button(macro_frame, "Grip Open (A5)",  width=16)
btn_grip_close.grid(row=4, column=0, padx=6, pady=6)
btn_grip_open.grid( row=4, column=1, padx=6, pady=6)
btn_grip_close.bind("<ButtonPress>",   lambda e: send_servo_cmd("U5"))
btn_grip_close.bind("<ButtonRelease>", lambda e: send_servo_cmd("u5"))
btn_grip_open.bind("<ButtonPress>",    lambda e: send_servo_cmd("D5"))
btn_grip_open.bind("<ButtonRelease>",  lambda e: send_servo_cmd("d5"))

# ===== Manual per-servo controls =====
manual_frame = card_frame(root, "Manual fine control (each axis)")

servo_labels = [
    "A0 - Base",
    "A1 - Column 1",
    "A2 - Column 2",
    "A3 - Head Left/Right",
    "A4 - Head Up/Down",
    "A5 - Gripper"
]

for i in range(6):
    row = i
    lbl = tk.Label(
        manual_frame, text=servo_labels[i],
        bg=CARD_BG, fg=TEXT_DARK,
        font=("Segoe UI", 9)
    )
    lbl.grid(row=row, column=0, padx=6, pady=4, sticky="w")

    btn_plus = create_button(manual_frame, "+", width=4, font_size=9)
    btn_minus = create_button(manual_frame, "-", width=4, font_size=9)
    btn_plus.grid( row=row, column=1, padx=4, pady=4)
    btn_minus.grid(row=row, column=2, padx=4, pady=4)

    btn_plus.bind("<ButtonPress>",   lambda e, idx=i: send_servo_cmd(f"U{idx}"))
    btn_plus.bind("<ButtonRelease>", lambda e, idx=i: send_servo_cmd(f"u{idx}"))
    btn_minus.bind("<ButtonPress>",   lambda e, idx=i: send_servo_cmd(f"D{idx}"))
    btn_minus.bind("<ButtonRelease>", lambda e, idx=i: send_servo_cmd(f"d{idx}"))

# ===== Status bar =====
status_var = tk.StringVar()
status_var.set(f"Connected on {PORT}" if ser else "❌ Serial not connected")

status_bar = tk.Label(
    root,
    textvariable=status_var,
    font=("Segoe UI", 9),
    bg=BG_MAIN,
    fg=TEXT_MUTED,
    anchor="w"
)
status_bar.pack(fill="x", padx=12, pady=8)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
