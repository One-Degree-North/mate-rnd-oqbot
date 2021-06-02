import time


class ReturnPacket:
    def __init__(self, packet_data):
        self.timestamp = time.time()
        self.og_cmd = packet_data[0]
        self.og_param = packet_data[1]
        self.cmd = packet_data[2]
        self.param = packet_data[3]
        self.data = packet_data[4:8]
    def __str__(self):
        return f""


class TestPacket:
    def __init__(self, valid, version, contents, timestamp):
        self.timestamp = timestamp
        self.valid = valid
        self.version = version
        self.contents = contents


class OKPacket:
    def __init__(self, og_cmd, og_param, success, timestamp):
        self.timestamp = timestamp
        self.original_command = og_cmd
        self.original_param = og_param
        self.success = success


class AccelPacket:
    def __init__(self, axis, value, timestamp):
        self.timestamp = timestamp
        self.axis = axis
        self.value = value


class AccelThreeAxisPacket:
    def __init__(self, values, timestamp):
        self.timestamp = timestamp
        self.values = values


class GyroPacket:
    def __init__(self, axis, value, timestamp):
        self.timestamp = timestamp
        self.axis = axis
        self.value = value


class GyroThreeAxisPacket:
    def __init__(self, values, timestamp):
        self.timestamp = timestamp
        self.values = values


class VoltageTemperaturePacket:
    def __init__(self, voltage, temperature, timestamp):
        self.timestamp = timestamp
        self.voltage = voltage
        self.temperature = temperature
