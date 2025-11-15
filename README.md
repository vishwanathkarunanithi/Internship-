# Internship-
won.py is the final output
all the files in the repository is only for references where we have made many changes in each level.
# EEPROM Simulation Project

This repository contains the developmental phases and final product for an **EEPROM (Electrically Erasable Programmable Read-Only Memory) Simulation**. This project was developed as part of an internship at **One Yes Info Tech Solutions**.

## Overview

The primary goal of this project is to model and simulate the behavior of an EEPROM chip using **Python**. The simulation covers the fundamental operations of an EEPROM, such as memory addressing, data writing, and data reading, all implemented in software.

This repository is unique because it doesn't just contain the final code. Instead, it includes all the intermediate development files (`.py` scripts), allowing you to trace the project's evolution from a simple concept to a complete, merged product.

---

## Repository Structure

This project was built in an incremental, phased approach. The repository contains over 20 distinct Python files, where each file represents a specific stage or feature addition in the development process.

* **Initial Phases:** Files like `phase_01.py`, `phase_02.py`, etc., represent the initial building blocks and basic logic.
* **Incremental Features:** Later files incrementally add complexity, such as improved addressing logic, write-protect mechanisms, or control signal handling.
* **Final Product:** The file named `[won.py]` represents the final, merged product. It combines all the features and logic from the previous phases into a single, comprehensive EEPROM model.

This structure is intended to showcase the iterative development process and provide a clear history of how the final simulation was built.

---

## Key Features (Final Model)

The final Python-based EEPROM model simulates the following core functionalities:

* **Memory Array:** A Python data structure (like a list, dictionary, or bytearray) representing the memory block.
* **Address Decoding:** Logic to select a specific memory location based on an address input.
* **Write Operation:** A function to simulate writing a byte/word of data to a selected address.
* **Read Operation:** A function to simulate retrieving the data from a selected address.
* **Control Logic:** Simulates the response to key control signals (e.g., `Chip Enable`, `Write Enable`) through function parameters or class methods.

*(Feel free to add any other specific features you implemented, like page write, erase cycles, or busy flags.)*

---

## Technologies Used

* **Core Language:** **Python 3.x**
* **Libraries:** [e.g., NumPy (if used for memory array), Pytest (if used for testing), or "None" if it's pure Python]

---

## How to Use

To run this simulation, you will need Python installed on your system.

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_GITHUB_REPOSITORY_URL]
    ```
2.  **Navigate to the directory:**
    ```bash
    cd [YOUR_REPOSITORY_NAME]
    ```
3.  **Run the Final Simulation:**
    Execute the main script. You may also need to run a test script that demonstrates the functionality.
    ```bash
    python [FINAL_FILE_NAME.py]
    ```
    *or, if you have a separate test script:*
    ```bash
    python [YOUR_TEST_SCRIPT.py]
    ```

---

## Author

* **Vishwanath Karunanithi**

This project was developed under the guidance and mentorship provided by **One Yes Info Tech Solutions** during my internship program.
