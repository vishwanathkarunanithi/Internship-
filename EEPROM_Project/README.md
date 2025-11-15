# EEPROM Simulation Project - Review 6+ (Final)

## Description
This project simulates an EEPROM (Electrically Erasable Programmable Read-Only Memory) using a binary file. 
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
- Power cycle simulation with timestamped logging.

## Files
- `eeprom.bin` — Simulated EEPROM memory file.
- `write_cycles.bin` — Tracks write cycles per address.
- `eeprom_log.txt` — Logs all operations including power cycles.
- `main.py` — The main EEPROM simulation script.

## Usage
1. Run `main.py` to interact with the EEPROM via menu options.

## Requirements
- Python 3.x
- No external libraries required
