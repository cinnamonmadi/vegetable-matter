import shared
import animation


# Class for the player character
class Player:
    SPEED = 3

    def __init__(self):
        self.position = shared.ZERO_VECTOR
        self.velocity = shared.ZERO_VECTOR
        self.animation = animation.Animation('player_run', 11)
        self.direction = 0

    def set_direction(self, direction):
        if self.animation.flip_h and direction == 1:
            self.animation.flip_h = False
        elif not self.animation.flip_h and direction == -1:
            self.animation.flip_h = True
        self.direction = direction

    def update(self, delta):
        self.velocity.x = self.direction * Player.SPEED
        self.position = self.position.sum_with(self.velocity.multiply_by(delta))

        self.animation.update(delta)

    def get_image(self):
        return self.animation.get_frame()
