import time


axes = ("X", "Y", "Z")


class ReturnPacket:
    def __init__(self, packet_data):
        self.timestamp = time.time()
        self.og_cmd = packet_data[0]
        self.og_param = packet_data[1]
        self.cmd = packet_data[2]
        self.param = packet_data[3]
        self.data = packet_data[4:8]

    def __str__(self):
        return f"[{self.timestamp}] og_cmd={self.og_cmd}, og_param={self.og_param}, cmd=" \
               f"{self.cmd}, param={self.param}, data: [{self.data}]"


class TestPacket:
    def __init__(self, valid, version, contents, timestamp):
        self.timestamp = timestamp
        self.valid = valid
        self.version = version
        self.contents = contents

    def __str__(self):
        is_valid = "Valid" if self.valid else "Invalid"
        return f"[{self.timestamp}] {is_valid} TestPacket: version={self.version}, contents={self.contents}"


class OKPacket:
    def __init__(self, og_cmd, og_param, success, timestamp):
        self.timestamp = timestamp
        self.original_command = og_cmd
        self.original_param = og_param
        self.success = success

    def __str__(self):
        is_success = "OK" if self.success else "Fail"
        return f"[{self.timestamp}] {is_success} from {self.original_command} with {self.original_param}"


class AccelPacket:
    def __init__(self, axis, value, timestamp):
        self.timestamp = timestamp
        self.axis = axis
        self.value = value

    def __str__(self):
        return f"[{self.timestamp}] Accelerometer {axes[self.axis]}: {self.value}"


class GyroPacket:
    def __init__(self, axis, value, timestamp):
        self.timestamp = timestamp
        self.axis = axis
        self.value = value

    def __str__(self):
        return f"[{self.timestamp}] Gyroscope {axes[self.axis]}: {self.value}"


class VoltageTemperaturePacket:
    def __init__(self, voltage, temperature, timestamp):
        self.timestamp = timestamp
        self.voltage = voltage
        self.temperature = temperature

    def __str__(self):
        return f"[{self.timestamp}] Voltage: {self.voltage}, Temperature: {self.temperature}"
