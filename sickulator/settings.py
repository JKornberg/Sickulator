import pygame as pg

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# game settings
WIDTH = 1024   # originally 1024
HEIGHT = 768 # og 768
FPS = 60
TITLE = "Agent City"
BGCOLOR = DARKGREY

# size of agents/camera
TILESIZE = 8
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
UISCALE = .15

# Camera Settings
PLAYER_SPEED = 100