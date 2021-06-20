# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 2
# Collisions and Tilemaps
# Video link: https://youtu.be/ajR4BZBKTr4
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import os
from game import Game
os.environ["SDL_VIDEODRIVER"]="x11"
os.environ['SDL_AUDIODRIVER'] = 'dsp'







if __name__ == "__main__":
    # create the game object
    g = Game()
    g.show_start_screen()
