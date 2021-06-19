import math


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

    def multiply_by(self, other):
        return Vector(self.x * other, self.y * other)


ZERO_VECTOR = Vector(0, 0)
