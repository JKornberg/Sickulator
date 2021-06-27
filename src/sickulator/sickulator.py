import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from game import Game
os.environ["SDL_VIDEODRIVER"]="x11"
os.environ['SDL_AUDIODRIVER'] = 'dsp'

def main():
    g = Game()
    g.show_start_screen()
    
if __name__ == "__main__":
    main()    # create the game object

