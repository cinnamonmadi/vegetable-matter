import pygame
import os
import sys
import shared
import animation
import level
import animviewer


# Class for the main game. Contains game loop and rendering code
class Game:
    # Screen size constants
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    DISPLAY_WIDTH = 640
    DISPLAY_HEIGHT = 360

    # Timekeeping constants
    TARGET_FPS = 60
    SECOND = 1000
    UPDATE_TIME = SECOND / 60.0

    def __init__(self):
        self.read_sys_args()

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
        self.debug_font = pygame.font.Font('./res/hack.ttf', 10)

        # Init animations
        animation.load_all()

        self.running = False

    # Read and handle system arguments
    def read_sys_args(self):
        self.current_state = None
        for i in range(0, len(sys.argv)):
            if sys.argv[i] == "--animviewer":
                self.current_state = animviewer.AnimViewer(sys.argv[i + 1])

    # Runs main game loop
    def loop(self):
        self.running = True
        if self.current_state is None:
            self.current_state = level.Level()
        while self.running:
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False
                else:
                    self.current_state.handle_input(event)

            # Update
            self.current_state.update(self.delta)

            # Render
            self.render_clear()
            self.current_state.render(self.display)
            self.render_fps()
            self.render_flip()

            # Timekeep
            self.clock_tick()

    # Renders text onto the display buffer
    # Will center text if the x or y coordinate on that axis is -1
    # A new font will be loaded if a font of the given size doesn't exist
    def render_fps(self):
        to_render = self.debug_font.render("FPS: " + str(self.fps), False, shared.Color.WHITE)
        self.display.blit(to_render, (0, 0))

    # Clears the display buffer
    def render_clear(self):
        pygame.draw.rect(self.display, shared.Color.BLACK, (0, 0, Game.DISPLAY_WIDTH, Game.DISPLAY_HEIGHT), False)

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
