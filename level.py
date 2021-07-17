import pygame
import os
import shared
import input
import animation
import player
import enemy


# The level state class
class Level:
    def __init__(self):
        self.player = player.Player()

        self.width = 0
        self.height = 0
        self.background = None
        self.camera_offset = shared.Vector.ZERO()

        self.platforms = []

        self.enemies = []
        self.particles = []
        self.bullets = []

    def on_resume(self):
        input.reset_all()

    def handle_input(self, event):
        input.handle(event)

    def update(self, delta):
        if input.is_just_pressed[input.PLAYER_LEFT]:
            self.player.set_direction(-1)
        elif input.is_just_released[input.PLAYER_LEFT]:
            if input.is_pressed[input.PLAYER_RIGHT]:
                self.player.set_direction(1)
            else:
                self.player.set_direction(0)
        if input.is_just_pressed[input.PLAYER_RIGHT]:
            self.player.set_direction(1)
        elif input.is_just_released[input.PLAYER_RIGHT]:
            if input.is_pressed[input.PLAYER_LEFT]:
                self.player.set_direction(-1)
            else:
                self.player.set_direction(0)

        if input.is_just_pressed[input.PLAYER_JUMP]:
            self.player.jump_input_timer = player.Player.JUMP_INPUT_DURATION

        self.player.update(delta, self.platforms + [enemy_obj.get_hitbox() for enemy_obj in self.enemies], [enemy_obj.get_hurtbox() for enemy_obj in self.enemies if enemy_obj.is_hurtbox_enabled()])

        if self.player.position.x - self.camera_offset.x < shared.DISPLAY_WIDTH * 0.4:
            self.camera_offset.x = self.player.position.x - (shared.DISPLAY_WIDTH * 0.4)
        elif self.player.position.x - self.camera_offset.x > shared.DISPLAY_WIDTH * 0.6:
            self.camera_offset.x = self.player.position.x - (shared.DISPLAY_WIDTH * 0.6)

        # if self.player.position.y - self.camera_offset.y < shared.DISPLAY_HEIGHT * 0.4:
            # self.camera_offset.y = self.player.position.y - (shared.DISPLAY_HEIGHT * 0.4)
        # elif self.player.position.y - self.camera_offset.y > shared.DISPLAY_HEIGHT * 0.6:
            # self.camera_offset.y = self.player.position.y - (shared.DISPLAY_HEIGHT * 0.6)

        if self.camera_offset.x < 0:
            self.camera_offset.x = 0
        elif self.camera_offset.x > 2560 - shared.DISPLAY_WIDTH:
            self.camera_offset.x = 2560 - shared.DISPLAY_WIDTH

        # if self.camera_offset.y < 0:
            # self.camera_offset.y = 0
        # elif self.camera_offset.y > 640 - shared.DISPLAY_HEIGHT:
            # self.camera_offset.y = 640 - shared.DISPLAY_HEIGHT

        self.particles += self.player.get_particles()
        if input.is_pressed[input.PLAYER_SHOOT]:
            new_bullet = self.player.shoot()
            if new_bullet is not None:
                self.bullets.append(new_bullet)

        for enemy_obj in self.enemies:
            enemy_obj.update(delta, self.player.get_hitbox(), self.platforms + [other_enemy.get_hitbox() for other_enemy in self.enemies if other_enemy is not enemy_obj])

        for bullet in self.bullets:
            bullet.update(delta)
            enemy_obj = bullet.check_collisions(self.platforms, self.enemies)
            if enemy_obj is not None:
                enemy_obj.take_damage()
                if not enemy_obj.is_alive():
                    self.particles.append((animation.Animation('onion_death', 10), enemy_obj.position.minus(shared.Vector(18, 32)).as_tuple()))
                    if enemy_obj.run_animation.flip_h:
                        self.particles[len(self.particles) - 1][0].flip_h = True
                    self.enemies.remove(enemy_obj)
        self.bullets = [bullet for bullet in self.bullets if not bullet.delete_me]

        for particle in self.particles:
            particle[0].update(delta)
        self.particles = [particle for particle in self.particles if not particle[0].finished]

        input.flush_events()

    def is_on_screen(self, rect):
        return shared.is_rect_collision(rect, self.camera_offset.as_tuple() + (shared.DISPLAY_WIDTH, shared.DISPLAY_HEIGHT))

    def camera_offset_rect(self, rect):
        return (rect[0] - self.camera_offset.x, rect[1] - self.camera_offset.y, rect[2], rect[3])

    def camera_offset_pos(self, pos):
        return (pos[0] - self.camera_offset.x, pos[1] - self.camera_offset.y)

    def render(self, display):
        display.blit(animation.frame_data['level'][0], shared.Vector.ZERO().minus(self.camera_offset).as_tuple())
        for platform in self.platforms:
            platform_rect = shared.Vector(platform[0], platform[1]).minus(self.camera_offset).as_tuple() + platform[2:]
            pygame.draw.rect(display, shared.Color.RED, platform_rect, False)
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

    def load_file(self, path):
        if not os.path.exists(path):
            self.gen_mapfile(path)

        self.player.position = shared.Vector(32, 32)
        self.enemies = []
        self.platforms = []

        mapfile = open(path, 'r')
        for line in mapfile.readlines():
            command, value = line.split('=')
            if command == 'size':
                self.width, self.height = [int(num) for num in value.split(',')]
            elif command == 'platform':
                self.platforms.append(tuple([int(num) for num in value.split(',')]))
        mapfile.close()

    def gen_mapfile(self, path):
        map_image_path = 'res/gfx/' + path[path.index('/') + 1:path.index('.')] + '.png'
        print(map_image_path)
        map_frame = pygame.image.load(map_image_path)
        map_frame.convert()

        tiles = []
        for x in range(0, map_frame.get_width()):
            tiles.append([])
            for y in range(0, map_frame.get_height()):
                color = map_frame.get_at((x, y))
                tiles[x].append(color.r == 0 and color.g == 0 and color.b == 0)

        breathing_tiles = []
        for x in range(0, map_frame.get_width()):
            breathing_tiles.append([])
            for y in range(0, map_frame.get_height()):
                if not tiles[x][y]:
                    breathing_tiles[x].append(False)
                    continue
                is_breathing = False
                adjacents = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                for adjacent in adjacents:
                    if adjacent[0] < 0 or adjacent[0] >= map_frame.get_width() or adjacent[1] < 0 or adjacent[1] >= map_frame.get_height():
                        continue
                    if not tiles[adjacent[0]][adjacent[1]]:
                        is_breathing = True
                        break
                breathing_tiles[x].append(is_breathing)

        platforms = []
        for x in range(0, map_frame.get_width()):
            for y in range(0, map_frame.get_height()):
                if breathing_tiles[x][y]:
                    new_x = x
                    curr_x = x
                    while breathing_tiles[curr_x][y]:
                        breathing_tiles[curr_x][y] = False
                        curr_x += 1
                    new_width = curr_x - new_x
                    platforms.append((new_x, y, new_width, 1))

        for y in range(0, map_frame.get_height()):
            for x in range(0, map_frame.get_width()):
                if breathing_tiles[x][y]:
                    new_y = y
                    curr_y = y
                    while breathing_tiles[x][curr_y]:
                        breathing_tiles[x][curr_y] = False
                        curr_y += 1
                    new_height = curr_y - new_y
                    platforms.append((x, new_y, 1, new_height))


        outfile = open(path, 'w')
        outfile.write('size=' + str(map_frame.get_width()) + ',' + str(map_frame.get_height()) + '\n')
        for platform in platforms:
            outfile.write('platform=' + ','.join([str(value) for value in platform]) + '\n')
        outfile.close()
