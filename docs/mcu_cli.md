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
    - 0=test, 1=ok, 2=accel, 3=gyro, 4=vt
