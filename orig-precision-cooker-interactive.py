#!/usr/bin/env python3
import asyncio
import logging
import sys
from bleak import BleakScanner, BleakClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# BLE Constants (using the full 128-bit UUIDs)
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Command functions based on your commands.ts file

def CMD_START():
    return "start"

def CMD_STOP():
    return "stop"

def CMD_READ_TARGET_TEMP():
    return "read set temp"

def CMD_READ_TEMP():
    return "read temp"

def CMD_READ_UNIT():
    return "read unit"

def CMD_READ_TIMER():
    return "read timer"

def CMD_START_TIMER():
    return "start time"

def CMD_STOP_TIMER():
    return "stop time"

def CMD_CLEAR_ALARM():
    # Note: clear alarm is only available on the WiFi (900w) model.
    return "clear alarm"

def CMD_FIRMWARE_VERSION():
    return "version"

def CMD_STATUS():
    return "status"

def CMD_SET_TIMER(minutes):
    return f"set timer {minutes}"

def CMD_SET_TEMP(temp):
    return f"set temp {temp}"

def CMD_SET_UNIT(unit):
    return f"set unit {unit.lower()}"

def CMD_GET_COOKER_ID():
    return "get id card"

# BLE Client class
class AnovaCookerClient:
    def __init__(self, address):
        self.address = address
        self.client = BleakClient(address)
        self._response_buffer = bytearray()
        self._response_future = None
        # This attribute will be set after GET_COOKER_ID:
        self.is_wifi_model = False

    async def connect(self):
        logger.info(f"Connecting to device at {self.address} ...")
        await self.client.connect()
        # Start notifications on the RX/TX characteristic.
        await self.client.start_notify(CHAR_UUID, self._notification_handler)
        logger.info("Connected and notifications started.")

    async def disconnect(self):
        logger.info("Disconnecting...")
        try:
            await self.client.stop_notify(CHAR_UUID)
        except Exception as e:
            logger.error(f"Warning: error stopping notifications: {e}")
        await self.client.disconnect()
        logger.info("Disconnected.")

    def _notification_handler(self, sender, data: bytearray):
        """
        Notification callback.
        Data is accumulated until a response chunk less than 20 bytes or ending with 0x0 is seen.
        """
        self._response_buffer.extend(data)
        if (len(data) < 20) or (data[-1] == 0):
            if self._response_future and not self._response_future.done():
                response_str = self._response_buffer.decode("ascii", errors="ignore").strip()
                self._response_future.set_result(response_str)
            self._response_buffer = bytearray()

    async def send_command(self, command: str, timeout: float = 15.0) -> str:
        """
        Sends a command (appends carriage return) and waits for a response.
        """
        full_command = command + "\r"
        data = full_command.encode("ascii")
        loop = asyncio.get_event_loop()
        self._response_future = loop.create_future()
        await self.client.write_gatt_char(CHAR_UUID, data, response=False)
        try:
            response = await asyncio.wait_for(self._response_future, timeout)
        except asyncio.TimeoutError:
            response = "Timeout waiting for response."
        finally:
            self._response_future = None
        return response

async def scan_and_select_device():
    """
    Scan for BLE devices and return the address of the first one that advertises our service.
    """
    logger.info("Scanning for devices...")
    devices = await BleakScanner.discover(timeout=5.0)
    for d in devices:
        uuids = d.metadata.get("uuids", [])
        if SERVICE_UUID.lower() in [u.lower() for u in uuids]:
            logger.info(f"Found device: {d.name} ({d.address}) advertising our service.")
            return d.address
        if d.name and "anova" in d.name.lower():
            logger.info(f"Found device by name: {d.name} ({d.address}).")
            return d.address
    return None

def print_help(is_wifi_model):
    help_text = f"""
Available commands:
  help              Show this help message.
  status            Get cooker status (sends "status").
  read_unit         Read current unit (sends "read unit").
  set_unit          Set temperature unit. You will be prompted for a value (e.g., C or F) (sends "set unit <value>").
  set_temp          Set target temperature. You will be prompted for a value (sends "set temp <value>").
  read_target_temp  Read target temperature (sends "read set temp").
  read_temp         Read current temperature (sends "read temp").
  set_timer         Set timer (in minutes). You will be prompted for a value (sends "set timer <value>").
  read_timer        Read timer value (sends "read timer").
  start_timer       Start the timer (sends "start time").
  stop_timer        Stop the timer (sends "stop time").
"""
    if is_wifi_model:
        help_text += """
  clear_alarm       Clear any alarm (sends "clear alarm").
  firmware_version  Read firmware version (sends "version").
"""
    help_text += """
  start             Start cooking. You will be prompted for target temperature and timer.
                    Sequence:
                      1. "set temp <temp>"
                      2. "stop time"
                      3. "set timer <timer>"
                      4. "start"
                      5. If timer > 0, "start time"
  stop              Stop cooking (sends "stop").
  beep              Beep (sends "stop").
  exit              Disconnect and exit.
"""
    logger.info(help_text)

