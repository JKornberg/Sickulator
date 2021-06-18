# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 2
# Collisions and Tilemaps
# Video link: https://youtu.be/ajR4BZBKTr4
import pygame as pg
import sys
from os import path
from settings import HEIGHT, WIDTH, UISCALE
from sprites import *
from tiles import *
import pygame_menu
from menus import *
import os
#os.environ["SDL_VIDEODRIVER"]="x11"
#os.environ['SDL_AUDIODRIVER'] = 'dsp'
class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # Creates physical game window
        pg.display.set_caption("test")
        pg.key.set_repeat(500, 100)  # Determines how held keys are handled (delay, interval) in ms
        self.home = homeMenu(lambda : self._update_from_selection(2))
        self.current = 0
        self.options = optionsMenu(lambda : self._update_from_selection(3))

    def run(self):
        self.simulation = Simulation(self)
        self.simulation.run()


    def quit(self):
        pg.quit()
        sys.exit()

    def show_start_screen(self):
        self.home.mainloop(self.screen)


    def show_go_screen(self):
        pass

    def _update_from_selection(self, index: int) -> None:
        """
        Change widgets depending on index.
        :param index: Index
        :return: None
        """
        self.current = index
        # Swap buttons using hide/show
        if index == 2:
            self.options.enable()
            self.options.mainloop(self.screen)
            self.home.disable()

        elif index == 3:
            self.home.disable()
            self.options.disable()
            g.run()

class Simulation:
    def __init__(self,game):
        self.game = game
        self.screen = game.screen
        self.load_data()
        self.clock = pg.time.Clock()
        self.ui = uiMenu()
        self.uiSurf = pg.Surface((WIDTH,HEIGHT * UISCALE))
        self.new()

    def load_data(self):
            '''Load all assets'''
            game_folder = path.dirname(__file__)
            map_folder = path.join(game_folder, 'map')
            self.map = TiledMap(path.join(map_folder, 'galletcitymap.tmx'))
            self.map_img = self.map.make_map()
            self.map_rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        #for row, tiles in enumerate(self.map_data):
        #   for col, tile in enumerate(tiles):
        #      if tile == '1':
        #         Wall(self, col, row)
            #    if tile == 'P':
            #       self.player = Player(self, col, row)
        self.player = Player(self, 5,5)
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            events = self.events()
            self.update()
            self.draw()
            self.ui.update(events)
            self.ui.draw(self.uiSurf, clear_surface=True)
            self.screen.blit(self.uiSurf,(0,1+HEIGHT-HEIGHT*.15))
            pg.display.flip()
            pg.display.update()


    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

    def events(self):
        # catch all events here
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_LEFT:
                    self.player.move(dx=-1)
                if event.key == pg.K_RIGHT:
                    self.player.move(dx=1)
                if event.key == pg.K_UP:
                    self.player.move(dy=-1)
                if event.key == pg.K_DOWN:
                    self.player.move(dy=1)
        return events

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        #self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #self.draw_grid()
        self.all_sprites.draw(self.screen)


if __name__ == "__main__":
    # create the game object
    g = Game()
    g.show_start_screen()
