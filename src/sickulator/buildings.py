import pygame as pg

vec2 = pg.Vector2


class Building:
    """
    type - 'home' or 'work'
    """

    def __init__(self, x, y, type, id):
        self.pos = vec2(x, y)
        self.type = type
        self.id = id

    """
    def create_homes(self):
        self.homes = []
        for x in range(0, len(home_addresses) - 1):
            self.homes.append(Building(home_addresses[x][0], home_addresses[x][1], "home"))
    
    def create_buildings(self):
        self.buildings = []
        for x in range(0, len(building_addresses)):
            if x < 6: # index of park addresses start on 6
                self.buildings.append(Building(building_addresses[x][0], building_addresses[x][1], "inside"))
            else:
                self.buildings.append(Building(building_addresses[x][0], building_addresses[x][1], "outside"))
    """


# home x-coord < 30
# building x-coord > 30


home_addresses = [
    (4, 4),
    (11, 4),
    (18, 4),
    (25, 4),
    (4, 12),
    (11, 12),
    (18, 12),
    (25, 12),
    (4, 22),
    (11, 22),
    (18, 22),
    (25, 22),
    (4, 30),
    (11, 30),
    (18, 30),
    (25, 30),
    (4, 40),
    (11, 40),
    (18, 40),
    (25, 40),
]

building_addresses = [
    (49, 6),
    (44, 19),
    (36, 23),
    (54, 23),
    (54, 30),
    (38, 36),
    (37, 8),
    (61, 6),
    (48, 43),
]

# (37, 8) = north park
# (61, 6) = baseball field
# (48,43) = southern park
