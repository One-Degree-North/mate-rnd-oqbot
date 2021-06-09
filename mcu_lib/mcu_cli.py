# mcu_cli.py
# a simple low-effort command-line interface for mcu.py.
# refer to docs/mcu_cli.md for usage details.


from mcu import *


print("mcu_cli.py | simple mcu.py interface\nrefer to docs/mcu_cli.md for usage details.")
mcu = MCUInterface(input("enter port: "), int(input("enter baudrate: ")))
mcu.open_serial()

while True:
    user_input = input(f"[{mcu.get_port()}@{mcu.get_baud()}]: ").split(" ")
    try:
        cmd = user_input[0]
        if cmd == "mv":
            motor = int(user_input[1])
            microseconds = int(user_input[2])
            mcu.cmd_setMotorMicroseconds(motor, microseconds)
        elif cmd == "mc":
            motor = int(user_input[1])
            percent = int(user_input[2])
            mcu.cmd_setMotorCalibrated(motor, percent)
        elif cmd == "test":
            mcu.cmd_test()
        elif cmd == "halt":
            mcu.cmd_halt()
        elif cmd == "smc":
            motor = int(user_input[1])
            calibration = int(user_input[2])
            mcu.cmd_setMotorCalibration(motor, calibration)
        elif cmd == "getimu":
            device = user_input[1]
            if device == "accel":
                mcu.cmd_getIMU(PARAM_ACCEL)
            elif device == "gyro":
                mcu.cmd_getIMU(PARAM_GYRO)
            else:
                print("invalid device")
        elif cmd == "sas":
            range = int(user_input[1])
            divisor = int(user_input[2])
            mcu.cmd_setAccelSettings(range, divisor)
        elif cmd == "sgs":
            range = int(user_input[1])
            divisor = int(user_input[2])
            mcu.cmd_setGyroSettings(range, divisor)
        elif cmd == "getvt":
            mcu.cmd_getVoltageAndTemperature()
        elif cmd == "sar":
            enabled = True if user_input[2] == "on" else False
            device = user_input[1]
            delay = int(user_input[3])
            if device == "accel":
                mcu.cmd_setAutoReport(PARAM_ACCEL, enabled, delay)
            elif device == "gyro":
                mcu.cmd_setAutoReport(PARAM_GYRO, enabled, delay)
            elif device == "vt":
                mcu.cmd_setAutoReport(PARAM_VOLT_TEMP, enabled, delay)
            else:
                print("invalid device")
        elif cmd == "sfb":
            enabled = True if user_input[1] == "on" else False
            mcu.cmd_setFeedback(enabled)
        elif cmd == "accel":
            print(mcu.latest_accel)
        elif cmd == "gyro":
            print(mcu.latest_gyro)
        elif cmd == "voltage":
            print(mcu.latest_voltage)
        elif cmd == "temp":
            print(mcu.latest_temp)
        elif cmd == "rpkt":
            queue = user_input[1]
            if queue == "test":
                print(mcu.test_queue.get(timeout=1))
            elif queue == "ok":
                print(mcu.ok_queue.get(timeout=1))
            elif queue == "accel":
                print(mcu.accel_queue.get(timeout=1))
            elif queue == "gyro":
                print(mcu.gyro_queue.get(timeout=1))
            elif queue == "vt":
                print(mcu.volt_temp_queue.get(timeout=1))
            else:
                print("invalid queue")
        elif cmd == "echo":
            print(" ".join(user_input[1:]))
        elif cmd == "exit":
            exit()
        else:
            print("invalid command")

    except:
        print("command error. this isn't a good cli, so you'll have to figure out what happened.")
