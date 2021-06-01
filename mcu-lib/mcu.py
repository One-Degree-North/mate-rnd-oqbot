import serial
import struct
import time
import threading
from queue import Queue

from packets import *


# bs ("byte-string")
def bs(v: int):
    return chr(v).encode('latin')


class MCUInterface:
    def __init__(self, port, baud=230400, close_on_startup=True, refresh_rate=1000):
        self.__serial = serial.Serial(port, baud, timeout=0, write_timeout=None)
        self.__queue = Queue()
        self.__fetch_thread = threading.Thread(target=self.read_serial)
        self.__parse_thread = threading.Thread(target=self.parse_serial)
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

    def start_serial(self):
        self.__serial.open()
        while not self.__serial.is_open:
            time.sleep(0.01)
        self.__thread_enable = True
        self.__fetch_thread.start()

    def read_serial(self):
        while self.__thread_enable:
            try:
                byte_string = self.__serial.read(size=16)
                for byte in byte_string:
                    self.__queue.put(byte)
            except serial.SerialException:
                pass
            time.sleep(self.__refresh_time)

    def parse_serial(self):
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
            self.test_queue.put(TestPacket(valid, version, contents))
        elif packet.cmd == bs(0x0A):
            # OK
            og_cmd = int.from_bytes(packet.og_cmd, 'big')
            og_param = int.from_bytes(packet.og_param, 'big')
            success = int.from_bytes(packet.param, 'big') > 0
            self.ok_queue.put(OKPacket(og_cmd, og_param, success))
        elif packet.cmd == bs(0x3A):
            # accel
            axis = int(int.from_bytes(packet.param, 'big') / 0x30)
            value = struct.unpack('f', packet.data)
            self.accel_queue.put(AccelPacket(axis, value))
            self.latest_acceleration[axis] = value
        elif packet.cmd == bs(0x3C):
            # gyro
            axis = int(int.from_bytes(packet.param, 'big') / 0x30)
            value = struct.unpack('f', packet.data)
            self.gyro_queue.put(GyroPacket(axis, value))
            self.latest_rotation[axis] = value
        elif packet.cmd == bs(0x44):
            # temp/volt
            temp, volts = struct.unpack('HH', packet.data)
            temp /= 100
            volts /= 100
            self.volt_temp_queue.put(VoltageTemperaturePacket(volts, temp))
        else:
            print("invalid packet")
