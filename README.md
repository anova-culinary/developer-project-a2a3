# Original BT/WiFi Anova Precision® Cooker Interface

A command-line utility for controlling the original BT/WiFi Anova Precision® Cooker sous vide devices via Bluetooth Low Energy (BLE). Supports both the 800w (BT-only) model and the 900w (BT+WiFi) model with an interactive command interface.

## Features

- **Multi-Model Support:** Compatible with both 800w (BT-only) and 900w (WiFi-enabled) models
- **Auto-Detection:** Identifies model type and enables model-specific commands
- **BLE Scanning & Connection:** Automatically discovers compatible devices using service UUID
- **Interactive Command Loop:** Provides a REPL interface for continuous device control
- **Comprehensive Command Set:** Control temperature, timer, unit settings, and device status
- **Model-Specific Functions:** Supports clearing alarms and firmware version checks on WiFi models

## Requirements

- Python 3.9 or higher
- [Bleak](https://github.com/hbldh/bleak) library for BLE communication

## Installation

1. **Install Python Dependencies:**
   ```bash
   pip install bleak
   ```

2. **Clone/Download the Repository:**
   ```bash
   git clone https://github.com/yourusername/original-precision-cooker.git
   cd original-precision-cooker
   ```

3. **Run the Script:**
   ```bash
   python original_precision_cooker.py
   ```

## Usage

Run the script to enter interactive mode:

```bash
python original_precision_cooker.py
```

The script will:
1. Scan for compatible devices
2. Connect to the first device found
3. Determine the model (800w or 900w)
4. Display available commands based on your model
5. Enter interactive mode where you can issue commands

### Available Commands

| Command | Description |
|---------|-------------|
| `status` | Get cooker status |
| `read_unit` | Read the current temperature unit (C/F) |
| `set_unit` | Set the temperature unit |
| `set_temp` | Set the target temperature |
| `read_target_temp` | Read the target temperature |
| `read_temp` | Read the current temperature |
| `set_timer` | Set the timer in minutes |
| `read_timer` | Read the current timer value |
| `start_timer` | Start the timer |
| `stop_timer` | Stop the timer |
| `start` | Start cooking (prompts for temperature and timer) |
| `stop` | Stop cooking |
| `beep` | Beep the device |
| `clear_alarm`* | Clear any alarm (WiFi model only) |
| `firmware_version`* | Read the firmware version (WiFi model only) |
| `help` | Show help message |
| `exit` | Disconnect and quit |

\* Only available on 900w (WiFi) models

### Cooking Workflow Example

To start cooking at 65.5°C for 2 hours:
1. Enter `set_unit` (then enter `C` when prompted)
2. Enter `set_temp` (then enter `65.5` when prompted)
3. Enter `set_timer` (then enter `120` when prompted)
4. Enter `start` to start cooking
5. Enter `start_timer` to begin the countdown

Alternatively, use the `start` command which will prompt for temperature and timer, then perform all necessary steps automatically.

## BLE Communication Protocol

- **Service UUID:** `0000ffe0-0000-1000-8000-00805f9b34fb`
- **Characteristic UUID:** `0000ffe1-0000-1000-8000-00805f9b34fb`
- **Command Format:** ASCII strings with trailing carriage return (`\r`)
- **Response Handling:** Accumulates BLE notification chunks until a complete response is received

## Architecture

The code is organized into several components:

- **AnovaCookerClient Class:** Manages BLE connection, notifications, and command/response handling
- **Command Functions:** Provides formatted command strings for all supported operations
- **BLE Scanning:** Discovers compatible devices by service UUID or name
- **Interactive Loop:** Implements the REPL interface with command dispatch
- **Model Detection:** Identifies device model to enable appropriate commands

## Debugging

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Contributions, bug reports, and suggestions are welcome! To contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2025 2025 Anova Applied Electronics, Inc

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
