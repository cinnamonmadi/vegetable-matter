import pygame
import shared


# The pause menu state class
class Pause:
    SCREEN_CENTER = (shared.DISPLAY_WIDTH / 2, shared.DISPLAY_HEIGHT / 2)

    def __init__(self, screen_size):
        self.screen_scale = (screen_size[0] / shared.DISPLAY_WIDTH, screen_size[1] / shared.DISPLAY_HEIGHT)

        self.background = pygame.Surface((shared.DISPLAY_WIDTH, shared.DISPLAY_HEIGHT))

        self.fade = pygame.Surface((shared.DISPLAY_WIDTH, shared.DISPLAY_HEIGHT))
        self.fade.set_alpha(100)
        self.fade.fill((0, 0, 0))

        self.size = ((200, 85))
        self.pos = (Pause.SCREEN_CENTER[0] - (self.size[0] / 2), Pause.SCREEN_CENTER[1] - (self.size[1] / 2))

        menu_font = pygame.font.Font('./res/hack.ttf', 12)
        self.title_text = menu_font.render('- Game Paused - ', False, shared.Color.BLACK)
        self.title_pos = (Pause.SCREEN_CENTER[0] - (self.title_text.get_width() / 2), self.pos[1] + 10)

        button_labels = ['Resume', 'Exit']
        self.buttons = [Button(menu_font, button_labels[0], (-1, self.title_pos[1] + 25))]
        for i in range(1, len(button_labels)):
            self.buttons.append(Button(menu_font, button_labels[i], (-1, self.buttons[i - 1].pos[1] + self.buttons[i - 1].box[3] + 5)))

        self.mouse_pos = (0, 0)
        self.state = -1

        self.is_active = False
        self.request_quit = False

    def set_active(self, current_state):
        pygame.draw.rect(self.background, shared.Color.BLACK, (0, 0, shared.DISPLAY_WIDTH, shared.DISPLAY_HEIGHT), False)
        current_state.render(self.background)
        self.is_active = True

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            self.is_active = False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = (event.pos[0] / self.screen_scale[0], event.pos[1] / self.screen_scale[1])
            self.state = -1
            for i in range(0, len(self.buttons)):
                if shared.point_in_rect(self.mouse_pos, self.buttons[i].box):
                    self.state = i
                    return
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != pygame.BUTTON_LEFT:
                return
            menu_value = self.buttons[self.state].value
            if menu_value == '':
                return
            elif menu_value == 'Resume':
                self.is_active = False
            elif menu_value == 'Exit':
                self.request_quit = True

    def update(self, delta):
        pass

    def render(self, display):
        display.blit(self.background, (0, 0))
        display.blit(self.fade, (0, 0))

        pygame.draw.rect(display, shared.Color.WHITE, self.pos + self.size)
        display.blit(self.title_text, self.title_pos)
        for i in range(0, len(self.buttons)):
            display.blit(self.buttons[i].text, self.buttons[i].pos)
            if self.state == i:
                pygame.draw.rect(display, shared.Color.BLACK, self.buttons[i].box, 1)


class Button:
    def __init__(self, font, text, pos):
        self.value = text
        self.text = font.render(text, False, shared.Color.BLACK)
        self.pos = list(pos)
        if self.pos[0] == -1:
            self.pos[0] = Pause.SCREEN_CENTER[0] - (self.text.get_width() / 2)
        if self.pos[1] == -1:
            self.pos[1] = Pause.SCREEN_CENTER[1] - (self.text.get_height() / 2)

        x_padding = 4
        y_padding = 1
        self.box = (self.pos[0] - x_padding, self.pos[1] - y_padding, self.text.get_width() + (x_padding * 2), self.text.get_height() + (y_padding * 2))
