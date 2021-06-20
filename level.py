import pygame
import shared
import player


# The level state class
class Level:
    def __init__(self):
        self.player = player.Player()
        self.player.position = shared.Vector(32, 200)

        self.platforms = [(0, 300, 640, 60), (200, 260, 100, 10)]
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
        self.player.update(delta, self.platforms)
        self.particles += self.player.get_particles()
        if pygame.key.get_pressed()[pygame.K_l]:
            new_bullet = self.player.shoot()
            if new_bullet is not None:
                self.bullets.append(new_bullet)

        for bullet in self.bullets:
            bullet.update(delta)
            bullet.check_collisions(self.platforms, [])
        self.bullets = [bullet for bullet in self.bullets if not bullet.delete_me]

        for particle in self.particles:
            particle[0].update(delta)
        self.particles = [particle for particle in self.particles if not particle[0].finished]

    def render(self, display):
        for platform in self.platforms:
            pygame.draw.rect(display, shared.Color.WHITE, platform)
        display.blit(self.player.get_frame(), self.player.position.as_tuple())

        for bullet in self.bullets:
            pygame.draw.rect(display, shared.Color.WHITE, bullet.get_hitbox())

        for particle in self.particles:
            display.blit(particle[0].get_frame(), particle[1])