async def interactive_loop(client: AnovaCookerClient):
    logger.info("\nEntering interactive mode. Type 'help' to see available commands.")
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Command> ")
        cmd = user_input.strip().lower()
        if cmd == "help":
            print_help(client.is_wifi_model)
        elif cmd == "status":
            response = await client.send_command(CMD_STATUS())
            logger.info(f"Response: {response}")
        elif cmd == "read_unit":
            response = await client.send_command(CMD_READ_UNIT())
            logger.info(f"Response: {response}")
        elif cmd == "set_unit":
            unit = await asyncio.get_event_loop().run_in_executor(None, input, "Enter unit (e.g., C or F): ")
            command_str = CMD_SET_UNIT(unit.strip())
            response = await client.send_command(command_str)
            logger.info(f"Response: {response}")
        elif cmd == "set_temp":
            temp = await asyncio.get_event_loop().run_in_executor(None, input, "Enter target temperature: ")
            command_str = CMD_SET_TEMP(temp.strip())
            response = await client.send_command(command_str)
            logger.info(f"Response: {response}")
        elif cmd == "read_target_temp":
            response = await client.send_command(CMD_READ_TARGET_TEMP())
            logger.info(f"Response: {response}")
        elif cmd == "read_temp":
            response = await client.send_command(CMD_READ_TEMP())
            logger.info(f"Response: {response}")
        elif cmd == "set_timer":
            timer = await asyncio.get_event_loop().run_in_executor(None, input, "Enter timer in minutes: ")
            command_str = CMD_SET_TIMER(timer.strip())
            response = await client.send_command(command_str)
            logger.info(f"Response: {response}")
        elif cmd == "read_timer":
            response = await client.send_command(CMD_READ_TIMER())
            logger.info(f"Response: {response}")
        elif cmd == "start_timer":
            response = await client.send_command(CMD_START_TIMER())
            logger.info(f"Response: {response}")
        elif cmd == "stop_timer":
            response = await client.send_command(CMD_STOP_TIMER())
            logger.info(f"Response: {response}")
        elif cmd == "clear_alarm":
            if client.is_wifi_model:
                response = await client.send_command(CMD_CLEAR_ALARM())
                logger.info(f"Response: {response}")
            else:
                logger.info("clear_alarm command is not available on 800w models.")
        elif cmd == "firmware_version":
            if client.is_wifi_model:
                response = await client.send_command(CMD_FIRMWARE_VERSION())
                logger.info(f"Response: {response}")
            else:
                logger.info("firmware_version command is not available on 800w models.")
        elif cmd == "start":
            temp = await asyncio.get_event_loop().run_in_executor(None, input, "Enter target temperature: ")
            timer = await asyncio.get_event_loop().run_in_executor(None, input, "Enter timer in minutes (0 if none): ")
            response = await client.send_command(CMD_SET_TEMP(temp.strip()))
            logger.info(f"SET_TEMP Response: {response}")
            response = await client.send_command(CMD_STOP_TIMER())
            logger.info(f"STOP_TIMER Response: {response}")
            response = await client.send_command(CMD_SET_TIMER(timer.strip()))
            logger.info(f"SET_TIMER Response: {response}")
            response = await client.send_command(CMD_START())
            logger.info(f"START Response: {response}")
            try:
                timer_val = float(timer.strip())
            except ValueError:
                timer_val = 0
            if timer_val > 0:
                response = await client.send_command(CMD_START_TIMER())
                logger.info(f"START_TIMER Response: {response}")
        elif cmd == "stop":
            response = await client.send_command(CMD_STOP())
            logger.info(f"Response: {response}")
        elif cmd == "beep":
            response = await client.send_command(CMD_STOP())
            logger.info(f"Response: {response}")
        elif cmd == "exit":
            logger.info("Exiting interactive mode...")
            break
        elif cmd == "":
            continue
        else:
            logger.info("Unknown command. Type 'help' for a list of commands.")

async def main():
    address = await scan_and_select_device()
    if not address:
        logger.error("No suitable device found. Exiting.")
        sys.exit(1)
    client = AnovaCookerClient(address)
    try:
        await client.connect()
    except Exception as e:
        logger.error(f"Error connecting to device: {e}")
        sys.exit(1)
    try:
        # Send GET_COOKER_ID command to determine model.
        id_response = await client.send_command(CMD_GET_COOKER_ID())
        if id_response.startswith("anova f56-"):
            client.is_wifi_model = True
            logger.info(f"Cooker version: 900w (WiFi model).")
        else:
            client.is_wifi_model = False
            logger.info(f"Cooker version: 800w model.")
        print_help(client.is_wifi_model)
        await interactive_loop(client)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("User interrupted execution. Exiting.")
