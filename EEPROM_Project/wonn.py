import os
import time
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024  # 1KB EEPROM
LOG_FILE = "eeprom_logs.txt"

# ---------- EEPROM Data Structure ----------
class EEPROMStruct(ctypes.Structure):
    _fields_ = [("id", ctypes.c_uint8),
                ("value", ctypes.c_uint16),
                ("flag", ctypes.c_uint8)]

class EEPROMUnion(ctypes.Union):
    _fields_ = [("data", EEPROMStruct),
                ("raw", ctypes.c_ubyte * ctypes.sizeof(EEPROMStruct))]

# ---------- Tooltip Class ----------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0,0,0,0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=3)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

# ---------- EEPROM Operations ----------
def ensure_eeprom():
    if not os.path.exists(EEPROM_FILE):
        with open(EEPROM_FILE, "wb") as f:
            f.write(bytes([0xFF] * EEPROM_SIZE))
        log("EEPROM file created and initialized.", "info")

def write_byte(address, value):
    if not (0 <= address < EEPROM_SIZE):
        log(f"Error: Address {address} out of range.", "error")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes([value]))
    log(f"Byte written: Address={address}, Value={value}", "success")

def read_byte(address):
    if not (0 <= address < EEPROM_SIZE):
        log(f"Error: Address {address} out of range.", "error")
        return
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        value = f.read(1)[0]
    log(f"Byte read: Address={address}, Value={value}", "success")
    return value

def write_bytes(address, data_list):
    if address + len(data_list) > EEPROM_SIZE:
        log("Error: Data exceeds EEPROM size.", "error")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes(data_list))
    log(f"Multiple bytes written at {address}: {data_list}", "success")

def read_bytes(address, length):
    if address + length > EEPROM_SIZE:
        log("Error: Read exceeds EEPROM size.", "error")
        return
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = list(f.read(length))
    log(f"Multiple bytes read at {address}: {data}", "success")
    return data

def write_string(address, string):
    data = string.encode('utf-8')
    write_bytes(address, data)
    log(f"String written at {address}: {string}", "success")

def read_string(address, length):
    data = read_bytes(address, length)
    if data is None:
        return
    string = bytes(data).decode('utf-8', errors='ignore')
    log(f"String read at {address}: {string}", "success")
    return string

def dump_eeprom(start=0, end=EEPROM_SIZE):
    if end > EEPROM_SIZE:
        end = EEPROM_SIZE
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(end - start)
    hex_str = ' '.join(f"{b:02X}" for b in data)
    log(f"EEPROM Dump [{start}:{end}]:\n{hex_str}", "info")

def checksum_block(start=0, length=EEPROM_SIZE):
    if start + length > EEPROM_SIZE:
        length = EEPROM_SIZE - start
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(length)
    chksum = sum(data) % 256
    log(f"Block checksum [{start}:{start+length}]: {chksum}", "info")
    return chksum

def delete_byte(address):
    write_byte(address, 0xFF)

def delete_bytes(address, length):
    write_bytes(address, [0xFF]*length)
    log(f"Deleted {length} bytes from {address}", "success")

def reset_eeprom():
    write_bytes(0, [0xFF]*EEPROM_SIZE)
    log("EEPROM reset complete.", "success")

def power_cycle():
    log("Simulating power cycle...", "info")
    time.sleep(0.5)
    log("Power cycle complete.", "success")

def write_struct(address, struct_obj):
    union = EEPROMUnion()
    union.data = struct_obj
    write_bytes(address, list(union.raw))
    log(f"Struct written at {address}: {struct_obj}", "success")

def read_struct(address):
    union = EEPROMUnion()
    raw_data = read_bytes(address, ctypes.sizeof(union))
    if raw_data is None:
        return
    for i in range(len(raw_data)):
        union.raw[i] = raw_data[i]
    log(f"Struct read at {address}: id={union.data.id}, value={union.data.value}, flag={union.data.flag}", "success")
    return union.data

# ---------- Logging ----------
def log(message, level="info"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    console.config(state='normal')
    console.insert("end", f"{timestamp} {message}\n", level)
    console.see("end")
    console.config(state='disabled')
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} [{level.upper()}] {message}\n")

def reset_log():
    console.config(state='normal')
    console.delete(1.0, "end")
    console.config(state='disabled')
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("")
    log("Log cleared.", "info")

