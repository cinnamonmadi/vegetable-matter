import pygame
import shared
import animation
import player
import enemy


# The level state class
class Level:
    def __init__(self):
        self.player = player.Player()
        self.player.position = shared.Vector(32, 200)

        self.camera_offset = shared.Vector.ZERO()

        self.platforms = [Platform('object_floor', 0, 300), Platform('object_platform', 200, 260)]
        self.enemies = []
        self.particles = []
        self.bullets = []

        new_enemy = enemy.Onion()
        new_enemy.position = shared.Vector(550, 200)
        self.enemies.append(new_enemy)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
        elif event.type == pygame.KEYUP:
            self.handle_keyup(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_a:
            self.player.set_direction(-1)
        elif event.key == pygame.K_d:
            self.player.set_direction(1)
        elif event.key == pygame.K_SPACE:
            self.player.jump_input_timer = player.Player.JUMP_INPUT_DURATION

    def handle_keyup(self, event):
        if event.key == pygame.K_a:
            if pygame.key.get_pressed()[pygame.K_d]:
                self.player.set_direction(1)
            else:
                self.player.set_direction(0)
        elif event.key == pygame.K_d:
            if pygame.key.get_pressed()[pygame.K_a]:
                self.player.set_direction(-1)
            else:
                self.player.set_direction(0)

    def update(self, delta):
        self.player.update(delta, [platform.get_hitbox() for platform in self.platforms] + [enemy_obj.get_hitbox() for enemy_obj in self.enemies], [enemy_obj.get_hurtbox() for enemy_obj in self.enemies if enemy_obj.is_hurtbox_enabled()])
        self.particles += self.player.get_particles()
        if pygame.key.get_pressed()[pygame.K_l]:
            new_bullet = self.player.shoot()
            if new_bullet is not None:
                self.bullets.append(new_bullet)

        for enemy_obj in self.enemies:
            enemy_obj.update(delta, self.player.get_hitbox(), [platform.get_hitbox() for platform in self.platforms] + [other_enemy.get_hitbox() for other_enemy in self.enemies if other_enemy is not enemy_obj])

        for bullet in self.bullets:
            bullet.update(delta)
            enemy_obj = bullet.check_collisions([platform.get_hitbox() for platform in self.platforms], self.enemies)
            if enemy_obj is not None:
                enemy_obj.take_damage()
                if not enemy_obj.is_alive():
                    self.enemies.remove(enemy_obj)
        self.bullets = [bullet for bullet in self.bullets if not bullet.delete_me]

        for particle in self.particles:
            particle[0].update(delta)
        self.particles = [particle for particle in self.particles if not particle[0].finished]

    def is_on_screen(self, rect):
        return shared.is_rect_collision(rect, self.camera_offset.as_tuple() + (shared.DISPLAY_WIDTH, shared.DISPLAY_HEIGHT))

    def camera_offset_rect(self, rect):
        return (rect[0] - self.camera_offset.x, rect[1] - self.camera_offset.y, rect[2], rect[3])

    def camera_offset_pos(self, pos):
        return (pos[0] - self.camera_offset.x, pos[1] - self.camera_offset.y)

    def render(self, display):
        for platform in self.platforms:
            if self.is_on_screen(platform.get_hitbox()):
                display.blit(platform.get_frame(), platform.position.minus(self.camera_offset).as_tuple())

        display.blit(self.player.get_frame(), self.player.position.minus(self.camera_offset).as_tuple())

        for enemy_obj in self.enemies:
            if self.is_on_screen(enemy_obj.get_frame_rect()):
                display.blit(enemy_obj.get_frame(), enemy_obj.position.minus(self.camera_offset).as_tuple())

        for bullet in self.bullets:
            if self.is_on_screen(bullet.get_frame_rect()):
                display.blit(bullet.get_frame(), bullet.position.minus(self.camera_offset).as_tuple())

        for particle in self.particles:
            if self.is_on_screen(particle[1] + particle[0].get_frame().get_size()):
                display.blit(particle[0].get_frame(), self.camera_offset_pos(particle[1]))

    def save_as(self, path):
        outfile = open(path, 'w')
        outfile.write('player=' + self.player.position.as_string() + '\n')
        for platform in self.platforms:
            outfile.write('platform=' + platform.name + ',' + platform.position.as_string() + '\n')
        for enemy_obj in self.enemies:
            outfile.write('enemy=' + enemy_obj.position.as_string() + '\n')
        outfile.close()

    def load_file(self, path):
        self.platforms = []
        self.enemies = []

        infile = open(path, 'r')
        for line in infile.readlines():
            line_without_newline_character = line[:len(line) - 1]
            line_parts = line_without_newline_character.split('=')
            line_command = line_parts[0]
            line_arguments = line_parts[1].split(',')

            if line_command == 'player':
                self.player.position = shared.Vector(int(line_arguments[0]), int(line_arguments[1]))
            elif line_command == 'platform':
                self.platforms.append(Platform(line_arguments[0], int(line_arguments[1]), int(line_arguments[2])))
            elif line_command == 'enemy':
                enemy_obj = enemy.Onion()
                enemy_obj.position = shared.Vector(int(line_arguments[0]), int(line_arguments[1]))
                self.enemies.append(enemy_obj)

        infile.close()


class Platform:
    def __init__(self, name, x, y):
        self.position = shared.Vector(x, y)
        self.name = name

    def get_frame(self):
        return animation.frame_data[self.name][0]

    def get_hitbox(self):
        return self.position.as_tuple() + self.get_frame().get_size()
