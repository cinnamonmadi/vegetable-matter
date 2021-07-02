import pygame

PLAYER_LEFT = 0
PLAYER_RIGHT = 1
PLAYER_JUMP = 2
PLAYER_SHOOT = 3

is_pressed = [False] * 4
is_just_pressed = [False] * 4
is_just_released = [False] * 4

current_joystick = -1
keymapping = {}


def reset_to_defaults():
    global current_joystick, keymapping

    current_joystick = -1
    keymapping[-1] = {
        pygame.K_a: PLAYER_LEFT,
        pygame.K_d: PLAYER_RIGHT,
        pygame.K_SPACE: PLAYER_JUMP,
        pygame.K_l: PLAYER_SHOOT
    }


def reset_all():
    global is_pressed

    is_pressed = [False] * len(is_pressed)
    flush_events()


def flush_events():
    global is_just_pressed, is_just_released

    is_just_pressed = [False] * len(is_just_pressed)
    is_just_released = [False] * len(is_just_released)


def handle(event):
    global is_pressed, is_just_pressed, is_just_released

    if event.type == pygame.KEYDOWN and current_joystick == -1:
        if event.key in keymapping[-1].keys():
            is_pressed[keymapping[-1][event.key]] = True
            is_just_pressed[keymapping[-1][event.key]] = True
    elif event.type == pygame.KEYUP and current_joystick == -1:
        if event.key in keymapping[-1].keys():
            is_pressed[keymapping[-1][event.key]] = False
            is_just_released[keymapping[-1][event.key]] = True
