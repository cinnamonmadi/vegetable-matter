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

        self.platforms = [(0, 300, 640, 60), (200, 260, 100, 10)]
        self.particles = []

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
        elif event.key == pygame.K_SPACE:
            self.player.jump_input_timer = player.Player.JUMP_INPUT_DURATION

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
        self.player.update(delta, self.platforms)
        self.particles += self.player.get_particles()

        for particle in self.particles:
            particle[0].update(delta)
        self.particles = [particle for particle in self.particles if not particle[0].finished]

    def render(self, display):
        for platform in self.platforms:
            pygame.draw.rect(display, shared.Color.WHITE, platform)
        display.blit(self.player.get_frame(), self.player.position.as_tuple())

        for particle in self.particles:
            display.blit(particle[0].get_frame(), particle[1])
