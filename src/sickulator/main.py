import os
import sys
sys.path.append(os.getcwd())

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from sickulator.game import Game
os.environ["SDL_VIDEODRIVER"]="x11"
os.environ['SDL_AUDIODRIVER'] = 'dsp'
from pathlib import Path

def main():
    g = Game()
    g.show_start_screen()
    
if __name__ == "__main__":
    main()    # create the game object

