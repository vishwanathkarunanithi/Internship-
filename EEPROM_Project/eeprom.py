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

def write_string(address, string):
    data = string.encode('utf-8')
    if address + len(data) > EEPROM_SIZE:
        log("Error: String too long for EEPROM at this address.", "error")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(data)
    log(f"String written at address {address}: {string}", "success")

def read_string(address, length):
    if address + length > EEPROM_SIZE:
        log("Error: Read length exceeds EEPROM size.", "error")
        return
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = f.read(length)
        string = data.decode('utf-8', errors='ignore')
    log(f"String read at address {address}: {string}", "success")
    return string

def dump_eeprom():
    with open(EEPROM_FILE, "rb") as f:
        data = f.read()
    hex_str = ' '.join(f"{b:02X}" for b in data)
    log("EEPROM Dump:\n" + hex_str, "info")

def checksum():
    with open(EEPROM_FILE, "rb") as f:
        data = f.read()
    chksum = sum(data) % 256
    log(f"EEPROM Checksum: {chksum}", "info")
    return chksum

def delete_byte(address):
    write_byte(address, 0xFF)
    log(f"Deleted byte at address {address}", "success")

def reset_eeprom():
    with open(EEPROM_FILE, "r+b") as f:
        f.write(bytes([0xFF] * EEPROM_SIZE))
    log("EEPROM reset complete.", "success")

def power_cycle():
    log("Simulating power cycle...", "info")
    time.sleep(0.5)
    log("Power cycle complete.", "success")

def write_struct(address, struct_obj):
    union = EEPROMUnion()
    union.data = struct_obj
    if address + ctypes.sizeof(union) > EEPROM_SIZE:
        log("Error: Struct too big for EEPROM at this address.", "error")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytearray(union.raw))
    log(f"Struct written at address {address}: {struct_obj}", "success")

def read_struct(address):
    union = EEPROMUnion()
    if address + ctypes.sizeof(union) > EEPROM_SIZE:
        log("Error: Struct read exceeds EEPROM size.", "error")
        return
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = f.read(ctypes.sizeof(union))
        for i in range(len(union.raw)):
            union.raw[i] = data[i]
    log(f"Struct read at address {address}: id={union.data.id}, value={union.data.value}, flag={union.data.flag}", "success")
    return union.data

# ---------- GUI Logging with file ----------
def log(message, level="info"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    # Console
    console.config(state='normal')
    console.insert("end", f"{timestamp} {message}\n", level)
    console.see("end")
    console.config(state='disabled')
    # File
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} [{level.upper()}] {message}\n")

def reset_log():
    console.config(state='normal')
    console.delete(1.0, "end")
    console.config(state='disabled')
    # Clear log file if exists
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("")
    log("Log cleared.", "info")

# ---------- GUI Callbacks ----------
def btn_write_byte():
    try:
        addr = int(entry_address.get())
        val = int(entry_value.get())
        write_byte(addr, val)
    except:
        log("Invalid input for Write Byte.", "error")

def btn_read_byte():
    try:
        addr = int(entry_address.get())
        read_byte(addr)
    except:
        log("Invalid input for Read Byte.", "error")

def btn_write_string():
    try:
        addr = int(entry_address.get())
        write_string(addr, entry_string.get())
    except:
        log("Invalid input for Write String.", "error")

def btn_read_string():
    try:
        addr = int(entry_address.get())
        length = int(entry_length.get())
        read_string(addr, length)
    except:
        log("Invalid input for Read String.", "error")

def btn_dump():
    dump_eeprom()

def btn_checksum():
    checksum()

def btn_delete():
    try:
        addr = int(entry_address.get())
        delete_byte(addr)
    except:
        log("Invalid input for Delete Byte.", "error")

def btn_reset():
    reset_eeprom()

def btn_power_cycle():
    power_cycle()

def btn_write_struct():
    try:
        struct_obj = EEPROMStruct(
            id=int(entry_id.get()),
            value=int(entry_struct_value.get()),
            flag=int(entry_flag.get())
        )
        addr = int(entry_address.get())
        write_struct(addr, struct_obj)
    except:
        log("Invalid input for Write Struct.", "error")

def btn_read_struct():
    try:
        addr = int(entry_address.get())
        read_struct(addr)
    except:
        log("Invalid input for Read Struct.", "error")

