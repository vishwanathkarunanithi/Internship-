import os
import time
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

# ------------------- EEPROM CONFIG -------------------
EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024
MAX_WRITE_CYCLES = 1000
WRITE_CYCLE_FILE = "write_cycles.bin"
LOG_FILE = "eeprom_log.txt"

write_cycles = [0] * EEPROM_SIZE

# ------------------- STRUCT / UNION -------------------
class EEPROMStruct(ctypes.Structure):
    _fields_ = [("id", ctypes.c_uint8),
                ("value", ctypes.c_uint16),
                ("flag", ctypes.c_uint8)]

class EEPROMUnion(ctypes.Union):
    _fields_ = [("data", EEPROMStruct),
                ("raw", ctypes.c_ubyte * ctypes.sizeof(EEPROMStruct))]

# ------------------- TOOLTIP -------------------
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
        x, y = self.widget.winfo_rootx()+25, self.widget.winfo_rooty()+20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=3)
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ------------------- EEPROM INITIALIZATION -------------------
def init_eeprom():
    global write_cycles
    if os.path.exists(EEPROM_FILE) and os.path.exists(WRITE_CYCLE_FILE):
        with open(EEPROM_FILE, "rb") as f:
            if len(f.read()) != EEPROM_SIZE:
                raise FileNotFoundError
        with open(WRITE_CYCLE_FILE, "rb") as f:
            write_cycles = list(f.read())
        log("EEPROM loaded successfully.", "info")
    else:
        with open(EEPROM_FILE, "wb") as f:
            default_text = b"Mission Complete"
            f.write(default_text + bytes([0x00]) + bytes([0xFF]*(EEPROM_SIZE-len(default_text)-1)))
        with open(WRITE_CYCLE_FILE, "wb") as f:
            f.write(bytes([0]*EEPROM_SIZE))
        log("EEPROM initialized with default text.", "info")

def save_write_cycles():
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes(write_cycles))

# ------------------- LOGGING -------------------
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

# ------------------- EEPROM OPERATIONS -------------------
def write_byte(address=None, value=None):
    if address is None:
        address = simpledialog.askinteger("Write Byte", f"Enter address (0-{EEPROM_SIZE-1}):")
    if value is None:
        value = simpledialog.askinteger("Write Byte", "Enter value (0-255):")
    if address is None or value is None:
        return
    if not (0 <= address < EEPROM_SIZE):
        log(f"Error: Address {address} out of range.", "error")
        return
    if write_cycles[address] >= MAX_WRITE_CYCLES:
        log(f"Max write cycles reached at address {address}.", "error")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes([value & 0xFF]))
    write_cycles[address] += 1
    save_write_cycles()
    log(f"Wrote {value} (0x{value:02X}) at address {address} (Cycles: {write_cycles[address]})", "success")

def read_byte(address=None):
    if address is None:
        address = simpledialog.askinteger("Read Byte", f"Enter address (0-{EEPROM_SIZE-1}):")
    if address is None:
        return
    if not (0 <= address < EEPROM_SIZE):
        log(f"Error: Address {address} out of range.", "error")
        return
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        val = f.read(1)[0]
    log(f"Address {address}: {val} (0x{val:02X})", "success")
    return val