def exit_gui():
    log("Exiting EEPROM GUI.", "info")
    root.destroy()

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("EEPROM Simulator GUI")
root.geometry("900x750")

frame_controls = tk.Frame(root)
frame_controls.pack(side="top", fill="x", padx=10, pady=10)

tk.Label(frame_controls, text="Address").grid(row=0, column=0)
entry_address = tk.Entry(frame_controls, width=8)
entry_address.grid(row=0, column=1)

tk.Label(frame_controls, text="Value / Bytes").grid(row=0, column=2)
entry_value = tk.Entry(frame_controls, width=20)
entry_value.grid(row=0, column=3, columnspan=2)

tk.Label(frame_controls, text="String / Multi-byte").grid(row=1, column=0)
entry_string = tk.Entry(frame_controls, width=40)
entry_string.grid(row=1, column=1, columnspan=4)

tk.Label(frame_controls, text="Length").grid(row=2, column=0)
entry_length = tk.Entry(frame_controls, width=8)
entry_length.grid(row=2, column=1)

tk.Label(frame_controls, text="Struct ID").grid(row=3, column=0)
entry_id = tk.Entry(frame_controls, width=8)
entry_id.grid(row=3, column=1)

tk.Label(frame_controls, text="Struct Value").grid(row=3, column=2)
entry_struct_value = tk.Entry(frame_controls, width=8)
entry_struct_value.grid(row=3, column=3)

tk.Label(frame_controls, text="Struct Flag").grid(row=3, column=4)
entry_flag = tk.Entry(frame_controls, width=8)
entry_flag.grid(row=3, column=5)

# ---------- Buttons ----------
btn_frame = tk.Frame(root)
btn_frame.pack(fill="x", padx=10, pady=10)

buttons = [
    ("Write Byte", lambda: write_byte(int(entry_address.get()), int(entry_value.get()))),
    ("Read Byte", lambda: read_byte(int(entry_address.get()))),
    ("Write Multiple Bytes", lambda: write_bytes(int(entry_address.get()), [int(b) for b in entry_value.get().split(",")])),
    ("Read Multiple Bytes", lambda: read_bytes(int(entry_address.get()), int(entry_length.get()))),
    ("Write String", lambda: write_string(int(entry_address.get()), entry_string.get())),
    ("Read String", lambda: read_string(int(entry_address.get()), int(entry_length.get()))),
    ("Dump EEPROM Section", lambda: dump_eeprom(int(entry_address.get()), int(entry_length.get()))),
    ("Compute Block Checksum", lambda: checksum_block(int(entry_address.get()), int(entry_length.get()))),
    ("Reset Log File", reset_log),
    ("Delete Byte", lambda: delete_byte(int(entry_address.get()))),
    ("Delete Bytes", lambda: delete_bytes(int(entry_address.get()), int(entry_length.get()))),
    ("Delete All Written Data", lambda: delete_bytes(0, EEPROM_SIZE)),
    ("Reset EEPROM", reset_eeprom),
    ("Simulate Power Cycle", power_cycle),
    ("Struct Write", lambda: write_struct(int(entry_address.get()), EEPROMStruct(int(entry_id.get()), int(entry_struct_value.get()), int(entry_flag.get())))),
    ("Struct Read", lambda: read_struct(int(entry_address.get()))),
    ("Exit", exit_gui)
]

btn_widgets = []
for i, (text, cmd) in enumerate(buttons):
    b = tk.Button(btn_frame, text=text, width=20, command=cmd)
    b.grid(row=i//3, column=i%3, padx=5, pady=5)
    btn_widgets.append(b)

# ---------- Console ----------
console = scrolledtext.ScrolledText(root, state="disabled", height=30)
console.pack(fill="both", padx=10, pady=10, expand=True)
console.tag_config("info", foreground="orange")
console.tag_config("error", foreground="red")
console.tag_config("success", foreground="green")

# ---------- Tooltips ----------
ToolTip(entry_address, "EEPROM address (0-1023)")
ToolTip(entry_value, "Byte or comma-separated bytes")
ToolTip(entry_string, "String or multi-byte input")
ToolTip(entry_length, "Length for read/dump/delete")
ToolTip(entry_id, "Struct ID (0-255)")
ToolTip(entry_struct_value, "Struct value (0-65535)")
ToolTip(entry_flag, "Struct flag (0-255)")

# Initialize EEPROM and log
ensure_eeprom()
log("EEPROM Simulator GUI ready.", "info")

root.mainloop()
