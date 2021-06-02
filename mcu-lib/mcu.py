# mcu.py
# a comprehensive library for communicating with the MATE OQBot.
# please read docs/packet_structure.md and docs/command_list.md for more information.
# there is a CLI for testing available at mcu_cli.py. read docs/mcu_cli.md for usage.

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
DEVICE_VOLT_TEMP = 0x17
MAX_QUEUE_SIZE = 512


# bs ("byte-string")
# converts an int into a single character bytestring
def bs(v: int) -> bytes:
    return chr(v).encode('latin')


# converts a signed int8 to unsigned int8
def to_unsigned_int8(signed_int8: int) -> int:
    assert -128 <= signed_int8 <= 127
    neg = signed_int8 < 0
    if neg:
        return signed_int8 + 0xFF
    return signed_int8


class MCUInterface:
    """
    MCUInterface - Layer for interfacing between a Python program and the microcontroller over Serial.

    Attributes:
        latest_accel : List[float] - latest acceleration values, [x, y, z].
        latest_gyro : List[float] - latest angular velocity values, [x, y, z].
        latest_voltage : float - latest voltage on the 12V rail.
        latest_temp : float - latest temperature measured within the electronics box.
        test_queue : Queue[TestPacket] - Queue to access all received packets of TestPacket type.
        ok_queue : Queue[OKPacket] - Queue to access all received packets of OKPacket type.
        accel_queue : Queue[AccelPacket] - Queue to access all received packets of AccelPacket type.
        gyro_queue : Queue[GyroPacket] - Queue to access all received packets of GyroPacket type.
        volt_temp_queue : Queue[VoltageTemperaturePacket] - Queue to access all received packets of that type.

    Methods:
        get_port() -> str
            returns the interface's serial.Serial object's port.
        get_baud() -> str
            returns the interface's serial.Serial Object's baudrate.
        open_serial()
            opens the integrated serial interface.
        close_serial()
            closes the integrated serial interface.
        cmd_{PACKET_COMMAND}()
            refer to docs/command_list.md. most should be self-explanatory.
    """
    def __init__(self, port: str, baud: int=230400, close_on_startup: bool=True, refresh_rate: int=1440):
        """
        Default and only constructor for the MCUInterface class.

        :param port: Port to connect to.
        :param baud: Baudrate to connect at.
        :param close_on_startup: Whether to close the serial object at startup, so it can be opened later.
        :param refresh_rate: Number of times per seconds to refresh the serial cache for packets.
        """
        self.__serial = serial.Serial(port, baud, timeout=0, write_timeout=None)
        self.__queue = Queue()
        self.__fetch_thread = threading.Thread(target=self.__read_serial)
        self.__parse_thread = threading.Thread(target=self.__parse_serial)
        self.__refresh_time = 1 / refresh_rate
        self.__thread_enable = False
        self.__init_queues()
        self.latest_accel = [0, 0, 0]
        self.latest_gyro = [0, 0, 0]
        self.latest_voltage = 0
        self.latest_temp = 0
        if close_on_startup:
            self.__serial.close()

    def __init_queues(self):
        self.test_queue = Queue(MAX_QUEUE_SIZE)
        self.ok_queue = Queue(MAX_QUEUE_SIZE)
        self.accel_queue = Queue(MAX_QUEUE_SIZE)
        self.gyro_queue = Queue(MAX_QUEUE_SIZE)
        self.volt_temp_queue = Queue(MAX_QUEUE_SIZE)

    def get_port(self) -> str:
        """
        Get the integrated serial object's port.

        :return: the port.
        """
        return self.__serial.port

    def get_baud(self) -> int:
        """
        Get the integrated serial object's baudrate.

        :return: the baudrate.
        """
        return self.__serial.baudrate

    def open_serial(self):
        """
        Opens the integrated serial's connection to the microcontroller.
        """
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
                    self.__queue.put(bs(byte))
            except serial.SerialException:
                pass
            time.sleep(self.__refresh_time)

    def __parse_serial(self):
        while self.__thread_enable:
            if self.__queue.qsize() >= 10:
                packet = self.__read_packet()
                if packet:
                    self.__parse_packet(packet)
            time.sleep(self.__refresh_time)

    def close_serial(self):
        """
        Closes the integrated serial's connection to the microcontroller.
        """
        self.__thread_enable = False
        self.__fetch_thread.join()
        self.__parse_thread.join()
        self.__serial.close()

    def __read_packet(self) -> ReturnPacket:  # returns a generic ReturnPacket
        next_byte = self.__queue.get()
        while next_byte != bs(0xAC) and self.__queue.qsize() >= 10:
            next_byte = self.__queue.get()
        if self.__queue.qsize() < 9:
            return
        packet_data = []
        for i in range(9):  # 0x1 to 0x9
            packet_data.append(self.__queue.get())
        if packet_data[8] != bs(0x74):
            # invalid packet
            return
        packet = ReturnPacket(packet_data)
        return packet

    def __parse_packet(self, packet: ReturnPacket):
        data_bs = packet.data[0] + packet.data[1] + packet.data[2] + packet.data[3]
        if not packet:
            return
        # let's all pretend this was a Python 3.10+ match/case statement
        if packet.cmd == bs(0x00):
            # test
            version = int.from_bytes(packet.data[0], 'big')
            contents = (packet.data[1] + packet.data[2] + packet.data[3]).decode('latin')
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
            value = struct.unpack('f', data_bs)
            self.accel_queue.put(AccelPacket(axis, value, packet.timestamp))
            self.latest_accel[axis] = value[0]
        elif packet.cmd == bs(0x3C):
            # gyro
            axis = int(int.from_bytes(packet.param, 'big') / 0x30)
            value = struct.unpack('f', data_bs)
            self.gyro_queue.put(GyroPacket(axis, value, packet.timestamp))
            self.latest_gyro[axis] = value[0]
        elif packet.cmd == bs(0x44):
            # temp/volt
            temp, volts = struct.unpack('HH', data_bs)
            temp /= 100
            volts /= 100
            self.latest_temp = temp
            self.latest_voltage = volts
            self.volt_temp_queue.put(VoltageTemperaturePacket(volts, temp, packet.timestamp))
        else:
            print("invalid packet")

    def __send_packet(self, cmd: int, param: int, data: bytes):
        assert len(data) == 4, "data is not 4 bytes long!"
        packet = bs(0xCA) + bs(cmd) + bs(param) + data + bs(0x47)
        self.__serial.write(packet)

    def cmd_test(self):
        self.__send_packet(0x00, 0xF0, NIL_BS * 4)

    def cmd_halt(self):
        self.__send_packet(0x0F, 0x00, NIL_BS * 4)

    def cmd_setMotorMicroseconds(self, motor: int, microseconds: int):
        assert 0 <= motor <= 4, "There are only 5 motors (0-4)"
        data = bs(microseconds // 0xFF) + bs(microseconds % 0xFF) + NIL_BS * 2
        self.__send_packet(0x10, motor, data)

    def cmd_setMotorCalibrated(self, motor: int, percent: int):
        assert 0 <= motor <= 4, "There are only 5 motors (0-4)"
        assert -100 <= percent <= 100, "Calibrated % Range is [-100, 100]"
        data = bs(to_unsigned_int8(percent)) + NIL_BS * 3
        self.__send_packet(0x12, motor, data)

    def cmd_setMotorCalibration(self, motor: int, value: int):
        assert 0 <= motor <= 4, "There are only 5 motors (0-4)"
        assert 0 <= value <= 4000, "Calibration range is [0, 4000] where 1000 is normal"
        data = bs(value // 0xFF) + bs(value % 0xFF) + NIL_BS * 2
        self.__send_packet(0x13, motor, data)

    def cmd_getIMU(self, device: int):
        assert device == DEVICE_ACCEL or device == DEVICE_GYRO, "invalid device!"
        self.__send_packet(0x30, device, NIL_BS * 4)

    def cmd_setAccelSettings(self, range: int, divisor: int):
        assert 0 <= range <= 3, "invalid range!"
        assert 1 <= divisor <= 0xFF, "invalid divisor!"
        data = bs(range) + bs(divisor) + NIL_BS * 2
        self.__send_packet(0x33, 0x15, data)

    def cmd_setGyroSettings(self, range: int, divisor: int):
        assert 0 <= range <= 3, "invalid range!"
        assert 1 <= divisor <= 0xFF, "invalid divisor!"
        data = bs(range) + bs(divisor) + NIL_BS * 2
        self.__send_packet(0x34, 0x16, data)

    def cmd_getVoltageAndTemperature(self):
        self.__send_packet(0x40, 0x17, NIL_BS * 4)

    def cmd_setVoltageCalibration(self, calibration: float):
        self.__send_packet(0x43, 0x17, struct.pack('f', calibration))

    def cmd_setAutoReport(self, device, enabled: bool, delay: int):
        assert device == 0x15 or device == 0x16 or device == 0x17, "invalid device!"
        assert 0 <= delay <= 65535, "invalid delay!"
        on = 0xFF if enabled else 0x00
        data = bs(on) + bs(delay // 0xFF) + bs(delay % 0xFF) + NIL_BS
        self.__send_packet(0x50, device, data)

    def cmd_setFeedback(self, enabled: bool):
        on = 0xFF if enabled else 0x00
        data = bs(on) + NIL_BS * 3
        self.__send_packet(0x51, 0x01, data)


if __name__ == "__main__":
    # runs a simple test to verify that communication is working.
    mcu = MCUInterface(input("Port? \n"), int(input("Baudrate? \n")))
    mcu.open_serial()
    print("Sending cmd_test in 0.5 seconds:")
    time.sleep(0.5)
    mcu.cmd_test()
    print("Sent! Waiting 0.5 seconds for response...")
    time.sleep(0.5)
    print("If we received a packet, it would be here:")
    print(mcu.test_queue.get())
    mcu.close_serial()
