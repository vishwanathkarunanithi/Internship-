# EEPROM Simulation - Day 1
# Description: Initialize a 1KB EEPROM file with 0xFF and display its contents.

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024   # 1KB EEPROM


def init_eeprom():
    """Initialize EEPROM file with 0xFF if not already created."""
    try:
        with open(EEPROM_FILE, "rb") as f:
            data = f.read()
            if len(data) == EEPROM_SIZE:
                print("✅ EEPROM already initialized.")
                return
    except FileNotFoundError:
        pass

    # Create fresh EEPROM file
    with open(EEPROM_FILE, "wb") as f:
        f.write(bytes([0xFF] * EEPROM_SIZE))
    print("✅ EEPROM initialized with size:", EEPROM_SIZE, "bytes")


def dump_eeprom(start=0, length=32):
    """Print a small portion of EEPROM contents for checking."""
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(length)
        print("EEPROM Dump:", " ".join(f"{b:02X}" for b in data))


if __name__ == "__main__":
    init_eeprom()
    dump_eeprom(0, 32)
