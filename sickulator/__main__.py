# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 2
# Collisions and Tilemaps
# Video link: https://youtu.be/ajR4BZBKTr4
import pygame as pg
import sys
from os import path

from .settings import *
from .sprites import *
from .menus import homeMenu, optionsMenu, uiMenu
from pytmx.util_pygame import load_pygame


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # Creates physical game window
        pg.display.set_caption("test")
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)  # Determines how held keys are handled (delay, interval) in ms
        self.map_data = load_pygame('sickulator/map/map.tmx')
        self.home = homeMenu(lambda : self._update_from_selection(2))
        self.current = 0
        self.options = optionsMenu(lambda : self._update_from_selection(3))
        self.uiSurf = pg.Surface((WIDTH,HEIGHT * UISCALE))
        self.ui = uiMenu()
        


    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)

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
            self.screen.blit(self.uiSurf,(0,0))
            pg.display.flip()
            pg.display.update()


    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()


    def draw(self):
        for layer in self.map_data.layers:
            for x, y, image in layer.tiles():
                print(x, y, image) # What to do here?
       
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
            self.ui.enable()
            g.new()
            g.run()


# create the game object

if __name__ == "__main__":
    g = Game()
    g.show_start_screen()
