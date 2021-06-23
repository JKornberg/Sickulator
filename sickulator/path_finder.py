from grid import grid # For testing purposes
from copy import copy
PATH_NUMBER = 2
WIDTH = 64
HEIGHT = 48


class Tile:
    def __init__(self, col, row, type):
        self.col = col
        self.row = row
        self.path = []
        self.status = 'Unknown'
        self.visited = False
        self.type = type


class PathFinder:
    def __init__(self):
        self.grid = self.create_grid()
        self.queue = []


    def create_grid(self):
        map = []
        for col in range(len(grid[0])):
            tiles = []
            for row in range(len(grid)):
                tile = Tile(col, row, grid[row][col])
                if grid[row][col] == 2:
                    print("Home Coord:", col, row)
                tiles.append(tile)
            map.append(tiles)

        return map

    def add_all_neighbors(self):
        for row in self.grid:
            for tile in row:
                tile.add_neighbors(self.map)

    def find_path(self, start, end):
        starting_col = start[0]
        starting_row = start[1]
        starting_tile = self.grid[starting_row][starting_col]

        # Set up ending tile
        ending_col = end[0]
        ending_row = end[1]
        self.grid[ending_col][ending_row].type = "END"

        directions = ["North", "East", "South", "West"]
        self.queue.append(starting_tile)

        while (len(self.queue) > 0):
            current_tile = self.queue.pop(0)
            for dir in directions:
                new_tile = self.explore_direction(current_tile, dir)
                if new_tile.status == "Goal":
                    return new_tile.path
                elif new_tile.status == "Valid":
                    self.queue.append(new_tile)

        return False  # No Path Found

    def explore_direction(self, current_tile, direction):
        new_path = copy(current_tile.path)
        new_path.append(direction)

        x, y = current_tile.col, current_tile.row

        if (direction == 'North'):
            y -= 1
        elif (direction == 'East'):
            x += 1
        elif (direction == 'South'):
            y += 1
        elif (direction == 'West'):
            x -= 1

        next_tile = self.grid[y][x]

        next_tile.status = self.get_tile_status(next_tile)

        if next_tile.status == "Valid":
            next_tile.visited = True

        return next_tile

    def get_tile_status(self, tile):
        x = tile.col
        y = tile.row

        if (x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT):
            return "Invalid"
        elif tile.type == "END":
            return "Goal"
        elif tile.type != PATH_NUMBER or tile.visited:
            return "Blocked"
        else:
            return "Valid"


if __name__== "__main__":
    path_finder = PathFinder()
    starting_coords, ending_coords = (8, 11), (22, 11)
    path = path_finder.find_path(starting_coords, ending_coords)
    print(path)