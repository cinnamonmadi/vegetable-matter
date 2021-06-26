import math


DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 360


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def ZERO():
        return Vector(0, 0)

    def from_tuple(the_tuple):
        return Vector(the_tuple[0], the_tuple[1])

    def as_tuple(self):
        return (self.x, self.y)

    def length(self):
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    def normalized(self):
        magnitude = self.length()
        return Vector(self.x / magnitude, self.y / magnitude)

    def scaled_to(self, new_length):
        return self.normalized().multiply_by(new_length)

    def sum_with(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def minus(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def multiply_by(self, other):
        return Vector(self.x * other, self.y * other)

    def distance_from(self, other):
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2))

    def as_string(self):
        return str(self.x) + ',' + str(self.y)


def is_rect_collision(rect_a, rect_b):
    return not (rect_a[0] + rect_a[2] <= rect_b[0] or rect_b[0] + rect_b[2] <= rect_a[0] or rect_a[1] + rect_a[3] <= rect_b[1] or rect_b[1] + rect_b[3] <= rect_a[1])


def point_in_rect(point, rect):
    return point[0] >= rect[0] and point[0] <= rect[0] + rect[2] and point[1] >= rect[1] and point[1] <= rect[1] + rect[3]
