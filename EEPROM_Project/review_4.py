# EEPROM Simulation - Review 4
# Advanced EEPROM: block operations, checksum, write-cycle simulation

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024  # 1KB EEPROM
MAX_WRITE_CYCLES = 1000  # Simulate limited EEPROM write cycles
WRITE_CYCLE_FILE = "write_cycles.bin"

# Initialize write cycles for each address
write_cycles = [0] * EEPROM_SIZE


def init_eeprom():
    """Initialize EEPROM file and write-cycle file if not present."""
    try:
        with open(EEPROM_FILE, "rb") as f:
            data = f.read()
            if len(data) != EEPROM_SIZE:
                raise FileNotFoundError
        with open(WRITE_CYCLE_FILE, "rb") as f:
            cycles = f.read()
            if len(cycles) != EEPROM_SIZE:
                raise FileNotFoundError
            global write_cycles
            write_cycles = list(cycles)
        print("EEPROM and write-cycle data loaded.")
        return
    except FileNotFoundError:
        pass

    # Create fresh EEPROM file
    with open(EEPROM_FILE, "wb") as f:
        f.write(bytes([0xFF] * EEPROM_SIZE))
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes([0] * EEPROM_SIZE))
    print(f"EEPROM initialized with size: {EEPROM_SIZE} bytes")


def save_write_cycles():
    """Save the write cycle data to file."""
    with open(WRITE_CYCLE_FILE, "wb") as f:
        f.write(bytes(write_cycles))


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
    print(f"Wrote {value:#04X} at address {address} (Write cycles: {write_cycles[address]})")


def read_byte(address):
    """Read a single byte from a given EEPROM address."""
    if address < 0 or address >= EEPROM_SIZE:
        print("Address out of range!")
        return None
    with open(EEPROM_FILE, "rb") as f:
        f.seek(address)
        data = f.read(1)
        print(f"Read from addr {address}: {data[0]:02X}")
        return data[0]


def write_bytes(start_address, data_list):
    """Write multiple bytes sequentially."""
    for offset, val in enumerate(data_list):
        write_byte(start_address + offset, val)


def read_bytes(start_address, length):
    """Read multiple bytes sequentially."""
    return [read_byte(start_address + i) for i in range(length)]


def write_string(start_address, text):
    """Write string as bytes."""
    write_bytes(start_address, [ord(c) for c in text])


def read_string(start_address, length):
    """Read string of given length."""
    byte_list = read_bytes(start_address, length)
    return "".join(chr(b) for b in byte_list if b is not None)


def compute_checksum(start_address, length):
    """Compute simple checksum (sum modulo 256) for a block."""
    bytes_block = read_bytes(start_address, length)
    checksum = sum(b for b in bytes_block if b is not None) % 256
    print(f"Checksum of block [{start_address}-{start_address+length-1}] = {checksum:02X}")
    return checksum


if __name__ == "__main__":
    init_eeprom()

    while True:
        print("\n--- EEPROM Review 4 Menu ---")
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

        elif choice == "8":
            start = int(input("Enter start address: "))
            length = int(input("Enter block length: "))
            compute_checksum(start, length)

        elif choice == "0":
            print("Exiting EEPROM simulation.")
            break

        else:
            print("Invalid choice! Try again.")
