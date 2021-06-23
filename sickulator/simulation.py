import math
from os import path
from agent import Agent
from typing import Container
from tiles import *
from sprites import  *
import pygame_gui
from pygame_gui.elements import text
from math import floor
import sys
import pytmx
class Simulation:
    def __init__(self,game):
        self.game = game
        self.screen = game.screen
        self.load_data()
        self.show = False
        self.clock = pg.time.Clock()
        self.new()
        self.multiplier = 1
        self.day = 0
        self.simulation_settings = game.simulation_settings
        self.show_popup = False

    def enable_popup(self):
        print("PRESSED")
        self.show = True
        
    def load_data(self):
        '''Load all assets'''
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'map')
        self.map = TiledMap(path.join(map_folder, 'agentcity.tmx'))
        # following 2 lines added for generate_path_grid() function
        self.path_map = TiledMap(path.join(map_folder,'path_Map.tmx'))
        self.generate_path_grid()
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.player = Player(self, 5,5)

        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)

        self.camera = Camera(self.map.width, self.map.height)
        self.gui = pygame_gui.UIManager((WIDTH, HEIGHT),theme_path='theme.json')
        self.make_gui()

    def make_gui(self):
        bottom_bar = pygame_gui.elements.UIPanel(relative_rect=pg.Rect((0, HEIGHT-60), (WIDTH, 60)),starting_layer_height=0,
                                             manager=self.gui)


        self.info_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((0, 0), (50, 50)),text="Info",
                                             manager=self.gui,container=bottom_bar)

        self.timer = pygame_gui.elements.UILabel(relative_rect=pg.Rect((100, 0), (100,50)), text="Day: 0",container=bottom_bar, manager=self.gui)
        self.speed_label = pygame_gui.elements.UILabel(relative_rect=pg.Rect((200,0),(150,50)),text="Speed Controls:",container=bottom_bar,manager=self.gui)
        self.half_speed_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((350, 0), (50, 50)),text="0.5x",
                                             manager=self.gui,container=bottom_bar)
        self.normal_speed_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((400, 0), (50, 50)),text="*1x*",
                                             manager=self.gui,container=bottom_bar)
        self.double_speed_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((450, 0), (50, 50)),text="2x",
                                             manager=self.gui,container=bottom_bar)
        self.info = pygame_gui.elements.UIPanel(relative_rect=pg.Rect((0, 0), (350, HEIGHT-80)),starting_layer_height=0, manager=self.gui, visible=False)
        self.close_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((350-30,0), (30, 30)),text="X",
                                             manager=self.gui,container=self.info, visible=False)                                    

        self.description = pygame_gui.elements.UITextBox(html_text=
        """<body>THE SICKULATOR<br>The Sickulator is an agent-based simulator which visualizes the spread of disease in a small city. Agents begin every day at home with their family where they select a schedule for the day. They then venture out to the city and visit all the buildings their schedule includes. A small subset of agents begin the simulation infected, and we can watch the disease spread over time. The health status of an agent is represented by their color. Green is healthy, red is infected, blue is immune, and dark grey is deceased.</body>"""
        ,relative_rect=pg.Rect((0,0),(300,400)),container=self.info,manager=self.gui, layer_starting_height=2)

        self.status = pygame_gui.elements.UITextBox(relative_rect=pg.Rect((0,550),(300,200)),
            html_text=f"""<body>Healthy:  {Agent.health_counts[0]}<br>Infected: {Agent.health_counts[1]}<br>Immune:   {Agent.health_counts[2]}<br>Dead:     {Agent.health_counts[3]}</body>""", container=self.info, manager=self.gui,
            layer_starting_height=2)

        self.end_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((WIDTH-150,0),(120,50)),container=bottom_bar,manager=self.gui,text="End Simulation")

    def toggle_info(self, val):
        self.show_popup = val
        self.info.visible = val
        self.close_button.visible = val
        self.description.visible = val
        self.status.visible = val

    def update_status(self):
        self.status.html_text =f"""<body>Healthy:  {Agent.health_counts[0]}<br>Infected: {Agent.health_counts[1]}<br>Immune:   {Agent.health_counts[2]}<br>Dead:     {Agent.health_counts[3]}</body>"""
        self.status.rebuild() #  This might not be proper

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
        if (self.day != (y:=(floor(self.time/10)))):
            self.day = y
            self.timer.set_text("Day: " + str(self.day))
            if (self.day > self.simulation_settings.simulation_duration):
                self.end_game()
        self.all_sprites.update()
        self.camera.update(self.player)
        if (self.show_popup):
            self.update_status()



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
                    elif event.ui_element == self.end_button:
                        self.end_game()
            if event.type == pg.QUIT:
                self.playing = False
                self.quit()
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.playing = False
                    pg.quit()
                    sys.exit()
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

    def end_game(self):
        self.playing = False
        self.game.end_simulation()

    def quit(self):
        pg.quit()

    # Should create a 2D array out of path_Map.tmx #
    def generate_path_grid(self):
        self.grid = [[0 for x in range(int(self.path_map.width / 16))] for y in range(int(self.path_map.height / 16))]

        print(self.path_map.tmxdata)
        for layer in self.path_map.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    props = self.path_map.tmxdata.get_tile_properties_by_gid(gid)
                    print(props)
                    self.grid[y][x] = gid

        return self.grid

