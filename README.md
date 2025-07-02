<img src="https://developer.anovaculinary.com/img/logo.svg" alt="Anova Developers" width="350"/>

# Original BT/WiFi Anova Precision® Cooker

A command-line utility for controlling the original BT/WiFi Anova Precision® Cooker sous vide devices via Bluetooth Low Energy (BLE). This utility supports both BT-only 800w models and the BT+WiFi-enabled 900w model, providing an interactive command loop to send various commands and receive responses from the cooker.

<img src="https://developer.anovaculinary.com/img/Anova_Precision_Cooker_A2A3.jpg" alt="Anova Developers" width="271"/>

## Features

- **BLE Scanning & Connection:** Automatically scans for devices advertising the specified service UUID
- **Interactive Command Loop:** Provides a REPL interface where you can issue commands until you type `exit`
- **Multi-Model Support:** Detects whether the connected cooker is the 800w or 900w model and enables model-specific commands accordingly
- **Comprehensive Command Set:** Supports commands for starting/stopping cooking, reading temperatures, setting timers, and more
- **Robust Response Handling:** Accumulates response chunks from BLE notifications until a complete response is received

## Requirements

- Python 3.9 or higher
- [Bleak](https://github.com/hbldh/bleak) library for BLE communication

## Installation

1. **Install Python Dependencies:**
   ```bash
   pip install bleak
   ```

2. **Download the Script:**
   Clone or download the repository containing the CLI utility file.

3. **Run the Script:**
   Execute the script directly to start in interactive mode:
   ```bash
   python original_precision_cooker.py
   ```

## Architecture & Code Structure

The code is organized into the following sections:

- **BLE Constants & Command Functions:**
  - Defines the service UUID and characteristic UUID used for BLE communication
  - Implements simple command functions (e.g., `CMD_START`, `CMD_STOP`) that return command strings

- **AnovaCookerClient Class:**
  - Manages BLE connection to the cooker
  - Starts notifications on the designated characteristic and handles responses
  - Provides a method (`send_command`) to send a command (with a carriage return appended) and wait for a response
  - Determines the model (800w or 900w) by sending the `CMD_GET_COOKER_ID` command

- **Interactive Command Loop:**
  - Runs a REPL interface where the user can enter commands
  - Dispatches commands to the cooker and logs the responses
  - Provides model-specific help based on whether the cooker is a WiFi (900w) model

- **BLE Device Scanning:**
  - Scans for BLE devices advertising the specified service UUID or containing "anova" in their name
  - Selects the first matching device and returns its address

## BLE Communication Protocol

- **Device Pairing:**
  - Pairing occurs automatically on power up (or reboot) of the cooker
  - The device becomes discoverable and ready for BLE connection during startup

- **Service & Characteristic UUIDs:**
  - **Service UUID:** `0000ffe0-0000-1000-8000-00805f9b34fb`
  - **Characteristic UUID:** `0000ffe1-0000-1000-8000-00805f9b34fb`

- **Command Transmission:**
  - Commands are sent as ASCII strings with a trailing carriage return (`\r`)
  - The client writes data to the characteristic without waiting for an immediate response

- **Response Handling:**
  - BLE notifications are used to receive responses
  - The response is accumulated until a chunk less than 20 bytes is received or it ends with a `0x0` byte
  - The response is then decoded from ASCII and returned to the caller

## Interactive Usage

To start the interactive REPL, simply run the script:

```bash
python original_precision_cooker.py
```

After connecting, you'll see a help message listing all available commands. You can enter commands such as `status`, `set_temp`, `set_timer`, etc., and view the responses directly in the terminal. Type `exit` to disconnect and quit the interactive mode.

## Subcommands Overview

Below is a table of available commands for the interactive mode:

| Command | Description |
| --- | --- |
| **help** | Show this help message. |
| **status** | Get cooker status (sends `"status"`). |
| **read_unit** | Read the current temperature unit (sends `"read unit"`). |
| **set_unit** | Set the temperature unit. You will be prompted for a value (e.g., C or F) (sends `"set unit <value>"`). |
| **set_temp** | Set the target temperature. You will be prompted for a value (sends `"set temp <value>"`). |
| **read_target_temp** | Read the target temperature (sends `"read set temp"`). |
| **read_temp** | Read the current temperature (sends `"read temp"`). |
| **set_timer** | Set the timer in minutes. You will be prompted for a value (sends `"set timer <value>"`). |
| **read_timer** | Read the current timer value (sends `"read timer"`). |
| **start_timer** | Start the timer (sends `"start time"`). |
| **stop_timer** | Stop the timer (sends `"stop time"`). |
| **clear_alarm** | Clear any alarm (sends `"clear alarm"`) – *only available on the WiFi (900w) model*. |
| **firmware_version** | Read the firmware version (sends `"version"`) – *only available on the WiFi (900w) model*. |
| **start** | Start cooking. Prompts for target temperature and timer. Executes a sequence: set temperature, stop timer, set timer, start cooking, and (if timer > 0) start timer. |
| **stop** | Stop cooking (sends `"stop"`). |
| **beep** | Beep (sends `"stop"` as a placeholder command). |
| **exit** | Disconnect from the device and exit the interactive mode. |

## API Reference

### Core Classes & Functions

### `AnovaCookerClient`

Handles the BLE connection and communication with the cooker.

- **Attributes:**
  - `address`: The BLE address of the cooker.
  - `client`: Instance of `BleakClient` used for BLE communication.
  - `is_wifi_model`: Boolean flag indicating if the connected cooker is a WiFi (900w) model.
- **Methods:**
  - `connect()`: Connects to the device and starts BLE notifications.
  - `disconnect()`: Stops notifications and disconnects from the device.
  - `_notification_handler(sender, data)`: Callback for BLE notifications that accumulates data until a complete response is received.
  - `send_command(command: str, timeout: float = 15.0) -> str`: Sends a command (appending a carriage return) and waits for a response.

### Command Functions

These functions return command strings to be sent to the cooker:

- `CMD_START()`
- `CMD_STOP()`
- `CMD_READ_TARGET_TEMP()`
- `CMD_READ_TEMP()`
- `CMD_READ_UNIT()`
- `CMD_READ_TIMER()`
- `CMD_START_TIMER()`
- `CMD_STOP_TIMER()`
- `CMD_CLEAR_ALARM()` *Note: Available only on WiFi (900w) models.*
- `CMD_FIRMWARE_VERSION()` *Note: Available only on WiFi (900w) models.*
- `CMD_STATUS()`
- `CMD_SET_TIMER(minutes)`
- `CMD_SET_TEMP(temp)`
- `CMD_SET_UNIT(unit)`
- `CMD_GET_COOKER_ID()`

### Helper Functions

- `scan_and_select_device() -> str`: Scans for BLE devices and returns the address of the first device advertising the specified service.
- `print_help(is_wifi_model)`: Displays the available commands and model-specific options.
- `interactive_loop(client: AnovaCookerClient)`: Runs the interactive REPL for sending commands and displaying responses.

## Logging & Debugging

The script uses Python's built-in `logging` module to output status messages and errors. The logging level is set to `INFO` by default. For more verbose output, adjust the logging configuration:

```python
logging.basicConfig(level=logging.DEBUG)
```

Logs include information on device scanning, connection status, command dispatch, and error messages.

## License

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2025 Anova Applied Electronics, Inc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

For more information on this license, please see [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT).
