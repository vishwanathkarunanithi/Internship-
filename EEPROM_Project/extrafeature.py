# EEPROM Simulation - Review 5
# Integrated Operations with Logging and Automatic Run

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
    default_text = "We are on a mission"
    default_bytes = [ord(c) for c in default_text]

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

    # Initialize EEPROM with default text + 0xFF padding
    eeprom_data = bytes(default_bytes + [0xFF] * (EEPROM_SIZE - len(default_bytes)))
    with open(EEPROM_FILE, "wb") as f:
        f.write(eeprom_data)

    # Initialize write cycles to zero
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes([0] * EEPROM_SIZE))

    print(f"EEPROM initialized with default text: '{default_text}'")
    log_action(f"EEPROM initialized fresh with default text: '{default_text}'")


def save_write_cycles():
    """Save write-cycle data to file."""
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes(write_cycles))


def dump_eeprom(start=0, length=32):
    """Print and log EEPROM section."""
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(length)
        hex_values = " ".join(f"{b:02X}" for b in data)
        ascii_values = "".join(chr(b) if 32 <= b <= 126 else "." for b in data)
        print(f"EEPROM Dump [{start}-{start+length-1}]:")
        print(f"HEX  : {hex_values}")
        print(f"ASCII: {ascii_values}")
        log_action(f"Dumped EEPROM section {start}-{start+length-1}")


def write_byte(address, value):
    """Write a single byte and track write cycles."""
    if address < 0 or address >= EEPROM_SIZE:
        print("Address out of range!")
        return
    if write_cycles[address] >= MAX_WRITE_CYCLES:
        print(f"Max write cycles reached at address {address}, write ignored.")
        log_action(f"WRITE_IGNORED address={address} value={value:#04X}")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes([value & 0xFF]))
    write_cycles[address] += 1
    save_write_cycles()
    print(f"Wrote {value:#04X} at address {address} (Write cycles: {write_cycles[address]})")
    log_action(f"WRITE address={address} value={value:#04X}")


def read_byte(address):
    """Read a single byte."""
    if address < 0 or address >= EEPROM_SIZE:
        print("Address out of range!")
        return None
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = f.read(1)
        print(f"Read from addr {address}: {data[0]:02X}")
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
    """Write string as bytes."""
    write_bytes(start_address, [ord(c) for c in text])
    log_action(f"WRITE_STRING '{text}' at {start_address}")


def read_string(start_address, length):
    """Read string of given length."""
    byte_list = read_bytes(start_address, length)
    s = "".join(chr(b) for b in byte_list if b is not None)
    log_action(f"READ_STRING '{s}' from {start_address}")
    return s


def compute_checksum(start_address, length):
    """Compute simple checksum (sum modulo 256) for a block."""
    bytes_block = read_bytes(start_address, length)
    checksum = sum(b for b in bytes_block if b is not None) % 256
    print(f"Checksum of block [{start_address}-{start_address+length-1}] = {checksum:02X}")
    log_action(f"CHECKSUM start={start_address} length={length} value={checksum:02X}")
    return checksum


# -------------------------------------------------------------------------
# Automated Operations Run
# -------------------------------------------------------------------------
def run_all_operations():
    print("\n=== EEPROM Operations Completed ===\n")
    init_eeprom()

    # 1. Byte operations
    print("-- Byte Write/Read --")
    write_byte(10, 0x42)
    time.sleep(0.1)
    read_byte(10)

    # 2. String operations
    print("\n-- String Write/Read --")
    write_string(100, "HELLO")
    print("Read string:", read_string(100, 5))

    # 3. Checksum example
    print("\n-- Checksum Demo --")
    compute_checksum(100, 5)

    # 4. Dump section
    print("\n-- EEPROM Dump --")
    dump_eeprom(0, 128)

    log_action("Full EEPROM operations executed successfully")
    print("\n✅ Successfully completed — details logged in eeprom_log.txt")


# -------------------------------------------------------------------------
# Interactive menu or automatic run
# -------------------------------------------------------------------------
if __name__ == "__main__":
    init_eeprom()

    print("\nSelect mode:")
    print("1: Run full EEPROM operations")
    print("2: Open interactive menu")
    mode = input("Enter choice: ").strip()

    if mode == "1":
        run_all_operations()

    else:
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
            print("0: Exit")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                try:
                    addr = int(input("Address (0-1023): "))
                    val = int(input("Value (0-255): "))
                    write_byte(addr, val)
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "2":
                try:
                    addr = int(input("Address (0-1023): "))
                    read_byte(addr)
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "3":
                try:
                    addr = int(input("Start address (0-1023): "))
                    data = input("Comma-separated values: ")
                    byte_list = [int(x.strip()) for x in data.split(",")]
                    write_bytes(addr, byte_list)
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "4":
                try:
                    addr = int(input("Start address (0-1023): "))
                    length = int(input("Length: "))
                    vals = read_bytes(addr, length)
                    print("Read sequence:", [v for v in vals if v is not None])
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "5":
                try:
                    addr = int(input("Start address (0-1023): "))
                    text = input("String to write: ")
                    write_string(addr, text)
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "6":
                try:
                    addr = int(input("Start address (0-1023): "))
                    length = int(input("String length: "))
                    print("Read string:", read_string(addr, length))
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "7":
                try:
                    start = int(input("Start address: "))
                    length = int(input("Length: "))
                    dump_eeprom(start, length)
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "8":
                try:
                    start = int(input("Start address: "))
                    length = int(input("Block length: "))
                    compute_checksum(start, length)
                except ValueError:
                    print("Invalid input! Enter integers only.")

            elif choice == "0":
                print("Exiting EEPROM simulation.")
                break

            else:
                print("Invalid choice! Try again.")
