import shared
import animation


class Enemy:
    GRAVITY = 0.1
    MAX_FALL_SPEED = 3
    INVULN_DURATION = 5

    def __init__(self):
        assert hasattr(self, 'SPEED'), 'Enemy speed not defined'
        assert hasattr(self, 'SEARCH_RADIUS'), 'Enemy search radius not defined'
        assert hasattr(self, 'MAX_HEALTH'), 'Enemy max health not defined'
        assert hasattr(self, 'run_animation'), 'Enemy run animation was not defined'
        assert hasattr(self, 'attack_animation'), 'Enemy attack animation was not defined'
        assert hasattr(self, 'hitbox'), 'Enemy hitbox not defined'
        assert hasattr(self, 'hurtbox'), 'Enemy hurtbox not defined'

        self.position = shared.Vector.ZERO()
        self.velocity = shared.Vector.ZERO()
        self.movement = shared.Vector.ZERO()

        self.attack_animation.finished = True

        self.direction = 0
        self.grounded = False

        self.invuln_timer = 0
        self.health = self.MAX_HEALTH
        self.has_projectile = False

    def get_hitbox(self):
        return (self.position.x + self.hitbox[0], self.position.y + self.hitbox[1], self.hitbox[2], self.hitbox[3])

    def get_hurtbox(self):
        right_side_hurtbox_offset = 0
        if not self.attack_animation.flip_h:
            right_side_hurtbox_offset = self.hitbox[2]
        return (self.position.x + self.hurtbox[0] + right_side_hurtbox_offset, self.position.y + self.hurtbox[1], self.hurtbox[2], self.hurtbox[3])

    def is_hurtbox_enabled(self):
        return False

    def get_projectile(self, player_center):
        return None

    def get_death_particle(self):
        return None

    def set_direction(self, player_center):
        self.direction = 0
        if self.attack_animation.finished and self.position.distance_from(player_center) <= self.SEARCH_RADIUS:
            if player_center.x > self.position.x:
                self.direction = 1
            else:
                self.direction = -1

    def update(self, delta, player_center, player_rect, platforms):
        self.set_direction(player_center)

        self.velocity.x = self.direction * self.SPEED
        self.velocity.y += Enemy.GRAVITY * delta
        if self.velocity.y > Enemy.MAX_FALL_SPEED:
            self.velocity.y = Enemy.MAX_FALL_SPEED

        self.movement = self.velocity.multiply_by(delta)
        self.position = self.position.sum_with(self.movement)

        self.check_collisions(platforms)

        self.invuln_timer -= delta
        if self.invuln_timer < 0:
            self.invuln_timer = 0
            self.run_animation.whitemask = False
            self.attack_animation.whitemask = False

        if self.direction == -1 and not self.run_animation.flip_h:
            self.run_animation.flip_h = True
            self.attack_animation.flip_h = True
        elif self.direction == 1 and self.run_animation.flip_h:
            self.run_animation.flip_h = False
            self.attack_animation.flip_h = False

        if not self.attack_animation.finished:
            self.attack_animation.update(delta)
            self.run_animation.reset()
        elif not self.grounded or self.direction == 0:
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

                if shared.is_rect_collision((self.position.x + self.hitbox[0] + self.movement.x, self.position.y + self.hitbox[1], self.hitbox[2], self.hitbox[3]), collider):
                    x_caused = True
                if shared.is_rect_collision((self.position.x + self.hitbox[0], self.position.y + self.hitbox[1] + self.movement.y, self.hitbox[2], self.hitbox[3]), collider):
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
        self.invuln_timer = Enemy.INVULN_DURATION
        self.run_animation.whitemask = True
        self.attack_animation.whitemask = True

    def is_alive(self):
        return self.health > 0


class Onion(Enemy):
    def __init__(self):
        self.SPEED = 1
        self.SEARCH_RADIUS = 200
        self.MAX_HEALTH = 10
        self.run_animation = animation.Animation('onion_run', 7)
        self.attack_animation = animation.Animation('onion_attack', 7)
        self.hitbox = (6, 9, 22, 23)
        self.hurtbox = (-5, 0, 10, 23)
        super().__init__()

    def update(self, delta, player_center, player_rect, platforms):
        super().update(delta, player_center, player_rect, platforms)
        if self.attack_animation.finished and shared.is_rect_collision(self.get_hurtbox(), player_rect):
            self.attack_animation.finished = False

    def is_hurtbox_enabled(self):
        return not self.attack_animation.finished and self.attack_animation.frame == 5

    def get_death_particle(self):
        death_particle = (animation.Animation('onion_death', 10), self.position.minus(shared.Vector(18, 32)).as_tuple())
        death_particle.flip_h = self.run_animation.flip_h
        return death_particle


class Tomato(Enemy):
    def __init__(self):
        self.SPEED = 0
        self.SEARCH_RADIUS = 200
        self.MAX_HEALTH = 10
        self.run_animation = animation.Animation('tomato_idle', 8)
        self.attack_animation = animation.Animation('tomato_attack', 10)
        self.hitbox = (7, 11, 19, 22)
        self.hurtbox = None
        super().__init__()

        self.projectile_primed = False

    def set_direction(self, player_center):
        self.direction = 0
        if self.position.distance_from(player_center) <= self.SEARCH_RADIUS:
            if player_center.x > self.position.x:
                self.direction = 1
            else:
                self.direction = -1

    def update(self, delta, player_center, player_rect, platforms):
        if self.attack_animation.finished and self.position.distance_from(player_center) <= self.SEARCH_RADIUS:
            self.attack_animation.finished = False
            self.projectile_primed = True
        elif not self.attack_animation.finished and self.attack_animation.frame == 4 and self.projectile_primed:
            self.has_projectile = True
            self.projectile_primed = False
        super().update(delta, player_center, player_rect, platforms)

    def get_projectile(self, player_center):
        self.has_projectile = False
        x_offset = 32
        if self.run_animation.flip_h:
            x_offset = -13
        x_offset = 0
        return TomatoHead(self.position.sum_with(shared.Vector(x_offset, 0)), player_center, self.run_animation.flip_h)


class TomatoHead():
    SPEED = 2

    def __init__(self, position, target, flip_h):
        self.position = position
        self.animation = animation.Animation('tomato_projectile', 1)
        self.animation.flip_h = flip_h
        self.hitbox = (0, 0, 13, 17)

        self.velocity = shared.Vector.ZERO()
        self.velocity.x = TomatoHead.SPEED
        if flip_h:
            self.velocity.x *= -1

        t = (target.x - self.position.x) / self.velocity.x
        self.velocity.y = (target.y - self.position.y - (0.5 * Enemy.GRAVITY * t * t)) / t

        self.delete_me = False

    def update(self, delta, platforms):
        self.velocity.y += Enemy.GRAVITY * delta

        self.movement = self.velocity.multiply_by(delta)
        self.position = self.position.sum_with(self.movement)

        for platform in platforms:
            if shared.is_rect_collision(self.get_hitbox(), platform):
                self.delete_me = True
                break

    def get_hitbox(self):
        return (self.position.x + self.hitbox[0], self.position.y + self.hitbox[1], self.hitbox[2], self.hitbox[3])

    def get_frame(self):
        return self.animation.get_frame()

    def get_frame_rect(self):
        return self.position.as_tuple() + self.get_frame().get_size()

    def take_damage(self):
        self.delete_me = True
