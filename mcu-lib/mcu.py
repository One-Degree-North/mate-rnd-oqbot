import serial
import struct
import time
import threading
from queue import Queue

from packets import *

NIL_BS = chr(0x00).encode('latin')
MAX_BS = chr(0xFF).encode('latin')
DEVICE_ACCEL = 0x15
DEVICE_GYRO = 0x16
DEVICE_TEMPVOLT = 0x17


# bs ("byte-string")
def bs(v: int):
    return chr(v).encode('latin')


def to_unsigned_int8(signed_int8):
    assert -128 <= signed_int8 <= 127
    neg = signed_int8 < 0
    if neg:
        return signed_int8 + 0xFF
    return signed_int8


class MCUInterface:
    def __init__(self, port, baud=230400, close_on_startup=True, refresh_rate=1000):
        self.__serial = serial.Serial(port, baud, timeout=0, write_timeout=None)
        self.__queue = Queue()
        self.__fetch_thread = threading.Thread(target=self.__read_serial)
        self.__parse_thread = threading.Thread(target=self.__parse_serial)
        self.__refresh_time = 1 / refresh_rate
        self.__thread_enable = False
        self.__init_queues()
        self.latest_acceleration = [0, 0, 0]
        self.latest_rotation = [0, 0, 0]
        if close_on_startup:
            self.__serial.close()

    def __init_queues(self):
        self.test_queue = Queue(512)
        self.ok_queue = Queue(512)
        self.accel_queue = Queue(512)
        self.gyro_queue = Queue(512)
        self.volt_temp_queue = Queue(512)

    def open_serial(self):
        self.__serial.open()
        while not self.__serial.is_open:
            time.sleep(0.01)
        self.__thread_enable = True
        self.__fetch_thread.start()
        self.__parse_thread.start()

    def __read_serial(self):
        while self.__thread_enable:
            try:
                byte_string = self.__serial.read(size=16)
                for byte in byte_string:
                    self.__queue.put(byte)
            except serial.SerialException:
                pass
            time.sleep(self.__refresh_time)

    def __parse_serial(self):
        while self.__thread_enable:
            self.__parse_packet(self.__read_packet())
            time.sleep(self.__refresh_time)

    def close_serial(self):
        self.__thread_enable = False
        self.__fetch_thread.join()
        self.__serial.close()

    def __read_packet(self):  # returns a generic ReturnPacket
        next_byte = self.__queue.get()
        while next_byte != bs(0xAC):
            next_byte = self.__queue.get()
        packet_data = []
        for i in range(9):  # 0x1 to 0x9
            packet_data.append(self.__queue.get())
        if packet_data[8] != bs(0x74):
            # invalid packet
            return
        packet = ReturnPacket(packet_data)
        return packet

    def __parse_packet(self, packet: ReturnPacket):
        if not packet:
            return
        if packet.cmd == bs(0x00):
            # test
            version = int.from_bytes(packet.data[0], 'big')
            contents = packet.data[1:].decode('latin')
            valid = contents == "pog"
            self.test_queue.put(TestPacket(valid, version, contents, packet.timestamp))
        elif packet.cmd == bs(0x0A):
            # OK
            og_cmd = int.from_bytes(packet.og_cmd, 'big')
            og_param = int.from_bytes(packet.og_param, 'big')
            success = int.from_bytes(packet.param, 'big') > 0
            self.ok_queue.put(OKPacket(og_cmd, og_param, success, packet.timestamp))
        elif packet.cmd == bs(0x3A):
            # accel
            axis = int(int.from_bytes(packet.param, 'big') / 0x30)
            value = struct.unpack('f', packet.data)
            self.accel_queue.put(AccelPacket(axis, value, packet.timestamp))
            self.latest_acceleration[axis] = value
        elif packet.cmd == bs(0x3C):
            # gyro
            axis = int(int.from_bytes(packet.param, 'big') / 0x30)
            value = struct.unpack('f', packet.data)
            self.gyro_queue.put(GyroPacket(axis, value, packet.timestamp))
            self.latest_rotation[axis] = value
        elif packet.cmd == bs(0x44):
            # temp/volt
            temp, volts = struct.unpack('HH', packet.data)
            temp /= 100
            volts /= 100
            self.volt_temp_queue.put(VoltageTemperaturePacket(volts, temp, packet.timestamp))
        else:
            print("invalid packet")

    def __send_packet(self, cmd, param, data: bytes):
        assert len(data) == 4, "data is not 4 bytes long!"
        assert len(cmd) == len(param) == 1, "command or parameter is not 1 byte long!"
        packet = bs(0xCA) + bs(cmd) + bs(param) + data + bs(0x47)
        self.__serial.write(packet)

    def cmd_test(self):
        self.__send_packet(0x00, 0xF0, NIL_BS * 4)

    def cmd_halt(self):
        self.__send_packet(0x0F, 0x00, NIL_BS * 4)

    def cmd_setMotorMicroseconds(self, motor, microseconds):
        assert 0 <= motor <= 4, "There are only 5 motors (0-4)"
        data = bs(microseconds // 0xFF) + bs(microseconds % 0xFF) + NIL_BS * 2
        self.__send_packet(0x10, motor, data)

    def cmd_setMotorCalibrated(self, motor, percent):
        assert 0 <= motor <= 4, "There are only 5 motors (0-4)"
        assert -100 <= percent <= 100, "Calibrated % Range is [-100, 100]"
        data = bs(to_unsigned_int8(percent)) + NIL_BS * 3
        self.__send_packet(0x12, motor, data)

    def cmd_setMotorCalibration(self, motor, value):
        assert 0 <= motor <= 4, "There are only 5 motors (0-4)"
        assert 0 <= value <= 4000, "Calibration range is [0, 4000] where 1000 is normal"
        data = bs(value // 0xFF) + bs(value % 0xFF) + NIL_BS * 2
        self.__send_packet(0x13, motor, data)

    def cmd_getIMU(self, device):
        assert device == DEVICE_ACCEL or device == DEVICE_GYRO, "invalid device!"
        self.__send_packet(0x30, device, NIL_BS * 4)

    def cmd_setAccelSettings(self, range, divisor):
        assert 0 <= range <= 3, "invalid range!"
        assert 1 <= divisor <= 0xFF, "invalid divisor!"
        data = bs(range) + bs(divisor) + NIL_BS * 2
        self.__send_packet(0x33, 0x15, data)

    def cmd_setGyroSettings(self, range, divisor):
        assert 0 <= range <= 3, "invalid range!"
        assert 1 <= divisor <= 0xFF, "invalid divisor!"
        data = bs(range) + bs(divisor) + NIL_BS * 2
        self.__send_packet(0x34, 0x16, data)

    def cmd_getVoltageAndTemperature(self):
        self.__send_packet(0x40, 0x17, NIL_BS * 4)

    def cmd_setVoltageCalibration(self, calibration: float):
        self.__send_packet(0x43, 0x17, struct.pack('f', calibration))

    def cmd_setAutoReport(self, device, enabled: bool, delay: int):
        assert device == 0x14 or device == 0x16 or device == 0x17, "invalid device!"
        assert 0 <= delay <= 65535, "invalid delay!"
        on = 0xFF if enabled else 0x00
        data = bs(on) + bs(delay // 0xFF) + bs(delay % 0xFF) + NIL_BS
        self.__send_packet(0x50, device, data)

    def cmd_setFeedback(self, enabled):
        on = 0xFF if enabled else 0x00
        data = bs(on) + NIL_BS * 3
        self.__send_packet(0x51, 0x01, data)

    def print_queues(self):
