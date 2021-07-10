from queue import Queue, Empty
from threading import Thread

from mcu_lib.packets import OrientationPacket
from utils import *

COMPENSATION_CONSTANT = 0.2


class IMUCompensator:
    def __init__(self, orientation_queue: Queue):
        self.zero = Vector3(0, 0, 0)
        self.offset = Vector3(0, 0, 0)
        self.seen_axis = Vector3(INVALID, INVALID, INVALID)
        self.queue = orientation_queue
        self.thread = Thread(target=self.__compensate)
        self.thread_enable = False

    def zero_packet(self, pos: Vector3):
        self.zero = pos

    def init(self):
        # clear queue
        packets = []
        while self.queue.qsize() > 0:
            packets.append(self.queue.get())
        # reverse traversal of packets until all axes are met
        data = [INVALID, INVALID, INVALID]
        for i in range(len(packets), 0, -1):
            data[packets[i].axis] = packets[i].value
            if data[0] != INVALID and data[1] != INVALID and data[2] != INVALID:
                break
        # zero the packet
        self.zero_packet(Vector3(data[0], data[1], data[2]))

    def start(self):
        self.thread_enable = True
        self.thread.start()

    def stop(self):
        self.thread_enable = False
        self.thread.join()

    def __reset_seen(self):
        self.seen_axis = Vector3(INVALID, INVALID, INVALID)

    def __compensate(self):
        while True:
            try:
                packet: OrientationPacket = self.queue.get(timeout=0.1)
                self.seen_axis.set_axis(packet.axis, packet.value)
            except Empty:
                pass
            finally:
                if self.seen_axis.is_valid:
                    self.__update_offset(self.seen_axis)

    def __update_offset(self, orientation: Vector3):
        output = Vector3(0, 0, 0)
        for axis in range(3):
            output.set_axis(axis, pow(orientation.get_axis(axis) - self.zero.get_axis(axis), 1.5) / -2)
        self.offset = output
        self.__reset_seen()

    def get_offset(self):
        return self.offset


# left = pos X -> turn right
# up = neg Y -> turn down
