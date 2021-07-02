import pygame
import shared


# The pause menu state class
class Pause:
    SCREEN_CENTER = (shared.DISPLAY_WIDTH / 2, shared.DISPLAY_HEIGHT / 2)
    MAIN_MENU_SIZE = (200, 105)
    MAIN_MENU_POS = (SCREEN_CENTER[0] - (MAIN_MENU_SIZE[0] / 2), SCREEN_CENTER[1] - (MAIN_MENU_SIZE[1] / 2))

    def __init__(self, screen_size):
        self.screen_scale = (screen_size[0] / shared.DISPLAY_WIDTH, screen_size[1] / shared.DISPLAY_HEIGHT)

        self.background = pygame.Surface((shared.DISPLAY_WIDTH, shared.DISPLAY_HEIGHT))

        self.fade = pygame.Surface((shared.DISPLAY_WIDTH, shared.DISPLAY_HEIGHT))
        self.fade.set_alpha(100)
        self.fade.fill((0, 0, 0))

        self.main_menu_font = pygame.font.Font('./res/hack.ttf', 12)
        self.main_menu_title_text = self.main_menu_font.render('- Game Paused - ', False, shared.Color.BLACK)
        self.main_menu_title_pos = (Pause.SCREEN_CENTER[0] - (self.main_menu_title_text.get_width() / 2), Pause.MAIN_MENU_POS[1] + 10)

        resume_button = Button(self.main_menu_font, 'Resume', (-1, self.main_menu_title_pos[1] + 30))
        controls_button = Button(self.main_menu_font, 'Controls', (-1, resume_button.pos[1] + 20))
        exit_button = Button(self.main_menu_font, 'Exit', (-1, controls_button.pos[1] + 20))
        self.main_menu_buttons = [resume_button, controls_button, exit_button]

        self.menu_state = -1

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
            mouse_pos = (event.pos[0] / self.screen_scale[0], event.pos[1] / self.screen_scale[1])
            self.menu_state = -1
            for i in range(0, len(self.main_menu_buttons)):
                if shared.point_in_rect(mouse_pos, self.main_menu_buttons[i].box):
                    self.menu_state = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_state == 0:
                self.is_active = False
            elif self.menu_state == 2:
                self.request_quit = True

    def update(self, delta):
        pass

    def render(self, display):
        display.blit(self.background, (0, 0))
        display.blit(self.fade, (0, 0))

        pygame.draw.rect(display, shared.Color.WHITE, Pause.MAIN_MENU_POS + Pause.MAIN_MENU_SIZE)
        display.blit(self.main_menu_title_text, self.main_menu_title_pos)
        for i in range(0, len(self.main_menu_buttons)):
            display.blit(self.main_menu_buttons[i].text, self.main_menu_buttons[i].pos)
            if self.menu_state == i:
                pygame.draw.rect(display, shared.Color.BLACK, self.main_menu_buttons[i].box, 1)


class Button:
    def __init__(self, font, text, pos):
        self.text = font.render(text, False, shared.Color.BLACK)
        self.pos = list(pos)
        if self.pos[0] == -1:
            self.pos[0] = (shared.DISPLAY_WIDTH / 2) - (self.text.get_width() / 2)
        if self.pos[1] == -1:
            self.pos[1] = (shared.DISPLAY_HEIGHT / 2) - (self.text.get_height() / 2)

        x_padding = 4
        y_padding = 1
        self.box = (self.pos[0] - x_padding, self.pos[1] - y_padding, self.text.get_width() + (x_padding * 2), self.text.get_height() + (y_padding * 2))
