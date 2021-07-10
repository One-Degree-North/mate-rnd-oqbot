INVALID = 0x82D3F2


class Vector3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def set_axis(self, axis: int, value: float):
        if axis == 0:
            self.x = value
        elif axis == 1:
            self.y = value
        elif axis == 2:
            self.z = value
        else:
            raise IndexError("Invalid Axis")

    def get_axis(self, axis: int):
        if axis == 0:
            return self.x
        elif axis == 1:
            return self.y
        elif axis == 2:
            return self.z
        else:
            raise IndexError("Invalid Axis")

    def is_valid(self):
        return self.x != INVALID and self.y != INVALID and self.z != INVALID


class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
