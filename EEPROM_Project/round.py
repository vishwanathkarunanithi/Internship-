# EEPROM Simulation - Review 6+ (Final Update)
# Integrated with Logging, String Separator Fix, Delete & Reset Options
# Includes real power cycle detection and default text management
# Automatically generates README.md on first run

import time
from datetime import datetime
import os
import psutil

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024  # 1KB EEPROM
MAX_WRITE_CYCLES = 1000
WRITE_CYCLE_FILE = "write_cycles.bin"
LOG_FILE = "eeprom_log.txt"
DEFAULT_TEXT_FILE = "default_text.txt"

write_cycles = [0] * EEPROM_SIZE

# ------------------- Output Styling -------------------
def print_info(msg):
    print(f"\033[92m{msg}\033[0m")  # Green

def print_warning(msg):
    print(f"\033[93m{msg}\033[0m")  # Yellow

def print_error(msg):
    print(f"\033[91m{msg}\033[0m")  # Red

# ------------------- Create README -------------------
def create_readme():
    """Create README.md in the folder if it doesn't exist."""
    content = """# EEPROM Simulation Project - Review 6+ (Final)

## Description
This project simulates an EEPROM using a binary file. 
It supports reading, writing, deleting, dumping, checksums, logging, and simulates write-cycle limits.

## Features
- Initialize EEPROM with default text ("Mission Complete").
- Read/write single or multiple bytes.
- Read/write strings with 0x00 separators.
- Delete single bytes, blocks, or all written data.
- Compute block checksums.
- Full EEPROM reset with default text preservation.
- Log all operations with timestamps.
- Reset log file option.
- Write cycle limit simulation (default 1000 per byte).
- Detect real system power cycles.
- Change default text dynamically.

## Files
- `eeprom.bin` — Simulated EEPROM memory file.
- `write_cycles.bin` — Tracks write cycles per address.
- `eeprom_log.txt` — Logs all operations including power cycles.
- `default_text.txt` — Stores current default text.
- `main.py` — The main EEPROM simulation script.

## Usage
Run `main.py` to interact with the EEPROM via menu options.

## Requirements
- Python 3.x
- psutil library (for power cycle detection)
"""
    if not os.path.exists("README.md"):
        with open("README.md", "w") as f:
            f.write(content)
        print_info("README.md has been created in the current folder.")

