import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import time
from datetime import datetime
import ctypes

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024

# ---------- Structure & Union Definition ----------
class DataStruct(ctypes.Structure):
    _fields_ = [("address", ctypes.c_uint16),
                ("value", ctypes.c_uint8),
                ("timestamp", ctypes.c_uint32)]

class DataUnion(ctypes.Union):
    _fields_ = [("data", DataStruct),
                ("raw", ctypes.c_byte * ctypes.sizeof(DataStruct))]

# ---------- EEPROM Functions ----------
def init_eeprom():
    if not os.path.exists(EEPROM_FILE):
        with open(EEPROM_FILE, 'wb') as f:
            f.write(b'\xFF' * EEPROM_SIZE)

init_eeprom()

def log_action(action):
    with open("eeprom_log.txt", 'a') as log:
        log.write(f"{datetime.now()} - {action}\n")

def write_eeprom(addr, val):
    if 0 <= addr < EEPROM_SIZE:
        with open(EEPROM_FILE, 'r+b') as f:
            f.seek(addr)
            f.write(bytes([val]))
        log_action(f"Wrote {val} at {addr}")
    else:
        messagebox.showerror("Error", "Address out of range!")

def read_eeprom(addr):
    if 0 <= addr < EEPROM_SIZE:
        with open(EEPROM_FILE, 'rb') as f:
            f.seek(addr)
            val = ord(f.read(1))
        log_action(f"Read {val} from {addr}")
        return val
    else:
        messagebox.showerror("Error", "Address out of range!")
        return None

def reset_eeprom():
    with open(EEPROM_FILE, 'wb') as f:
        f.write(b'\xFF' * EEPROM_SIZE)
    log_action("EEPROM Reset Completed")
    messagebox.showinfo("Reset", "EEPROM reset done.")

# ---------- Structure Read/Write ----------
def write_structure():
    try:
        addr = int(addr_entry.get())
        val = int(value_entry.get())
        ts = int(time.time())
        du = DataUnion()
        du.data = DataStruct(addr, val, ts)
        packed = bytes(du.raw)

        if addr + len(packed) > EEPROM_SIZE:
            messagebox.showerror("Error", "Structure exceeds EEPROM size!")
            return

        with open(EEPROM_FILE, 'r+b') as f:
            f.seek(addr)
            f.write(packed)
        log_action(f"Structure written at {addr}: value={val}, time={ts}")
        messagebox.showinfo("Success", "Structure written successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def read_structure():
    try:
        addr = int(addr_entry.get())
        du = DataUnion()
        with open(EEPROM_FILE, 'rb') as f:
            f.seek(addr)
            du.raw[:] = f.read(ctypes.sizeof(DataStruct))
        data = du.data
        messagebox.showinfo("Read Struct", f"Address={data.address}\nValue={data.value}\nTimestamp={data.timestamp}")
        log_action(f"Read structure from {addr}: value={data.value}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("EEPROM Control Panel with Structure Access")
root.geometry("500x500")
root.resizable(False, False)

title = ttk.Label(root, text="EEPROM Simulator GUI", font=("Segoe UI", 14, "bold"))
title.pack(pady=10)

frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Address:").grid(row=0, column=0, padx=5, pady=5)
addr_entry = ttk.Entry(frame, width=10)
addr_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Value:").grid(row=1, column=0, padx=5, pady=5)
value_entry = ttk.Entry(frame, width=10)
value_entry.grid(row=1, column=1, padx=5, pady=5)

btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Write Byte", command=lambda: write_eeprom(int(addr_entry.get()), int(value_entry.get()))).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(btn_frame, text="Read Byte", command=lambda: messagebox.showinfo("Value", f"{read_eeprom(int(addr_entry.get()))}")).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(btn_frame, text="Reset EEPROM", command=reset_eeprom).grid(row=0, column=2, padx=5, pady=5)

ttk.Button(btn_frame, text="Write Structure", command=write_structure).grid(row=1, column=0, padx=5, pady=5)
ttk.Button(btn_frame, text="Read Structure", command=read_structure).grid(row=1, column=1, padx=5, pady=5)

ttk.Button(root, text="Exit", command=root.destroy).pack(pady=10)

log_box = scrolledtext.ScrolledText(root, width=60, height=10)
log_box.pack(pady=10)

def refresh_log():
    if os.path.exists("eeprom_log.txt"):
        with open("eeprom_log.txt", 'r') as f:
            log_box.delete(1.0, tk.END)
            log_box.insert(tk.END, f.read())
    root.after(2000, refresh_log)

refresh_log()
root.mainloop()
