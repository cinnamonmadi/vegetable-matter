import pygame
import shared
import enemy
import level


# The level editor state class
class Editor:
    VALID_OBJECTS = ['object_floor', 'object_platform']

    def __init__(self, screen_size):
        self.level = level.Level()
        self.screen_scale = (screen_size[0] / shared.DISPLAY_WIDTH, screen_size[1] / shared.DISPLAY_HEIGHT)
        self.input_string = ''
        self.held_object = None
        self.render_gridlines = True
        self.grid_size = 16

        self.font = pygame.font.Font('./res/hack.ttf', 10)

    def scale_to_screen(self, pos):
        return (int(pos[0] / self.screen_scale[0]), int(pos[1] / self.screen_scale[1]))

    def snap_to_grid(self, pos):
        return (int(pos[0] / self.grid_size) * self.grid_size, int(pos[1] / self.grid_size) * self.grid_size)

    def handle_input(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mousemovement(event)
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mousedown(event)

    def handle_keydown(self, event):
        if self.held_object is not None:
            if event.key == pygame.K_d:
                if self.held_object in self.level.platforms:
                    self.level.platforms.remove(self.held_object)
                    self.held_object = None
                elif self.held_object in self.level.enemies:
                    self.level.enemies.remove(self.held_object)
                    self.held_object = None
            return
        if (event.key >= pygame.K_a and event.key <= pygame.K_z) or event.key == pygame.K_SPACE or (event.key >= pygame.K_0 and event.key <= pygame.K_9) or event.key == pygame.K_PERIOD:
            self.input_string += chr(event.key)
        elif event.key == pygame.K_MINUS and (pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]):
            self.input_string += '_'
        elif event.key == pygame.K_BACKSPACE:
            self.input_string = self.input_string[:len(self.input_string) - 1]
        elif event.key == pygame.K_RETURN:
            self.handle_command(self.input_string)
            self.input_string = ''

    def handle_mousemovement(self, event):
        if pygame.mouse.get_pressed()[2]:
            camera_movement = shared.Vector.from_tuple(self.scale_to_screen(event.rel))
            self.level.camera_offset = self.level.camera_offset.minus(camera_movement)
        elif self.held_object is not None:
            self.held_object.position = shared.Vector.from_tuple(self.snap_to_grid(self.scale_to_screen(event.pos))).sum_with(self.level.camera_offset)

    def handle_mousedown(self, event):
        if self.held_object is not None:
            self.held_object = None
        elif self.input_string == '':
            mouse_pos = shared.Vector.from_tuple(self.scale_to_screen(event.pos)).sum_with(self.level.camera_offset).as_tuple()
            for platform in self.level.platforms:
                if shared.point_in_rect(mouse_pos, platform.get_hitbox()):
                    self.held_object = platform
                    return
            for enemy_obj in self.level.enemies:
                if shared.point_in_rect(mouse_pos, enemy_obj.get_hitbox()):
                    self.held_object = enemy_obj
                    return
            if shared.point_in_rect(mouse_pos, self.level.player.get_hitbox()):
                self.held_object = self.level.player

    def handle_command(self, command):
        command_parts = command.split(' ')
        if command_parts[0] == 'place' and len(command_parts) == 2:
            if command_parts[1] in Editor.VALID_OBJECTS:
                self.held_object = level.Platform(command_parts[1], 0, 0)
                self.level.platforms.append(self.held_object)
            elif command_parts[1] == 'onion':
                self.held_object = enemy.Onion()
                self.level.enemies.append(self.held_object)
        elif command_parts[0] == 'grid':
            if len(command_parts) == 2 and command_parts[1] == 'toggle':
                self.render_gridlines = not self.render_gridlines
            elif len(command_parts) == 2 and command_parts[1] == 'on':
                self.render_gridlines = True
            elif len(command_parts) == 2 and command_parts[1] == 'off':
                self.render_gridlines = False
            elif len(command_parts) == 3 and command_parts[1] == 'size' and command_parts[2].isnumeric():
                self.grid_size = int(command_parts[2])
        elif command_parts[0] == 'save':
            if len(command_parts) == 2:
                self.level.save_as(command_parts[1])
        elif command_parts[0] == 'load':
            if len(command_parts) == 2:
                self.level.load_file(command_parts[1])

    def update(self, delta):
        pass

    def render(self, display):
        self.level.render(display)

        if self.held_object is not None:
            display.blit(self.held_object.get_frame(), self.held_object.position.minus(self.level.camera_offset).as_tuple())

        if self.render_gridlines:
            line_x = self.level.camera_offset.x
            line_x = int(line_x / self.grid_size) * self.grid_size
            if line_x - self.level.camera_offset.x < 0:
                line_x += self.grid_size
            while line_x - self.level.camera_offset.x >= 0 and line_x - self.level.camera_offset.x < shared.DISPLAY_WIDTH:
                pygame.draw.rect(display, shared.Color.YELLOW, (line_x - self.level.camera_offset.x, 0, 1, shared.DISPLAY_HEIGHT), 0)
                line_x += self.grid_size

            line_y = self.level.camera_offset.y
            line_y = int(line_y / self.grid_size) * self.grid_size
            if line_y - self.level.camera_offset.y < 0:
                line_y += self.grid_size
            while line_y - self.level.camera_offset.y >= 0 and line_y - self.level.camera_offset.y < shared.DISPLAY_HEIGHT:
                pygame.draw.rect(display, shared.Color.YELLOW, (0, line_y - self.level.camera_offset.y, shared.DISPLAY_WIDTH, 1), 0)
                line_y += self.grid_size

        typing_text = self.font.render(self.input_string, False, shared.Color.WHITE)
        display.blit(typing_text, (0, 10))
