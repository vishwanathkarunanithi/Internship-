# EEPROM Simulation - Review 3
# Advanced EEPROM simulation: single-byte, multi-byte, string storage, enhanced dump

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024  # 1KB EEPROM


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
    print(f"✅ EEPROM initialized with size: {EEPROM_SIZE} bytes")


def dump_eeprom(start=0, length=32):
    """Print a portion of EEPROM contents in hex and ASCII."""
    with open(EEPROM_FILE, "rb") as f:
        f.seek(start)
        data = f.read(length)
        hex_values = " ".join(f"{b:02X}" for b in data)
        ascii_values = "".join(chr(b) if 32 <= b <= 126 else "." for b in data)
        print(f"EEPROM Dump [{start}-{start+length-1}]:")
        print(f"HEX  : {hex_values}")
        print(f"ASCII: {ascii_values}")


def write_byte(address, value):
    """Write a single byte at a given EEPROM address."""
    if address < 0 or address >= EEPROM_SIZE:
        print("❌ Address out of range!")
        return
    with open(EEPROM_FILE, "r+b") as f:
        f.seek(address)
        f.write(bytes([value & 0xFF]))
    print(f"✍️  Wrote {value:#04X} at address {address}")


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


def write_bytes(start_address, data_list):
    """Write a sequence of bytes starting at a given address."""
    for offset, val in enumerate(data_list):
        write_byte(start_address + offset, val)


def read_bytes(start_address, length):
    """Read a sequence of bytes starting at a given address."""
    return [read_byte(start_address + i) for i in range(length)]


def write_string(start_address, text):
    """Write a string as bytes into EEPROM."""
    byte_list = [ord(c) for c in text]
    write_bytes(start_address, byte_list)


def read_string(start_address, length):
    """Read a string of given length from EEPROM."""
    byte_list = read_bytes(start_address, length)
    return "".join(chr(b) for b in byte_list if b is not None)


if __name__ == "__main__":
    init_eeprom()

    while True:
        print("\n--- EEPROM Review 3 Menu ---")
        print("1: Write a single byte")
        print("2: Read a single byte")
        print("3: Write multiple bytes")
        print("4: Read multiple bytes")
        print("5: Write a string")
        print("6: Read a string")
        print("7: Dump EEPROM section")
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
            addr = int(input("Enter start address (0-1023): "))
            data = input("Enter comma-separated byte values (0-255): ")
            byte_list = [int(x.strip()) for x in data.split(",")]
            write_bytes(addr, byte_list)

        elif choice == "4":
            addr = int(input("Enter start address (0-1023): "))
            length = int(input("Enter number of bytes to read: "))
            vals = read_bytes(addr, length)
            print("Read sequence:", [v for v in vals if v is not None])

        elif choice == "5":
            addr = int(input("Enter start address (0-1023): "))
            text = input("Enter string to write: ")
            write_string(addr, text)

        elif choice == "6":
            addr = int(input("Enter start address (0-1023): "))
            length = int(input("Enter string length: "))
            result = read_string(addr, length)
            print("Read string:", result)

        elif choice == "7":
            start = int(input("Enter start address: "))
            length = int(input("Enter length: "))
            dump_eeprom(start, length)

        elif choice == "0":
            print("Exiting EEPROM simulation.")
            break

        else:
            print("❌ Invalid choice! Try again.")
