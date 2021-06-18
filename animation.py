import pygame


# An array of named animation frames
frame_data = {}


# Loads an animation from a given path
def load(path, frame_count, frame_size, has_alpha=True):
    # load animation source sheet
    sprite_sheet = pygame.image.load(path)
    if has_alpha:
        sprite_sheet.convert_alpha()
    else:
        sprite_sheet.convert()

    # split source sheet into an array of individual frames
    frames = []
    frame_x = 0
    frame_y = 0
    while len(frames) != frame_count:
        frames.append(sprite_sheet.subsurface((frame_x, frame_y) + frame_size))

        frame_x += frame_size[0]
        if frame_x == sprite_sheet.get_width():
            frame_x = 0
            frame_y += frame_size[1]

    return frames


# Loads all the animations
# This is placed here so that it can be called explicitly after pygame has initialized, otherwise some of the image loading functions will fail
def load_all():
    global frame_data

    frame_data = {
        'slime_move': load('./res/slime_move.png', 5, (64, 64), True)
    }


#  An instance of an animation. Refers to the frames of an animation without actually storing duplicate loaded images
class Animation:
    def __init__(self, name, fps):
        self.name = name
        self.set_fps(fps)
        self.reset()

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

    def get_frame(self):
        return frame_data[self.name][self.frame]
