import pygame
import shared
import player
import enemy


# The level state class
class Level:
    def __init__(self):
        self.player = player.Player()
        self.player.position = shared.Vector(32, 200)

        self.platforms = [(0, 300, 640, 60), (200, 260, 100, 10)]
        self.enemies = []
        self.particles = []
        self.bullets = []

        new_enemy = enemy.Onion()
        new_enemy.position = shared.Vector(550, 200)
        self.enemies.append(new_enemy)

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
        self.particles += self.player.get_particles()
        if pygame.key.get_pressed()[pygame.K_l]:
            new_bullet = self.player.shoot()
            if new_bullet is not None:
                self.bullets.append(new_bullet)

        for enemy_obj in self.enemies:
            enemy_obj.update(delta, self.player.get_hitbox(), self.platforms)

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

    def render(self, display):
        for platform in self.platforms:
            pygame.draw.rect(display, shared.Color.WHITE, platform)
        display.blit(self.player.get_frame(), self.player.position.as_tuple())

        for enemy_obj in self.enemies:
            display.blit(enemy_obj.get_frame(), enemy_obj.position.as_tuple())

        for bullet in self.bullets:
            display.blit(bullet.get_frame(), bullet.position.as_tuple())

        for particle in self.particles:
            display.blit(particle[0].get_frame(), particle[1])
