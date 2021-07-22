import pygame

sfx = {}


def load_all():
    global sfx

    sfx = {
        'player_jump': pygame.mixer.Sound('./res/sfx/player_jump.wav'),
        'player_shoot': pygame.mixer.Sound('./res/sfx/player_shoot.wav')
    }


def play(name):
    sfx[name].play()
