import pygame
import shared


# An array of named animation frames
frame_data = {}
whitemasked_frame_data = {}


# Loads an animation from a given path
def load(path, frame_size, has_alpha=True):
    # load animation source sheet
    sprite_sheet = pygame.image.load(path)
    if has_alpha:
        sprite_sheet.convert_alpha()
    else:
        sprite_sheet.convert()

    # split source sheet into an array of individual frames
    frames = []
    frame_count = (sprite_sheet.get_width() / frame_size[0]) * (sprite_sheet.get_height() / frame_size[1])
    frame_x = 0
    frame_y = 0
    while len(frames) != frame_count:
        frames.append(sprite_sheet.subsurface((frame_x, frame_y) + frame_size))

        frame_x += frame_size[0]
        if frame_x == sprite_sheet.get_width():
            frame_x = 0
            frame_y += frame_size[1]

    return frames


def load_static(path, has_alpha=True):
    sprite = pygame.image.load(path)
    if has_alpha:
        sprite.convert_alpha()
    else:
        sprite.convert()

    return [sprite]


# Returns a copy of an animation but each pixel is white
# This is used to create an "enemies flashing white when they get hurt effect"
# Normally you would probably use shaders for this, but pygame doesn't give us a nice way to implement those,
# and I figured pre-generating copies of the animations upfront would be kinder on the game's FPS than trying to do per-pixel software rendering in real time
def generate_whitemask(source_animation):
    whitemask = []
    for frame in source_animation:
        whitemasked_frame = pygame.Surface(frame.get_size(), pygame.SRCALPHA, 32)
        for x in range(0, frame.get_width()):
            for y in range(0, frame.get_height()):
                if frame.get_at((x, y)).a != 0:
                    whitemasked_frame.set_at((x, y), pygame.Color(255, 255, 255, 255))
        whitemask.append(whitemasked_frame)

    return whitemask


# Loads all the animations
# This is placed here so that it can be called explicitly after pygame has initialized, otherwise some of the image loading functions will fail
def load_all():
    global frame_data, whitemasked_frame_data

    frame_data = {
        'player_run': load('./res/player_run.png', (32, 32), True),
        'player_jump': load('./res/player_jump.png', (32, 32), True),
        'player_liftoff': load('./res/player_liftoff.png', (32, 32), True),
        'bullet': load_static('./res/bullet.png', True),
        'carrot_run': load('./res/carrot.png', (32, 32), True),
        'onion_run': load('./res/onion_run.png', (32, 32), True),
        'onion_attack': load('./res/onion_attack.png', (32, 32), True),
        'object_floor': load_static('./res/object_floor.png', False),
        'object_platform': load_static('./res/object_platform.png', False),
        'tiles': load('./res/tileset.png', (shared.TILE_SIZE, shared.TILE_SIZE), False)
    }

    whitemasked_frame_data = {
        'player_run': generate_whitemask(frame_data['player_run']),
        'player_jump': generate_whitemask(frame_data['player_jump']),
        'onion_run': generate_whitemask(frame_data['onion_run']),
        'onion_attack': generate_whitemask(frame_data['onion_attack'])
    }


#  An instance of an animation. Refers to the frames of an animation without actually storing duplicate loaded images
class Animation:
    def __init__(self, name, fps):
        self.name = name
        self.set_fps(fps)
        self.reset()
        self.flip_h = False
        self.finished = False
        self.whitemask = False

    def set_fps(self, fps):
        self.frame_duration = 60.0 / fps

    def reset(self):
        self.timer = 0
        self.frame = 0

    def update(self, delta):
        self.timer += delta
        while self.timer >= self.frame_duration:
            self.timer -= self.frame_duration
            self.frame += 1
            if self.frame >= len(frame_data[self.name]):
                self.frame = 0
                self.finished = True

    def get_frame(self):
        frame = None
        if self.whitemask:
            frame = whitemasked_frame_data[self.name][self.frame]
        else:
            frame = frame_data[self.name][self.frame]
        return pygame.transform.flip(frame, self.flip_h, False)

    def get_frame_at(self, index):
        frame = None
        if self.whitemask:
            frame = whitemasked_frame_data[self.name][index]
        else:
            frame = frame_data[self.name][index]
        return pygame.transform.flip(frame, self.flip_h, False)
