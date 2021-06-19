# mcu_cli.py
mcu_cli.py is a simple command-line interface for testing mcu.py.

refer to [the command list](command-list.md) for more details.

### Commands
Forward Commands:
- 0x10 - `mv {motor} {microseconds}`
- 0x12 - `mc {motor} {percent}`
- 0x00 - `test`
- 0x0F - `halt`
- 0x13 - `smc {motor} {calibration}`
- 0x30 - `getimu {device}`
    - devices: accel, gyro, linaccel, orientation
- 0x33 - `sas {range} {divisor}`
- 0x34 - `sgs {range} {divisor}`
- 0x35 - `gic`
- 0x40 - `getvt`
- 0x50 - `sar {device} {on/off} {delay}`
    - devices: accel, gyro, vt, linaccel, orientation
- 0x51 - `sfb {on/off}`

Getter Commands:
- `accel` - returns the latest acceleration data.
- `gyro` - returns the latest gyro data.
- `voltage` - returns the latest voltage.
- `temp` - returns the latest temperature.
- `rpkt {queue}` - retrieves one packet from a queue.
    - queues: test, ok, accel, gyro, vt, linaccel, orientation, motor

Other Commands:
- `echo {msg}`
- `exit` (kinda doesn't work...)
