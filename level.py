import pygame
import shared
import animation
import player
import enemy


# The level state class
class Level:
    def __init__(self):
        self.player = player.Player()

        self.camera_offset = shared.Vector.ZERO()

        self.tiles = []
        self.platforms = []

        self.enemies = []
        self.particles = []
        self.bullets = []

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
        self.player.update(delta, self.platforms + [enemy_obj.get_hitbox() for enemy_obj in self.enemies], [enemy_obj.get_hurtbox() for enemy_obj in self.enemies if enemy_obj.is_hurtbox_enabled()])

        if self.player.position.x - self.camera_offset.x < shared.DISPLAY_WIDTH * 0.4:
            self.camera_offset.x = self.player.position.x - (shared.DISPLAY_WIDTH * 0.4)
        elif self.player.position.x - self.camera_offset.x > shared.DISPLAY_WIDTH * 0.6:
            self.camera_offset.x = self.player.position.x - (shared.DISPLAY_WIDTH * 0.6)
        if self.camera_offset.x < 0:
            self.camera_offset.x = 0
        elif self.camera_offset.x > (len(self.tiles[0]) * shared.TILE_SIZE) - shared.DISPLAY_WIDTH:
            self.camera_offset.x = (len(self.tiles[0]) * shared.TILE_SIZE) - shared.DISPLAY_WIDTH

        self.particles += self.player.get_particles()
        if pygame.key.get_pressed()[pygame.K_l]:
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
        # important assumption being made here: camera position is never negative (otherwise this logic wouldn't work)
        start_x = int(self.camera_offset.x / shared.TILE_SIZE)
        y = int(self.camera_offset.y / shared.TILE_SIZE)
        while (y * shared.TILE_SIZE) - self.camera_offset.y < shared.DISPLAY_HEIGHT:
            x = start_x
            while (x * shared.TILE_SIZE) - self.camera_offset.x < shared.DISPLAY_WIDTH:
                if self.tiles[y][x] != -1:
                    display.blit(animation.frame_data['tiles'][self.tiles[y][x]], ((x * shared.TILE_SIZE) - self.camera_offset.x, (y * shared.TILE_SIZE) - self.camera_offset.y))
                x += 1
            y += 1

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
        infile = open(path, 'r')

        self.tiles = []

        vegetable_tiles_gid = -1
        vegetable_chars_gid = -1

        current_layer = None
        current_firstgid = -1
        current_y = 0

        for line in infile.readlines():
            line = line.strip()

            if current_layer is not None:
                if line.startswith('<data'):
                    continue
                if line[len(line) - 1] != ',':
                    current_layer = None
                else:
                    line = line[:(len(line) - 1)]

                row = [int(value) - current_firstgid for value in line.split(',')]
                for x in range(0, len(row)):
                    if current_layer == 'tiles':
                        self.tiles[current_y][x] = row[x]
                    elif current_layer == 'chars':
                        if row[x] == 0:
                            self.player.position = shared.Vector(x * 32, current_y * 32)
                        elif row[x] == 1:
                            new_enemy = enemy.Onion()
                            new_enemy.position = shared.Vector(x * 32, current_y * 32)
                            self.enemies.append(new_enemy)
                current_y += 1

            data = Level.read_xml_line(line)
            if data is None:
                continue

            if data['header'] == 'map':
                for y in range(0, int(data['height'])):
                    self.tiles.append([])
                    for x in range(0, int(data['width'])):
                        self.tiles[y].append(-1)

            if data['header'] == 'tileset':
                if data['source'] == 'vegetable_tiles.tsx':
                    vegetable_tiles_gid = int(data['firstgid'])
                elif data['source'] == 'vegetable_chars.tsx':
                    vegetable_chars_gid = int(data['firstgid'])

            if data['header'] == 'layer':
                current_layer = data['name']
                if current_layer == 'tiles':
                    current_firstgid = vegetable_tiles_gid
                else:
                    current_firstgid = vegetable_chars_gid
                current_y = 0
        infile.close()

        self.platforms = [(x * shared.TILE_SIZE, y * shared.TILE_SIZE, shared.TILE_SIZE, shared.TILE_SIZE) for x in range(0, len(self.tiles[0])) for y in range(0, len(self.tiles)) if self.tiles[y][x] != -1]

    def read_xml_line(line):
        if line.startswith('<?') or line.startswith('</') or not line.startswith('<'):
            return None

        if line.endswith('/>'):
            line = line[1:line.index('/>')]
        else:
            line = line[1:line.index('>')]

        parts = line.split(' ')

        data = {}
        data['header'] = parts[0]

        for part in parts[1:]:
            data_name = part[:part.index('=')]
            data_value = part[(part.index('"') + 1):(len(part) - 1)]
            data[data_name] = data_value

        return data


class Platform:
    def __init__(self, name, x, y):
        self.position = shared.Vector(x, y)
        self.name = name

    def get_frame(self):
        return animation.frame_data[self.name][0]

    def get_hitbox(self):
        return self.position.as_tuple() + self.get_frame().get_size()
