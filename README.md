# mate-rnd-oqbot
This is the repository containing all the code for One Degree North Robotics's ROV for the 2021 MATE Ranger competition.

## Directory
- `controls_pygame` - original pygame version of control GUI. no longer working. deprecated.
- `controls_pyqt` - new PyQt5 version of the control GUI.
	- `gui.py` - main GUI script.
	- `key_signal.py` - helper script containing key signal class.
	- `exit_program.py` - program exit and cleanup
- `docs`
	- `command-list.md` - list of commands that can be sent between the microcontroller and control station.
	- `packet-structure.md` - document detailing how packets work and how they are sent in communications.
	- `mcu_cli.md` - list of commands for `mcu_cli.py`
- `mcu-code`
	- `mcu-code.ino` - contains all microcontroller-side code. 
- `mcu_lib`
	- `mcu.py` - main script containing the `MCUInterface` class.
	- `command_constants.py` - various constants to import. 
	- `packets.py` - script containing packet classes representing each type of return packet, as well as generic
- `mcu_tests`
	- `multi-sensor-test/multi-sensor-test.ino` - test ICM20649. outdated
	- `multi-serial-test/multi-serial-test.ino` - test multiple serial channels, including debug, on M0+-type chips
	- `pwm-test/pwm-test.ino` - test one PWM motor.
- `comms.py` - communication layer interface between a GUI and `mcu.py`.
- `main.py` - main script, to be run by the user.
- `mcu_cli.py` - command line tool for manually sending commands to `mcu.py`. see `docs/mcu_cli.md`.

## Dependencies
#### Python 3.9+ (`pip`)
- PyQt5 (should also work with PySide2/PySide6/PyQt6)
- PySerial v3.0+
#### Arduino 1.8.10+
- Arduino SAMD
- Adafruit's Board Manager URL (`https://adafruit.github.io/arduino-board-index/package_adafruit_index.json`)
	- Adafruit SAMD
- On Linux, make sure you have `arm-none-eabi-gcc` working

## Instructions
Clone the repo:
```bash
git clone https://github.com/One-Degree-North/mate-rnd-oqbot
cd mate-rnd-oqbot
```
Install dependencies, if needed:
```bash
python3.9 -m pip install PyQt5 pyserial
```
On Linux, allow read/write/execute access on the `tty` port that you want to use:
```bash
# replace X with the one you're using (usually 0)
sudo chmod a+rwx /dev/ttyUSBX
```
Run the script:
```bash
python3.9 main.py
```
## Resources
- [System integration diagram](https://drive.google.com/file/d/1JZqKvZUZwccuLYaYtTmzM63PLmp5iuI3/view?usp=sharing)
- Technical Paper (soon)

## Credits
- **Team Developers**
	- Jefferson Zhang (lutet88)
	- Ayam Babu (ayambabu23)
	- Liam Kelly (fillnye)
	- Nitya Arora (arora767287)
- **Other team contributors**
	-	Ming Jin Yong
	-	Emilio Orcullo
