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
            'PLAYER_RIGHT': False,
            'PLAYER_JUMP': False
        }

        self.floor_rect = (0, 300, 640, 60)
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
            self.inputs['PLAYER_JUMP'] = True

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
        elif event.key == pygame.K_SPACE:
            self.inputs['PLAYER_JUMP'] = False

    def update(self, delta):
        self.player.update(delta)
        self.player.check_collisions([self.floor_rect])
        if self.inputs['PLAYER_JUMP']:
            self.player.jump()
        self.particles += self.player.get_particles()

        for particle in self.particles:
            particle[0].update(delta)
        self.particles = [particle for particle in self.particles if not particle[0].finished]

    def render(self, display):
        pygame.draw.rect(display, shared.Color.WHITE, self.floor_rect)
        display.blit(self.player.get_frame(), self.player.position.as_tuple())

        for particle in self.particles:
            display.blit(particle[0].get_frame(), particle[1])
