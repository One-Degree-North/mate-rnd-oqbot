# mcu_cli.py
mcu_cli.py is a simple command-line interface for testing mcu.py.

### Commands
Forward Commands:
- `mv {motor} {microseconds}`
- `mc {motor} {percent}`
- `test`
- `halt`
- `smc {motor} {calibration}`
- `getimu {device}`
    - devices: accel, gyro
- `sas {range} {divisor}`
- `sgs {range} {divisor}`
- `getvt`
- `sar {device} {on/off} {delay}`
    - devices: accel, gyro, vt
- `sfb {on/off}`

Getter Commands:
- `accel`
- `gyro`
- `voltage`
- `temp`
- `rpkt {queue}`
    - queues: test, ok, accel, gyro, vt
