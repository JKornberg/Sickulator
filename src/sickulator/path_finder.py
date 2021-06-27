from copy import copy

PATH_NUMBER = 25
DOOR = 39
WIDTH = 64
HEIGHT = 48

""" 
Grid is a 2d array like 

[
    [col1, col2, col3],
    [row 2], 
    [row 3]
]

so grid[0][0] is the top left corner
grid[1][0] is the second row, first column
grid[0][1] is the first row, second column
etc...
"""


class Tile:
    def __init__(self, col, row, type):
        self.col = col
        self.row = row
        self.path = []
        self.status = "Unknown"
        self.visited = False
        self.type = type


class PathFinder:
    def __init__(self, grid):
        self.grid = grid
        self.map = self.create_grid()
        self.queue = []

    def create_grid(self):
        map = []
        for row in range(len(self.grid)):
            tiles = []
            for col in range(len(self.grid[0])):
                tile = Tile(col, row, self.grid[row][col])
                tiles.append(tile)
            map.append(tiles)
        return map

    def find_path(self, start, end):
        if start == end:
            return [start]

        starting_col = start[0]
        starting_row = start[1]
        starting_tile = self.map[int(starting_row)][int(starting_col)]

        # Set up ending tile
        ending_col = end[0]
        ending_row = end[1]
        self.map[ending_row][ending_col].type = "END"

        directions = ["North", "East", "South", "West"]
        self.queue.append(starting_tile)

        while len(self.queue) > 0:
            current_tile = self.queue.pop(0)
            for dir in directions:
                new_tile = self.explore_direction(current_tile, dir)
                if new_tile and new_tile.status == "Goal":
                    new_tile.path.append((ending_col, ending_row))
                    self.reset_grid()
                    return new_tile.path
                elif new_tile and new_tile.status == "Valid":
                    self.queue.append(new_tile)

        self.reset_grid()
        return False  # No Path Found

    def reset_grid(self):
        self.map = self.create_grid()
        self.queue = []

    def explore_direction(self, current_tile, direction):
        new_path = copy(current_tile.path)
        new_path.append((current_tile.col, current_tile.row))

        x, y = current_tile.col, current_tile.row

        if direction == "North":
            y -= 1
        elif direction == "East":
            x += 1
        elif direction == "South":
            y += 1
        elif direction == "West":
            x -= 1

        try:
            next_tile = self.map[y][x]
        except IndexError:
            return None

        next_tile.status = self.get_tile_status(next_tile)
        next_tile.path = new_path

        if next_tile.status == "Valid":
            next_tile.visited = True

        return next_tile

    def get_tile_status(self, tile):
        x = tile.col
        y = tile.row

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return "Invalid"
        elif tile.type == "END":
            return "Goal"
        elif tile.type != PATH_NUMBER and tile.type != DOOR or tile.visited:
            return "Blocked"
        else:
            return "Valid"


## DEBUG
# if __name__== "__main__":
#     path_finder = PathFinder()
#     starting_coords, ending_coords = (4, 5), (46, 47)
#     path = path_finder.find_path(starting_coords, ending_coords)
