# EEPROM Simulation - Review 6+
# Integrated Demo with Logging, Automatic Test Run, and String Separator Fix

import time
from datetime import datetime

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024  # 1KB EEPROM
MAX_WRITE_CYCLES = 1000
WRITE_CYCLE_FILE = "write_cycles.bin"
LOG_FILE = "eeprom_log.txt"

write_cycles = [0] * EEPROM_SIZE


def log_action(message):
    """Append log entries with timestamps."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")


def init_eeprom():
    """Initialize EEPROM and write-cycle file if not present, with default text."""
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
        print("EEPROM and write-cycle data loaded.")
        log_action("EEPROM loaded successfully")
        return
    except FileNotFoundError:
        pass

    with open(EEPROM_FILE, "wb") as f:
        default_text = b"We are on a mission"
        f.write(default_text + bytes([0x00]) + bytes([0xFF] * (EEPROM_SIZE - len(default_text) - 1)))
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes([0] * EEPROM_SIZE))
    print(f"EEPROM initialized with default text: 'We are on a mission'")
    log_action("EEPROM initialized fresh with default text: 'We are on a mission'")


def save_write_cycles():
    """Save write-cycle data to file."""
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes(write_cycles))


def dump_eeprom(start=0, length=32):
    """Print and log EEPROM section with separate string detection."""
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(length)

    print(f"EEPROM Dump [{start}-{start+length-1}]:")
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
                print(f"Detected string: '{ascii_buffer}'")
                ascii_buffer = ""
    if ascii_buffer:
        print(f"Detected string: '{ascii_buffer}'")

    log_action(f"Dumped EEPROM section {start}-{start+length-1}")


def write_byte(address, value):
    """Write a single byte and track write cycles."""
    if address < 0 or address >= EEPROM_SIZE:
        print("Address out of range!")
        return
    if write_cycles[address] >= MAX_WRITE_CYCLES:
        print(f"Max write cycles reached at address {address}")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes([value & 0xFF]))
    write_cycles[address] += 1
    save_write_cycles()
    print(f"Wrote {value} (0x{value:02X}) at address {address} (Write cycles: {write_cycles[address]})")
    log_action(f"WRITE address={address} value={value:#04X}")


def read_byte(address):
    """Read a single byte."""
    if address < 0 or address >= EEPROM_SIZE:
        print("Address out of range!")
        return None
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = f.read(1)
        print(f"Address: {address}  Value: {data[0]} (0x{data[0]:02X})")
        log_action(f"READ address={address} value={data[0]:02X}")
        return data[0]


def write_bytes(start_address, data_list):
    """Write multiple bytes sequentially."""
    for offset, val in enumerate(data_list):
        write_byte(start_address + offset, val)
    log_action(f"WRITE_BLOCK start={start_address} length={len(data_list)}")


def read_bytes(start_address, length):
    """Read multiple bytes sequentially."""
    vals = [read_byte(start_address + i) for i in range(length)]
    log_action(f"READ_BLOCK start={start_address} length={length}")
    return vals


def write_string(start_address, text):
    """Write string as bytes and add a 0x00 separator."""
    write_bytes(start_address, [ord(c) for c in text])
    if start_address + len(text) < EEPROM_SIZE:
        write_byte(start_address + len(text), 0x00)  # separator
    log_action(f"WRITE_STRING '{text}' at {start_address}")


def read_string(start_address, length):
    """Read string of given length."""
    byte_list = read_bytes(start_address, length)
    s = "".join(chr(b) for b in byte_list if b is not None and 32 <= b <= 126)
    print(f"Detected string at address {start_address}: '{s}'")
    log_action(f"READ_STRING '{s}' from {start_address}")
    return s


def compute_checksum(start_address, length):
    """Compute simple checksum (sum modulo 256) for a block."""
    bytes_block = read_bytes(start_address, length)
    checksum = sum(b for b in bytes_block if b is not None) % 256
    print(f"Checksum of block [{start_address}-{start_address+length-1}] = {checksum} (0x{checksum:02X})")
    log_action(f"CHECKSUM start={start_address} length={length} value={checksum:02X}")
    return checksum


def reset_log():
    """Reset the log file."""
    with open(LOG_FILE, "w") as f:
        f.write("")
    print("Log file has been reset successfully.")
    log_action("Log file reset")


# -------------------------------------------------------------------------
# Interactive menu
# -------------------------------------------------------------------------
if __name__ == "__main__":
    init_eeprom()

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
            print("Read sequence:", [v for v in vals if v is not None])

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

        elif choice == "0":
            print("Exiting EEPROM simulation.")
            break

        else:
            print("Invalid choice! Try again.")