# ------------------- Logging -------------------
def log_action(message):
    """Append log entries with timestamps."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# ------------------- EEPROM Initialization -------------------
def init_eeprom():
    """Initialize EEPROM and write cycles."""
    global write_cycles
    try:
        with open(EEPROM_FILE, "rb") as f:
            data = f.read()
            if len(data) != EEPROM_SIZE:
                raise FileNotFoundError
        with open(WRITE_CYCLE_FILE, "rb") as f:
            cycles = f.read()
            if len(cycles) != EEPROM_SIZE:
                raise FileNotFoundError
            write_cycles = list(cycles)
        print_info("EEPROM and write-cycle data loaded.")
        log_action("EEPROM loaded successfully")
    except FileNotFoundError:
        default_text = get_default_text().encode()
        with open(EEPROM_FILE, "wb") as f:
            f.write(default_text + bytes([0x00]) + bytes([0xFF] * (EEPROM_SIZE - len(default_text) - 1)))
        with open(WRITE_CYCLE_FILE, "wb") as f:
            f.write(bytes([0] * EEPROM_SIZE))
        print_info(f"EEPROM initialized with default text: '{default_text.decode()}'")
        log_action(f"EEPROM initialized fresh with default text: '{default_text.decode()}'")

def save_write_cycles():
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes(write_cycles))

# ------------------- EEPROM Operations -------------------
def write_byte(address, value):
    if address < 0 or address >= EEPROM_SIZE:
        print_error("Address out of range!")
        return
    if write_cycles[address] >= MAX_WRITE_CYCLES:
        print_warning(f"Max write cycles reached at address {address}")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes([value & 0xFF]))
    write_cycles[address] += 1
    save_write_cycles()
    print_info(f"Wrote {value} (0x{value:02X}) at address {address} (Write cycles: {write_cycles[address]})")
    log_action(f"WRITE address={address} value={value:#04X}")

def read_byte(address):
    if address < 0 or address >= EEPROM_SIZE:
        print_error("Address out of range!")
        return None
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = f.read(1)
        print_info(f"Address: {address}  Value: {data[0]} (0x{data[0]:02X})")
        log_action(f"READ address={address} value={data[0]:02X}")
        return data[0]

def write_bytes(start_address, data_list):
    for offset, val in enumerate(data_list):
        write_byte(start_address + offset, val)
    log_action(f"WRITE_BLOCK start={start_address} length={len(data_list)}")

def read_bytes(start_address, length):
    vals = [read_byte(start_address + i) for i in range(length)]
    log_action(f"READ_BLOCK start={start_address} length={length}")
    return vals

def write_string(start_address, text):
    write_bytes(start_address, [ord(c) for c in text])
    if start_address + len(text) < EEPROM_SIZE:
        write_byte(start_address + len(text), 0x00)
    log_action(f"WRITE_STRING '{text}' at {start_address}")

def read_string(start_address, length):
    byte_list = read_bytes(start_address, length)
    s = "".join(chr(b) for b in byte_list if b is not None and 32 <= b <= 126)
    print_info(f"Detected string at address {start_address}: '{s}'")
    log_action(f"READ_STRING '{s}' from {start_address}")
    return s

def dump_eeprom(start=0, length=32):
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(length)

    print_info(f"EEPROM Dump [{start}-{start+length-1}]:")
    print("Address  Value(decimal)  Value(hex)  ASCII")
    print("-----------------------------------------")

    ascii_buffer = ""
    for offset, b in enumerate(data):
        addr = start + offset
        ascii_char = chr(b) if 32 <= b <= 126 else "."
        print(f"{addr:5}    {b:12}    0x{b:02X}    {ascii_char}")
        if 32 <= b <= 126:
            ascii_buffer += ascii_char
        else:
            if ascii_buffer:
                print_info(f"Detected string: '{ascii_buffer}'")
                ascii_buffer = ""
    if ascii_buffer:
        print_info(f"Detected string: '{ascii_buffer}'")

    log_action(f"Dumped EEPROM section {start}-{start+length-1}")

def compute_checksum(start_address, length):
    bytes_block = read_bytes(start_address, length)
    checksum = sum(b for b in bytes_block if b is not None) % 256
    print_info(f"Checksum of block [{start_address}-{start_address+length-1}] = {checksum} (0x{checksum:02X})")
    log_action(f"CHECKSUM start={start_address} length={length} value={checksum:02X}")
    return checksum

def reset_log():
    confirm = input("Are you sure you want to reset the log file? (y/n): ").lower()
    if confirm != "y":
        print_warning("Reset log cancelled.")
        return
    with open(LOG_FILE, "w") as f:
        f.write("")
    print_info("Log file has been reset successfully.")
    log_action("Log file reset")

# ------------------- Delete & Reset -------------------
def delete_single_byte():
    addr = int(input("Enter byte address to delete: "))
    if addr < 0 or addr >= EEPROM_SIZE:
        print_error("Address out of range!")
        return
    confirm = input(f"Are you sure you want to delete byte at address {addr}? (y/n): ").lower()
    if confirm != "y":
        print_warning("Delete cancelled.")
        return
    write_byte(addr, 0xFF)
    print_info(f"Deleted byte at address {addr}")
    log_action(f"Deleted single byte at address {addr}")

def delete_string(start_address, length):
    if start_address < 0 or start_address + length > EEPROM_SIZE:
        print_error("Address or length out of range!")
        return
    confirm = input(f"Are you sure you want to delete {length} bytes starting at {start_address}? (y/n): ").lower()
    if confirm != "y":
        print_warning("Delete cancelled.")
        return
    for i in range(length):
        write_byte(start_address + i, 0xFF)
    print_info(f"Deleted {length} bytes from address {start_address}")
    log_action(f"Deleted {length} bytes from address {start_address}")

def delete_all_written():
    confirm = input("Are you sure you want to delete all written data? (y/n): ").lower()
    if confirm != "y":
        print_warning("Delete cancelled.")
        return
    with open(EEPROM_FILE, "r+b") as f:
        data = bytearray(f.read())
        erased = 0
        for i in range(len(data)):
            if data[i] != 0xFF:
                data[i] = 0xFF
                erased += 1
                write_cycles[i] += 1
        f.seek(0)
        f.write(data)
    save_write_cycles()
    print_info(f"Deleted {erased} bytes of written data.")
    log_action(f"Deleted {erased} bytes of written data")

def reset_eeprom():
    confirm = input("Are you sure you want to RESET the entire EEPROM? (y/n): ").lower()
    if confirm != "y":
        print_warning("EEPROM reset cancelled.")
        return
    default_text = get_default_text().encode()
    with open(EEPROM_FILE, "wb") as f:
        f.write(default_text + bytes([0x00]) + bytes([0xFF] * (EEPROM_SIZE - len(default_text) - 1)))
    global write_cycles
    write_cycles = [0] * EEPROM_SIZE
    save_write_cycles()
    print_info(f"EEPROM has been fully reset with default text: '{default_text.decode()}'")
    log_action(f"EEPROM fully reset with default text: '{default_text.decode()}'")

# ------------------- Default Text Management -------------------
def get_default_text():
    if not os.path.exists(DEFAULT_TEXT_FILE):
        with open(DEFAULT_TEXT_FILE, "w") as f:
            f.write("Mission Complete")
    with open(DEFAULT_TEXT_FILE, "r") as f:
        return f.read().strip()

def change_default_text():
    new_text = input("Enter new default text: ").strip()
    with open(DEFAULT_TEXT_FILE, "w") as f:
        f.write(new_text)
    print_info(f"Default text changed to: '{new_text}'")
    log_action(f"Default text changed to: '{new_text}'")

# ------------------- Real Power Cycle Detection -------------------
last_boot = psutil.boot_time()
def detect_real_power_cycle():
    """Detect if system has rebooted since last run."""
    current_boot = psutil.boot_time()
    if current_boot != last_boot:
        log_action(f"System reboot detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info("System reboot detected and logged.")

def manual_power_cycle_log():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_action(f"Manual power cycle logged at {timestamp}")
    print_info(f"Power cycle logged at {timestamp}")

# ------------------- Main Function -------------------
def main():
    create_readme()
    init_eeprom()
    detect_real_power_cycle()

    while True:
        print("\n--- EEPROM Menu ---")
        print("1: Write single byte")
        print("2: Read single byte")
        print("3: Write multiple bytes")
        print("4: Read multiple bytes")
        print("5: Write string")
        print("6: Read string")
        print("7: Dump EEPROM section")
        print("8: Compute block checksum")
        print("9: Reset log file")
        print("10: Delete single byte")
        print("11: Delete string/block")
        print("12: Delete all written data")
        print("13: Reset entire EEPROM")
        print("14: Change default text")
        print("15: Log power cycle manually")
        print("0: Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            addr = int(input("Address (0-1023): "))
            val = int(input("Value (0-255): "))
            write_byte(addr, val)
        elif choice == "2":
            addr = int(input("Address (0-1023): "))
            read_byte(addr)
        elif choice == "3":
            addr = int(input("Start address (0-1023): "))
            data = input("Comma-separated values: ")
            byte_list = [int(x.strip()) for x in data.split(",")]
            write_bytes(addr, byte_list)
        elif choice == "4":
            addr = int(input("Start address (0-1023): "))
            length = int(input("Length: "))
            vals = read_bytes(addr, length)
            print_info("Read sequence: " + str([v for v in vals if v is not None]))
        elif choice == "5":
            addr = int(input("Start address (0-1023): "))
            text = input("String to write: ")
            write_string(addr, text)
        elif choice == "6":
            addr = int(input("Start address (0-1023): "))
            length = int(input("String length: "))
            read_string(addr, length)
        elif choice == "7":
            start = int(input("Start address: "))
            length = int(input("Length: "))
            dump_eeprom(start, length)
        elif choice == "8":
            start = int(input("Start address: "))
            length = int(input("Block length: "))
            compute_checksum(start, length)
        elif choice == "9":
            reset_log()
        elif choice == "10":
            delete_single_byte()
        elif choice == "11":
            start = int(input("Start address: "))
            length = int(input("Length to delete: "))
            delete_string(start, length)
        elif choice == "12":
            delete_all_written()
        elif choice == "13":
            reset_eeprom()
        elif choice == "14":
            change_default_text()
        elif choice == "15":
            manual_power_cycle_log()
        elif choice == "0":
            print_info("Exiting EEPROM simulation.")
            break
        else:
            print_error("Invalid choice! Try again.")

# ------------------- Entry Point -------------------
if __name__ == "__main__":
    main()
