# EEPROM Simulation - Interactive Version
# Description: Write/read bytes interactively, dump contents, test persistence.

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

    with open(EEPROM_FILE, "wb") as f:
        f.write(bytes([0xFF] * EEPROM_SIZE))
    print("✅ EEPROM initialized with size:", EEPROM_SIZE, "bytes")


def dump_eeprom(start=0, length=32):
    """Print a small portion of EEPROM contents for checking."""
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(length)
        print("EEPROM Dump:", " ".join(f"{b:02X}" for b in data))


def write_byte(address, value):
    """Write a single byte at a given EEPROM address."""
    if address < 0 or address >= EEPROM_SIZE:
        print("❌ Address out of range!")
        return

    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes([value & 0xFF]))

    print(f"✍️  Wrote {value:#04x} at address {address}")


def read_byte(address):
    """Read a single byte from a given EEPROM address."""
    if address < 0 or address >= EEPROM_SIZE:
        print("❌ Address out of range!")
        return None

    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = f.read(1)
        print(f"📖 Read from addr {address}: {data[0]:02X}")
        return data[0]


if __name__ == "__main__":
    init_eeprom()

    while True:
        print("\n--- EEPROM Menu ---")
        print("1: Write a byte")
        print("2: Read a byte")
        print("3: Dump EEPROM section")
        print("0: Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            addr = int(input("Enter address (0-1023): "))
            val = int(input("Enter value (0-255): "))
            write_byte(addr, val)
        elif choice == "2":
            addr = int(input("Enter address (0-1023): "))
            read_byte(addr)
        elif choice == "3":
            start = int(input("Enter start address: "))
            length = int(input("Enter length: "))
            dump_eeprom(start, length)
        elif choice == "0":
            print("Exiting EEPROM simulation.")
            break
        else:
            print("❌ Invalid choice! Try again.")
