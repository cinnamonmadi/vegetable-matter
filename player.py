import shared
import animation


# Class for the player character
class Player:
    SPEED = 2
    GRAVITY = 0.1
    MAX_FALL_SPEED = 3
    JUMP_IMPULSE = 3
    JUMP_INPUT_DURATION = 4
    COYOTE_TIME_DURATION = 4
    SHOT_DELAY = 7
    KNOCKBACK_DURATION = 120

    def __init__(self):
        self.position = shared.Vector.ZERO()
        self.velocity = shared.Vector.ZERO()
        self.movement = shared.Vector.ZERO()

        self.knockback = shared.Vector.ZERO()
        self.knockback_timer = 0

        self.run_animation = animation.Animation('player_run', 11)
        self.jump_animation = animation.Animation('player_jump', 1)

        self.size = self.run_animation.get_frame().get_size()
        self.hitbox_offset = shared.Vector(9, 11)
        self.hitbox_size = (14, 21)
        self.direction = 0
        self.grounded = False
        self.jump_input_timer = 0
        self.coyote_timer = 0

        self.shoot_timer = 0

        self.particles = []

    def get_hitbox(self):
        return self.position.sum_with(self.hitbox_offset).as_tuple() + self.hitbox_size

    def apply_knockback(self, x, y):
        self.knockback_timer = Player.KNOCKBACK_DURATION
        self.knockback = shared.Vector(x, y)

    def set_direction(self, direction):
        if self.run_animation.flip_h and direction == 1:
            self.run_animation.flip_h = False
            self.jump_animation.flip_h = False
        elif not self.run_animation.flip_h and direction == -1:
            self.run_animation.flip_h = True
            self.jump_animation.flip_h = True
        self.direction = direction

    def jump(self):
        if self.grounded or self.coyote_timer > 0:
            self.velocity.y = -Player.JUMP_IMPULSE
            self.grounded = False
            self.coyote_timer = 0
            self.particles.append((animation.Animation('player_liftoff', 11), self.position.as_tuple()))

    def update(self, delta, platforms, hurtboxes):
        if self.knockback_timer > 0:
            self.velocity = self.knockback
        else:
            self.velocity.x = self.direction * Player.SPEED
        self.velocity.y += Player.GRAVITY * delta
        if self.velocity.y > Player.MAX_FALL_SPEED:
            self.velocity.y = Player.MAX_FALL_SPEED

        self.movement = self.velocity.multiply_by(delta)
        self.position = self.position.sum_with(self.movement)

        self.check_collisions(platforms)
        if self.grounded:
            self.coyote_timer = Player.COYOTE_TIME_DURATION
        if self.jump_input_timer > 0 and self.grounded:
            self.jump_input_timer = 0
            self.jump()
        self.jump_input_timer -= delta
        if self.jump_input_timer < 0:
            self.jump_input_timer = 0

        for hurtbox in hurtboxes:
            if shared.is_rect_collision(self.get_hitbox(), hurtbox):
                hurtbox_center_x = hurtbox[0] + (hurtbox[2] / 2)
                hitbox_center_x = self.get_hitbox()[0] + (self.get_hitbox()[2] / 2)
                if hurtbox_center_x >= hitbox_center_x:
                    self.apply_knockback(-3, -2)
                else:
                    self.apply_knockback(3, -2)
                break

        self.coyote_timer -= delta
        if self.coyote_timer < 0:
            self.coyote_timer = 0

        self.shoot_timer -= delta
        if self.shoot_timer < 0:
            self.shoot_timer = 0

        self.knockback_timer -= delta
        if self.knockback_timer < 0:
            self.knockback_timer = 0

        if not self.grounded or self.direction == 0:
            self.run_animation.reset()
        else:
            self.run_animation.update(delta)

    def check_collisions(self, colliders):
        self.grounded = False
        for collider in colliders:
            if shared.is_rect_collision(self.get_hitbox(), collider):
                self.knockback_timer = 0
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
        if self.grounded:
            return self.run_animation.get_frame()
        else:
            if abs(self.velocity.y) < 0.5:
                return self.jump_animation.get_frame_at(1)
            elif self.velocity.y < 0:
                return self.jump_animation.get_frame_at(0)
            else:
                return self.jump_animation.get_frame_at(2)

    # get_particles() and get_bullets() hand-off generated child objects to the Level class so that the generated objects will be updated in the scope of Level.update()
    def get_particles(self):
        return_list = []
        while len(self.particles) != 0:
            return_list.append(self.particles.pop(0))
        return return_list

    def shoot(self):
        if self.shoot_timer > 0:
            return None

        new_bullet = Bullet()
        hitbox = self.get_hitbox()
        new_bullet.position = shared.Vector(hitbox[0] + (hitbox[2] / 2) - (new_bullet.hitbox_size[0] / 2), hitbox[1] + (hitbox[3] / 2) - (new_bullet.hitbox_size[1] / 2))
        if self.run_animation.flip_h:
            new_bullet.position.x -= 15
            new_bullet.velocity = shared.Vector(-Bullet.SPEED, 0)
        else:
            new_bullet.position.x += 15
            new_bullet.velocity = shared.Vector(Bullet.SPEED, 0)
        self.shoot_timer = Player.SHOT_DELAY
        return new_bullet


class Bullet:
    DAMAGE = 1
    SPEED = 7
    TIME_TO_LIVE = 180

    def __init__(self):
        self.position = shared.Vector.ZERO()
        self.velocity = shared.Vector.ZERO()
        self.hitbox_size = (10, 6)
        self.ttl = Bullet.TIME_TO_LIVE
        self.delete_me = False

    def get_hitbox(self):
        return self.position.as_tuple() + self.hitbox_size

    def update(self, delta):
        self.ttl -= delta
        if self.ttl <= 0:
            self.delete_me = True

        movement = self.velocity.multiply_by(delta)
        self.position = self.position.sum_with(movement)

    # Checks for collisions and requests to delete itself if a collision occurred
    # If the collision is with an enemy, the enemy is returned so that damage can be applied
    # Assumes each enemy has a get_hitbox() function
    def check_collisions(self, static_colliders, enemy_colliders):
        hitbox = self.get_hitbox()
        for enemy in enemy_colliders:
            if shared.is_rect_collision(hitbox, enemy.get_hitbox()):
                self.delete_me = True
                return enemy
        for collider in static_colliders:
            if shared.is_rect_collision(hitbox, collider):
                self.delete_me = True
                return None
        return None

    def get_frame(self):
        return animation.frame_data['bullet'][0]
