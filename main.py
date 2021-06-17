import pygame
import os


# Class for the main game. Contains game loop and rendering code
class Game:
    # Screen size constants
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 360
    DISPLAY_WIDTH = 640
    DISPLAY_HEIGHT = 360

    # Timekeeping constants
    TARGET_FPS = 60
    SECOND = 1000
    UPDATE_TIME = SECOND / 60.0

    # Color constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    def __init__(self):
        # Init pygame window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.screen = pygame.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT), 0, 32)
        self.display = pygame.Surface((Game.DISPLAY_WIDTH, Game.DISPLAY_HEIGHT))
        self.clock = pygame.time.Clock()

        # Init timekeeping variables
        self.frames = 0
        self.fps = 0
        self.delta = 0
        self.after_time = 0
        self.before_time = 0
        self.before_sec = 0

        # Init fonts
        pygame.font.init()
        self.fonts = {}

        self.running = False

    # Runs main game loop
    def loop(self):
        self.running = True
        while self.running:
            self.handle_input()
            self.render_clear()
            self.render_text("FPS: " + str(self.fps), 0, 0, Game.WHITE, 10)
            self.render_flip()
            self.clock_tick()

    # Polls and handles pygame events
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False

    # Renders text onto the display buffer
    # Will center text if the x or y coordinate on that axis is -1
    # A new font will be loaded if a font of the given size doesn't exist
    def render_text(self, text, x, y, color, size):
        if size not in self.fonts.keys():
            self.fonts[size] = pygame.font.Font('./res/hack.ttf', size)
        to_render = self.fonts[size].render(text, False, color)

        render_x = x
        if render_x == -1:
            render_x = (Game.DISPLAY_WIDTH / 2) - (to_render.get_width() / 2)
        render_y = y
        if render_y == -1:
            render_y = (Game.DISPLAY_HEIGHT / 2) - (to_render.get_height() / 2)

        self.display.blit(to_render, (render_x, render_y))

    # Clears the display buffer
    def render_clear(self):
        pygame.draw.rect(self.display, Game.BLACK, (0, 0, Game.DISPLAY_WIDTH, Game.DISPLAY_HEIGHT), False)

    # Renders the display buffer onto the screen
    def render_flip(self):
        pygame.transform.scale(self.display, (Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT), self.screen)
        pygame.display.flip()
        self.frames += 1

    # Updates timekeep variables and calls pygame to sleep as needed to maintain target FPS
    def clock_tick(self):
        # Update delta based on the time elapsed
        self.after_time = pygame.time.get_ticks()
        self.delta = (self.after_time - self.before_time) / Game.UPDATE_TIME

        # Update the FPS if a second has passed
        if self.after_time - self.before_sec >= Game.SECOND:
            self.fps = self.frames
            self.frames = 0
            self.before_sec += Game.SECOND

        # Reset timer for next frame
        self.before_time = pygame.time.get_ticks()

        # Update pygame clock (will sleep as needed to maintain FPS)
        self.clock.tick(Game.TARGET_FPS)


if __name__ == "__main__":
    game = Game()
    game.loop()
