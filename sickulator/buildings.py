import pygame as pg

vec2 = pg.Vector2

class Building:
    """
    type - 'home' or 'work'
    """
    def __init__(self, x, y, type):
        self.pos = vec2(x,y)
        self.type = type




addresses = [(4, 4),
(11, 4),
(18, 4),
(25, 4),
(49, 6),
(4, 12),
(11, 12),
(18, 12),
(25, 12),
(44, 19),
(4, 22),
(11, 22),
(18, 22),
(25, 22),
(36, 23),
(54, 23),
(4, 30),
(11, 30),
(18, 30),
(25, 30),
(54, 30),
(38, 36),
(4, 40),
(11, 40),
(18, 40),
(25, 40)]