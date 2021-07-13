# imu_compensator.py
# IMU automatic compensation for keeping the robot in the correct orientation
# used for transect line routine

from queue import Queue, Empty
from threading import Thread
import time

from mcu_lib.packets import OrientationPacket
from mcu_lib.mcu import MCUInterface
from utils import *

COMPENSATION_CONSTANT = 0.7
COMPENSATION_MULTIPLIER = 2.14

QUEUE_WAIT_DELAY = 0.1
QUEUE_WAIT_SIZE = 6

NORMALIZE_MAX = 50


class IMUCompensator:
    def __init__(self, mcu: MCUInterface, orientation_queue: Queue):
        self.mcu = mcu
        self.zero = Vector3.invalid()
        self.offset = Vector3.new()
        self.seen_axis = Vector3.invalid()
        self.queue = orientation_queue
        self.thread = Thread(target=self.__compensate)
        self.thread_enable = False
        self.enable = False

    def zero_packet(self, pos: Vector3):
        self.zero = pos

    def zero_current(self):
        self.zero = Vector3.from_arr(self.mcu.latest_orientation)

    def init(self):
        time.sleep(QUEUE_WAIT_DELAY)
        if self.queue.qsize() == 0:
            input("No readings from IMU. MCU is likely not on!\nPress enter to retry: ")
        # wait for initial readings
        while self.queue.qsize() < QUEUE_WAIT_SIZE:
            time.sleep(QUEUE_WAIT_DELAY)
        # clear queue
        packets = []
        while self.queue.qsize() > 0:
            packets.append(self.queue.get())
        # reverse traversal of packets until all axes are met
        for i in range(len(packets)-1, -1, -1):
            self.zero.set_axis(packets[i].axis, packets[i].value)
            if self.zero.is_valid():
                break

    def start(self):
        self.thread_enable = True
        self.thread.start()

    def stop(self):
        self.thread_enable = False
        self.thread.join()

    def enable_imu(self):
        self.enable = True

    def disable_imu(self):
        self.enable = False
        self.offset = Vector3.new()

    def __reset_seen(self):
        self.seen_axis = Vector3.invalid()

    def __compensate(self):
        while self.thread_enable:
            try:
                packet: OrientationPacket = self.queue.get(timeout=QUEUE_WAIT_DELAY)
                self.seen_axis.set_axis(packet.axis, packet.value)
            except Empty:
                pass
            finally:
                if self.seen_axis.is_valid() and self.enable:
                    self.__update_offset(self.seen_axis)

    def __update_offset(self, orientation: Vector3):
        output = Vector3.new()
        for axis in range(3):
            axis_value = orientation.get_axis(axis) - self.zero.get_axis(axis)
            # work around the -180/180 barrier
            if axis_value <= -180:
                axis_value += 360
            if axis_value >= 180:
                axis_value -= 360
            # safety: check if robot has drifted too far (not safe to continue compensation)
            if axis_value > 90 or axis_value < -90 or not self.enable:
                # stop imu compensation
                if self.enable:
                    print(f"axis value out of bounds! {axis_value} degrees on {axis}")
                self.disable_imu()
                return
            pos = axis_value >= 0
            pow_value = pow(abs(axis_value), COMPENSATION_CONSTANT)
            if not pos:
                pow_value = -pow_value
            output.set_axis(axis, pow_value * COMPENSATION_MULTIPLIER)
        self.offset = output
        self.__reset_seen()
        self.__normalize_offset()

    def __normalize_offset(self):
        self.offset.x = round(self.offset.x)
        self.offset.y = round(self.offset.y)
        self.offset.z = round(self.offset.z)
        assert -NORMALIZE_MAX <= self.offset.x <= NORMALIZE_MAX
        assert -NORMALIZE_MAX <= self.offset.y <= NORMALIZE_MAX
        assert -NORMALIZE_MAX <= self.offset.z <= NORMALIZE_MAX

    def get_offset(self):
        return self.offset
