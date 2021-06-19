import pygame
import shared
import player


# The level state class
class Level:
    def __init__(self):
        self.player = player.Player()
        self.player.position = shared.Vector(32, 200)

        self.inputs = {
            'PLAYER_LEFT': False,
            'PLAYER_RIGHT': False
        }

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
        elif event.type == pygame.KEYUP:
            self.handle_keyup(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_a:
            self.inputs['PLAYER_LEFT'] = True
            self.player.set_direction(-1)
        elif event.key == pygame.K_d:
            self.inputs['PLAYER_RIGHT'] = True
            self.player.set_direction(1)

    def handle_keyup(self, event):
        if event.key == pygame.K_a:
            self.inputs['PLAYER_LEFT'] = False
            if self.inputs['PLAYER_RIGHT']:
                self.player.set_direction(1)
            else:
                self.player.set_direction(0)
        elif event.key == pygame.K_d:
            self.inputs['PLAYER_RIGHT'] = False
            if self.inputs['PLAYER_LEFT']:
                self.player.set_direction(-1)
            else:
                self.player.set_direction(0)

    def update(self, delta):
        self.player.update(delta)

    def render(self, display):
        display.blit(self.player.animation.get_frame(), self.player.position.as_tuple())
