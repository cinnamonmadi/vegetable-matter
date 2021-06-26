import shared
import animation


# onion_run fps = 7 and hitbox = 6, 9, 22, 23
class Onion:
    SPEED = 1
    GRAVITY = 0.1
    MAX_FALL_SPEED = 3
    PLAYER_SEARCH_RADIUS = 200
    MAX_HEALTH = 20
    INVULN_DURATION = 5

    def __init__(self):
        self.position = shared.Vector.ZERO()
        self.velocity = shared.Vector.ZERO()
        self.movement = shared.Vector.ZERO()

        self.run_animation = animation.Animation('onion_run', 7)
        self.attack_animation = animation.Animation('onion_attack', 7)
        self.attack_animation.finished = True  # turn off the one-shot animation to start

        self.hitbox_offset = shared.Vector(6, 9)
        self.hitbox_size = (22, 23)
        self.hurtbox_size = (10, 23)
        self.grounded = False

        self.invuln_timer = 0

        self.health = Onion.MAX_HEALTH

    def get_hitbox(self):
        return self.position.sum_with(self.hitbox_offset).as_tuple() + self.hitbox_size

    def get_hurtbox(self):
        hurtbox_x_offset = -5
        if not self.attack_animation.flip_h:
            hurtbox_x_offset += self.hitbox_size[0]
        return self.position.sum_with(self.hitbox_offset).sum_with(shared.Vector(hurtbox_x_offset, 0)).as_tuple() + self.hurtbox_size

    def is_hurtbox_enabled(self):
        return not self.attack_animation.finished and self.attack_animation.frame == 5

    def update(self, delta, player_rect, platforms):
        player_center = shared.Vector(player_rect[0] + (player_rect[2] / 2), player_rect[1] + (player_rect[3] / 2))
        direction = 0
        if self.attack_animation.finished and self.position.distance_from(player_center) <= Onion.PLAYER_SEARCH_RADIUS:
            if player_center.x > self.position.x:
                direction = 1
            else:
                direction = -1
        self.velocity.x = direction * Onion.SPEED
        self.velocity.y += Onion.GRAVITY * delta
        if self.velocity.y > Onion.MAX_FALL_SPEED:
            self.velocity.y = Onion.MAX_FALL_SPEED

        self.movement = self.velocity.multiply_by(delta)
        self.position = self.position.sum_with(self.movement)

        self.check_collisions(platforms)
        if self.attack_animation.finished and shared.is_rect_collision(self.get_hurtbox(), player_rect):
            self.attack_animation.finished = False

        self.invuln_timer -= delta
        if self.invuln_timer < 0:
            self.invuln_timer = 0
            self.run_animation.whitemask = False
            self.attack_animation.whitemask = False

        if direction == -1 and not self.run_animation.flip_h:
            self.run_animation.flip_h = True
            self.attack_animation.flip_h = True
        elif direction == 1 and self.run_animation.flip_h:
            self.run_animation.flip_h = False
            self.attack_animation.flip_h = False

        if not self.attack_animation.finished:
            self.attack_animation.update(delta)
            self.run_animation.reset()
        elif not self.grounded or direction == 0:
            self.run_animation.reset()
        else:
            self.run_animation.update(delta)

    def check_collisions(self, colliders):
        self.grounded = False
        for collider in colliders:
            if shared.is_rect_collision(self.get_hitbox(), collider):
                self.position = self.position.minus(self.movement)
                x_caused = False
                y_caused = False

                if shared.is_rect_collision((self.position.x + self.hitbox_offset.x + self.movement.x, self.position.y + self.hitbox_offset.y) + self.hitbox_size, collider):
                    x_caused = True
                if shared.is_rect_collision((self.position.x + self.hitbox_offset.x, self.position.y + self.hitbox_offset.y + self.movement.y) + self.hitbox_size, collider):
                    y_caused = True

                if not x_caused:
                    self.position.x += self.movement.x
                if not y_caused:
                    self.position.y += self.movement.y
                else:
                    if self.velocity.y > 0:
                        self.grounded = True

    def get_frame(self):
        if not self.attack_animation.finished:
            return self.attack_animation.get_frame()
        else:
            return self.run_animation.get_frame()

    def get_frame_rect(self):
        return self.position.as_tuple() + self.get_frame().get_size()

    def take_damage(self):
        if self.invuln_timer > 0:
            return
        self.health -= 1
        self.invuln_timer = Onion.INVULN_DURATION
        self.run_animation.whitemask = True
        self.attack_animation.whitemask = True

    def is_alive(self):
        return self.health > 0
