import pygame
import shared
import animation


# The animation viewer is a simple devtool state used to test viewing animations
class AnimViewer:
    def __init__(self, anim_name):
        self.anim = animation.Animation(anim_name, 5)
        self.playing = True
        self.typing_fps = False
        self.anim_fps = 5
        self.fps_string = str(self.anim_fps)
        self.scale = 1

        pygame.font.init()  # Per the pygame docs: it is safe to call this more than once
        self.font = pygame.font.Font('./res/hack.ttf', 10)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event)

    def get_key_as_number(event_key):
        if event_key >= pygame.K_0 and event_key <= pygame.K_9:
            return event_key - pygame.K_0
        elif event_key >= pygame.K_KP_1 and event_key <= pygame.K_KP_9:
            return (event_key - pygame.K_KP_1) + 1
        elif event_key == pygame.K_KP_0:  # We need to do a separte if here because K_KP_0 is actually greater in value than K_KP_9
            return 0
        else:
            return -1

    def handle_keydown(self, event):
        number = AnimViewer.get_key_as_number(event.key)
        if number != -1:
            self.handle_num_entry(number)
        elif self.typing_fps:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.finish_typing()
            return
        elif event.key == pygame.K_SPACE:
            self.playing = not self.playing
        elif event.key == pygame.K_UP:
            self.anim_fps += 1
            self.fps_string = str(self.anim_fps)
            self.anim.set_fps(self.anim_fps)
        elif event.key == pygame.K_DOWN:
            if self.anim_fps != 1:
                self.anim_fps -= 1
                self.fps_string = str(self.anim_fps)
                self.anim.set_fps(self.anim_fps)
        elif event.key == pygame.K_RIGHT:
            self.scale += 0.1
        elif event.key == pygame.K_LEFT:
            if self.scale > 0.5:
                self.scale -= 0.1
        elif event.key == pygame.K_RETURN:
            self.scale = 1

    def handle_num_entry(self, number):
        if not self.typing_fps:
            if number == 0:
                return
            self.typing_fps = True
            self.fps_string = ''
        self.fps_string += str(number)

    def finish_typing(self):
        self.anim_fps = int(self.fps_string)
        self.anim.set_fps(self.anim_fps)
        self.typing_fps = False

    def update(self, delta):
        if self.playing and not self.typing_fps:
            self.anim.update(delta)

    def render(self, display):
        anim_fps_text = self.font.render('Animation FPS: ' + self.fps_string, False, shared.Color.WHITE)
        scale_text = self.font.render('Animation Scale: x' + '{:.1f}'.format(self.scale), False, shared.Color.WHITE)
        display.blit(anim_fps_text, (0, 10))
        display.blit(scale_text, (0, 20))

        anim_frame = self.anim.get_frame()
        target_width = int(anim_frame.get_width() * self.scale)
        target_height = int(anim_frame.get_height() * self.scale)
        rendered_frame = pygame.transform.scale(anim_frame, (target_width, target_height))
        display.blit(rendered_frame, ((display.get_width() / 2) - (target_width / 2), (display.get_height() / 2) - (target_height / 2)))