def write_bytes(start_address=None, byte_list=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Write Multiple Bytes", f"Enter start address (0-{EEPROM_SIZE-1}):")
    if byte_list is None:
        data_str = simpledialog.askstring("Write Multiple Bytes", "Enter comma-separated byte values (0-255):")
        if data_str is None:
            return
        try:
            byte_list = [int(x.strip()) for x in data_str.split(",")]
        except:
            log("Invalid input for multiple bytes.", "error")
            return
    for offset, val in enumerate(byte_list):
        write_byte(start_address + offset, val)
    log(f"Wrote {len(byte_list)} bytes starting at {start_address}.", "success")

def read_bytes(start_address=None, length=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Read Multiple Bytes", f"Enter start address (0-{EEPROM_SIZE-1}):")
    if length is None:
        length = simpledialog.askinteger("Read Multiple Bytes", "Enter number of bytes to read:")
    if start_address is None or length is None:
        return
    vals = []
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start_address)
        vals = list(f.read(length))
    # Print in formatted way
    console.config(state='normal')
    console.insert("end", f"EEPROM Dump [{start_address}-{start_address+length-1}]:\n", "info")
    console.insert("end", "Addr  Dec   Hex   ASCII  WriteCycles\n")
    console.insert("end", "----------------------------------\n")
    ascii_buf = ""
    for i, b in enumerate(vals):
        addr = start_address + i
        ascii_ch = chr(b) if 32 <= b <= 126 else "."
        console.insert("end", f"{addr:04}  {b:3}  0x{b:02X}   {ascii_ch}       {write_cycles[addr]}\n")
        if 32 <= b <= 126:
            ascii_buf += ascii_ch
        else:
            if ascii_buf:
                console.insert("end", f"Detected string: '{ascii_buf}'\n")
                ascii_buf = ""
    if ascii_buf:
        console.insert("end", f"Detected string: '{ascii_buf}'\n")
    console.config(state='disabled')
    log(f"Read {length} bytes starting at {start_address}.", "success")
    return vals

def write_string(start_address=None, text=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Write String", f"Enter start address (0-{EEPROM_SIZE-1}):")
    if text is None:
        text = simpledialog.askstring("Write String", "Enter string to write:")
    if start_address is None or text is None:
        return
    bytes_list = [ord(c) for c in text]
    write_bytes(start_address, bytes_list)
    # Add null terminator if possible
    if start_address + len(bytes_list) < EEPROM_SIZE:
        write_byte(start_address + len(bytes_list), 0x00)
    log(f"String '{text}' written at address {start_address}.", "success")

def read_string(start_address=None, length=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Read String", f"Enter start address (0-{EEPROM_SIZE-1}):")
    if length is None:
        length = simpledialog.askinteger("Read String", "Enter string length:")
    if start_address is None or length is None:
        return
    byte_list = read_bytes(start_address, length)
    if byte_list is None:
        return
    s = "".join(chr(b) for b in byte_list if 32 <= b <= 126)
    log(f"String read at address {start_address}: '{s}'", "success")
    return s

def delete_byte(address=None):
    if address is None:
        address = simpledialog.askinteger("Delete Byte", f"Enter address (0-{EEPROM_SIZE-1}):")
    if address is None:
        return
    write_byte(address, 0xFF)
    log(f"Deleted byte at address {address}", "success")

def delete_bytes(start_address=None, length=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Delete Bytes", f"Enter start address (0-{EEPROM_SIZE-1}):")
    if length is None:
        length = simpledialog.askinteger("Delete Bytes", "Enter length:")
    if start_address is None or length is None:
        return
    for i in range(length):
        write_byte(start_address + i, 0xFF)
    log(f"Deleted {length} bytes starting at {start_address}", "success")

def reset_eeprom():
    write_bytes(0, [0xFF]*EEPROM_SIZE)
    log("EEPROM fully reset.", "success")

def power_cycle():
    log("Simulating power cycle...", "info")
    time.sleep(0.5)
    log("Power cycle complete.", "success")

def write_struct(start_address=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Struct Write", f"Enter start address (0-{EEPROM_SIZE-1}):")
    sid = simpledialog.askinteger("Struct Write", "Enter Struct ID (0-255):")
    sval = simpledialog.askinteger("Struct Write", "Enter Struct Value (0-65535):")
    sflag = simpledialog.askinteger("Struct Write", "Enter Struct Flag (0-255):")
    if None in (start_address, sid, sval, sflag):
        return
    s = EEPROMStruct(sid, sval, sflag)
    u = EEPROMUnion()
    u.data = s
    write_bytes(start_address, list(u.raw))
    log(f"Struct written at {start_address}: id={sid}, value={sval}, flag={sflag}", "success")

def read_struct(start_address=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Struct Read", f"Enter start address (0-{EEPROM_SIZE-1}):")
    if start_address is None:
        return
    u = EEPROMUnion()
    raw_data = read_bytes(start_address, ctypes.sizeof(u))
    if raw_data is None:
        return
    for i in range(len(raw_data)):
        u.raw[i] = raw_data[i]
    log(f"Struct read at {start_address}: id={u.data.id}, value={u.data.value}, flag={u.data.flag}", "success")
    return u.data

def compute_checksum(start_address=None, length=None):
    if start_address is None:
        start_address = simpledialog.askinteger("Checksum", f"Enter start address (0-{EEPROM_SIZE-1}):")
    if length is None:
        length = simpledialog.askinteger("Checksum", "Enter block length:")
    if start_address is None or length is None:
        return
    vals = read_bytes(start_address, length)
    if vals is None:
        return
    chksum = sum(vals) % 256
    log(f"Checksum of block [{start_address}-{start_address+length-1}]: {chksum}", "info")
    return chksum

def exit_gui():
    log("Exiting EEPROM GUI.", "info")
    root.destroy()

# ------------------- GUI -------------------
root = tk.Tk()
root.title("EEPROM Simulator GUI")
root.geometry("950x750")

btn_frame = tk.Frame(root)
btn_frame.pack(fill="x", padx=10, pady=10)

buttons = [
    ("Write Byte", write_byte),
    ("Read Byte", read_byte),
    ("Write Multiple Bytes", write_bytes),
    ("Read Multiple Bytes", read_bytes),
    ("Write String", write_string),
    ("Read String", read_string),
    ("Dump EEPROM Section", lambda: read_bytes()),
    ("Compute Block Checksum", compute_checksum),
    ("Reset Log File", reset_log),
    ("Delete Byte", delete_byte),
    ("Delete Bytes", delete_bytes),
    ("Delete All Written Data", lambda: delete_bytes(0, EEPROM_SIZE)),
    ("Reset EEPROM", reset_eeprom),
    ("Simulate Power Cycle", power_cycle),
    ("Struct Write", write_struct),
    ("Struct Read", read_struct),
    ("Exit", exit_gui)
]

for i, (text, cmd) in enumerate(buttons):
    b = tk.Button(btn_frame, text=text, width=25, command=cmd)
    b.grid(row=i//3, column=i%3, padx=5, pady=5)

console = scrolledtext.ScrolledText(root, state="disabled", height=30)
console.pack(fill="both", padx=10, pady=10, expand=True)
console.tag_config("info", foreground="orange")
console.tag_config("error", foreground="red")
console.tag_config("success", foreground="green")

# Initialize EEPROM
init_eeprom()
log("EEPROM Simulator GUI ready.", "info")
root.mainloop()