# ---------- GUI Layout ----------
root = tk.Tk()
root.title("EEPROM Simulator GUI")
root.geometry("850x700")

frame_controls = tk.Frame(root)
frame_controls.pack(side="top", fill="x", padx=10, pady=10)

tk.Label(frame_controls, text="Address").grid(row=0, column=0)
entry_address = tk.Entry(frame_controls, width=8)
entry_address.grid(row=0, column=1)

tk.Label(frame_controls, text="Value").grid(row=0, column=2)
entry_value = tk.Entry(frame_controls, width=8)
entry_value.grid(row=0, column=3)

tk.Label(frame_controls, text="String").grid(row=1, column=0)
entry_string = tk.Entry(frame_controls, width=20)
entry_string.grid(row=1, column=1, columnspan=3)

tk.Label(frame_controls, text="Length").grid(row=2, column=0)
entry_length = tk.Entry(frame_controls, width=8)
entry_length.grid(row=2, column=1)

tk.Label(frame_controls, text="Struct ID").grid(row=3, column=0)
entry_id = tk.Entry(frame_controls, width=8)
entry_id.grid(row=3, column=1)

tk.Label(frame_controls, text="Struct Value").grid(row=3, column=2)
entry_struct_value = tk.Entry(frame_controls, width=8)
entry_struct_value.grid(row=3, column=3)

tk.Label(frame_controls, text="Struct Flag").grid(row=4, column=0)
entry_flag = tk.Entry(frame_controls, width=8)
entry_flag.grid(row=4, column=1)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(fill="x", padx=10, pady=10)

buttons = [
    ("Write Byte", btn_write_byte),
    ("Read Byte", btn_read_byte),
    ("Write String", btn_write_string),
    ("Read String", btn_read_string),
    ("Dump EEPROM", btn_dump),
    ("Checksum", btn_checksum),
    ("Delete Byte", btn_delete),
    ("Reset EEPROM", btn_reset),
    ("Power Cycle", btn_power_cycle),
    ("Write Struct", btn_write_struct),
    ("Read Struct", btn_read_struct),
    ("Reset Log", reset_log),
]

btn_widgets = []
for i, (text, cmd) in enumerate(buttons):
    b = tk.Button(btn_frame, text=text, width=15, command=cmd)
    b.grid(row=i//4, column=i%4, padx=5, pady=5)
    btn_widgets.append(b)

# Console
console = scrolledtext.ScrolledText(root, state="disabled", height=25)
console.pack(fill="both", padx=10, pady=10, expand=True)

# Configure tag colors
console.tag_config("info", foreground="orange")
console.tag_config("error", foreground="red")
console.tag_config("success", foreground="green")

# ---------- Tooltips ----------
ToolTip(entry_address, "Enter EEPROM address (0-1023)")
ToolTip(entry_value, "Enter a byte value (0-255)")
ToolTip(entry_string, "Enter string to write to EEPROM")
ToolTip(entry_length, "Enter number of bytes to read for string")
ToolTip(entry_id, "Struct ID (0-255)")
ToolTip(entry_struct_value, "Struct value (0-65535)")
ToolTip(entry_flag, "Struct flag (0-255)")

tooltips = [
    ("Write a single byte to the EEPROM", btn_widgets[0]),
    ("Read a byte from the EEPROM", btn_widgets[1]),
    ("Write a string to EEPROM starting at the address", btn_widgets[2]),
    ("Read string from EEPROM of given length", btn_widgets[3]),
    ("Dump entire EEPROM content in hex", btn_widgets[4]),
    ("Calculate EEPROM checksum", btn_widgets[5]),
    ("Delete byte (set to 0xFF) at address", btn_widgets[6]),
    ("Reset entire EEPROM to 0xFF", btn_widgets[7]),
    ("Simulate a power cycle", btn_widgets[8]),
    ("Write structured data to EEPROM", btn_widgets[9]),
    ("Read structured data from EEPROM", btn_widgets[10]),
    ("Clear the console log and log file", btn_widgets[11])
]

for tip_text, btn in tooltips:
    ToolTip(btn, tip_text)

# Initialize EEPROM and log
ensure_eeprom()
log("EEPROM Simulator GUI ready.", "info")

root.mainloop()
