# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 2
# Collisions and Tilemaps
# Video link: https://youtu.be/ajR4BZBKTr4
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import contextlib
import pygame as pg
import sys
from os import path
from pygame_gui.elements import text
from settings import HEIGHT, WIDTH, UISCALE
from sprites import *
from tiles import *
import pygame_menu
from menus import *
import os
import pygame_gui
from math import floor
os.environ["SDL_VIDEODRIVER"]="x11"
os.environ['SDL_AUDIODRIVER'] = 'dsp'

class Game:
    def __init__(self):
        _stdout = sys.stdout
        _stderr = sys.stderr
        sys.stdout = sys.stderr = None
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # Creates physical game window
        pg.display.set_caption("The Sickulator")
        pg.key.set_repeat(500, 100)  # Determines how held keys are handled (delay, interval) in ms
        self.home = homeMenu(lambda : self._update_from_selection(2))
        self.current = 0
        self.options = optionsMenu(lambda : self._update_from_selection(3))
        sys.stdout = _stdout
        sys.stderr = _stderr

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
        self.show = False
        self.clock = pg.time.Clock()
        self.new()
        self.multiplier = 1


    def enable_popup(self):
        print("PRESSED")
        self.show = True
        
    def load_data(self):
        '''Load all assets'''
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'map')
        self.map = TiledMap(path.join(map_folder, 'agentcity.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.player = Player(self, 5,5)
        self.camera = Camera(self.map.width, self.map.height)
        self.gui = pygame_gui.UIManager((WIDTH, HEIGHT),theme_path='theme.json')
        self.make_gui()

    def make_gui(self):
        bottom_bar = pygame_gui.elements.UIPanel(relative_rect=pg.Rect((0, HEIGHT-80), (WIDTH, 80)),starting_layer_height=0,
                                             manager=self.gui)


        self.info_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((0, 0), (50, 50)),text="Info",
                                             manager=self.gui,container=bottom_bar)

        self.timer = pygame_gui.elements.UILabel(relative_rect=pg.Rect((100, 0), (100,50)), text="Day: 0",container=bottom_bar, manager=self.gui)
        self.half_speed_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((200, 0), (50, 50)),text="0.5x",
                                             manager=self.gui,container=bottom_bar)
        self.normal_speed_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((250, 0), (50, 50)),text="*1x*",
                                             manager=self.gui,container=bottom_bar)
        self.double_speed_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((300, 0), (50, 50)),text="2x",
                                             manager=self.gui,container=bottom_bar)
        self.info = pygame_gui.elements.UIPanel(relative_rect=pg.Rect((0, 0), (350, HEIGHT-80)),starting_layer_height=0, manager=self.gui, visible=False)
        self.close_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((350-30,0), (30, 30)),text="X",
                                             manager=self.gui,container=self.info, visible=False)                                    


    def toggle_info(self, val):
        self.info.visible = val
        self.close_button.visible = val

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        self.time = 0
        while self.playing:
            #print(self.show)
            self.dt = (self.clock.tick(FPS) / 1000) * self.multiplier
            self.time += self.dt
            self.events()
            self.update()
            self.draw()
            self.gui.update(self.dt)
            self.gui.draw_ui(self.screen)
            pg.display.flip()
            pg.display.update()


    def update(self):
        # update portion of the game loop
        self.timer.set_text("Day: " + str(floor(self.time/10)))
        self.all_sprites.update()
        self.camera.update(self.player)


    def events(self):
        # catch all events here
        events = pg.event.get()
        for event in events:
            self.gui.process_events(event)
            
            if event.type == pg.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.info_button:
                        self.toggle_info(True)
                    elif event.ui_element == self.close_button:
                        self.toggle_info(False)
                    elif event.ui_element == self.half_speed_button:
                        self.half_speed_button.set_text("*0.5x*")
                        self.normal_speed_button.set_text("1x")
                        self.double_speed_button.set_text("2x")
                        self.multiplier = 0.5  
                    elif event.ui_element == self.normal_speed_button:
                        self.half_speed_button.set_text("0.5x")
                        self.normal_speed_button.set_text("*1x*")
                        self.double_speed_button.set_text("2x")
                        self.multiplier = 1                        
                    elif event.ui_element == self.double_speed_button:
                        self.half_speed_button.set_text("0.5x")
                        self.normal_speed_button.set_text("1x")
                        self.double_speed_button.set_text("*2x*")
                        self.multiplier = 2     
            if event.type == pg.QUIT:
                self.playing = False
                self.quit()
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.playing = False
                    pg.quit()
                    sys.exit()
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
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.all_sprites.draw(self.screen)

    def quit(self):
        pg.quit()

if __name__ == "__main__":
    # create the game object
    g = Game()
    g.show_start_screen()
