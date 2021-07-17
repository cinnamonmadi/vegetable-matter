import pygame

sfx = {}


def load_all():
    global sfx

    sfx = {
        'player_jump': pygame.mixer.Sound('./res/sfx/player_jump.wav'),
        'player_shoot': pygame.mixer.Sound('./res/sfx/player_shoot.wav')
    }

    sfx['player_shoot'].set_volume(0.3)


def play(name):
    sfx[name].play()
