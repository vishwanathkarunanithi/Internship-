# ============================================================
# EEPROM Simulation with STRUCT and UNION Support
# ------------------------------------------------------------
# - EEPROM Simulation (1KB)
# - Logging, Reset, Delete, Checksum
# - Structure & Union Simulation (like Embedded C)
# ============================================================

import os
import struct
import time
from datetime import datetime

EEPROM_FILE = "eeprom.bin"
EEPROM_SIZE = 1024
LOG_FILE = "eeprom_log.txt"


# ============================================================
# Logger Class
# ============================================================
class Logger:
    @staticmethod
    def log(message):
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")


# ============================================================
# STRUCT and UNION Simulation
# ============================================================

# Example C-like Structure:
# struct SensorData {
#     uint16_t id;
#     float temperature;
#     float humidity;
# };

# Simulated with Python struct format: <Hff
# < = little endian, H = unsigned short, f = float
class SensorData:
    def __init__(self, sensor_id=0, temperature=0.0, humidity=0.0):
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.humidity = humidity

    def pack(self):
        """Convert structure to bytes."""
        return struct.pack("<Hff", self.sensor_id, self.temperature, self.humidity)

    @classmethod
    def unpack(cls, data):
        """Convert bytes back to structure."""
        sensor_id, temperature, humidity = struct.unpack("<Hff", data)
        return cls(sensor_id, temperature, humidity)


# Example UNION Simulation
# union DataUnion {
#     uint32_t raw;
#     float f;
# };
class DataUnion:
    """Simulates a C-style union between a 32-bit integer and float."""
    def __init__(self, value=0):
        self.value = value

    def as_float(self):
        """Interpret the 4 bytes as float."""
        return struct.unpack("<f", struct.pack("<I", self.value))[0]

    def as_int(self):
        """Interpret the float value as integer bits."""
        return struct.unpack("<I", struct.pack("<f", self.value))[0]


# ============================================================
# EEPROM Simulation
# ============================================================
class EEPROM:
    def __init__(self, size=EEPROM_SIZE):
        self.size = size
        if not os.path.exists(EEPROM_FILE):
            with open(EEPROM_FILE, "wb") as f:
                f.write(b'\xFF' * size)
            Logger.log("EEPROM initialized")
        print("EEPROM Ready")

    def write_bytes(self, address, data: bytes):
        if address + len(data) > self.size:
            raise ValueError("Write out of range")
        with open(EEPROM_FILE, "r+b") as f:
            f.seek(address)
            f.write(data)
        Logger.log(f"Wrote {len(data)} bytes at {address}")

    def read_bytes(self, address, length):
        if address + length > self.size:
            raise ValueError("Read out of range")
        with open(EEPROM_FILE, "rb") as f:
            f.seek(address)
            data = f.read(length)
        Logger.log(f"Read {length} bytes at {address}")
        return data

    def dump(self, start=0, length=64):
        with open(EEPROM_FILE, "rb") as f:
            f.seek(start)
            data = f.read(length)
        print(f"\nEEPROM Dump [{start}–{start+length-1}]")
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_chunk = ' '.join(f'{b:02X}' for b in chunk)
            ascii_chunk = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            print(f"{start+i:04X}: {hex_chunk:<48}  {ascii_chunk}")


# ============================================================
# Demo of STRUCT & UNION
# ============================================================
def demo_struct_union():
    eeprom = EEPROM()

    # ---------- STRUCT DEMO ----------
    sensor = SensorData(sensor_id=123, temperature=36.5, humidity=78.2)
    packed_data = sensor.pack()
    eeprom.write_bytes(0, packed_data)

    # Read back and unpack
    read_data = eeprom.read_bytes(0, struct.calcsize("<Hff"))
    sensor2 = SensorData.unpack(read_data)
    print("\n[STRUCT DEMO]")
    print(f"Sensor ID: {sensor2.sensor_id}")
    print(f"Temperature: {sensor2.temperature}")
    print(f"Humidity: {sensor2.humidity}")

    # ---------- UNION DEMO ----------
    union_val = DataUnion(0x42C80000)  # raw bits for 100.0 float
    print("\n[UNION DEMO]")
    print(f"As Integer: {union_val.value}")
    print(f"As Float: {union_val.as_float()}")

    union2 = DataUnion()
    union2.value = union_val.as_int()
    print(f"As Re-Converted Integer: {union2.value}")


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    demo_struct_union()
