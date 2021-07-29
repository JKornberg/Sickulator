from sickulator.simulation import Simulation
from sickulator.settings import HEIGHT, WIDTH, UISCALE, SimulationSettings
import sys
import pygame as pg
from sickulator.menus import *
import pygame_menu
import pickle
import os
from os import path
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt


class Game:
    def __init__(self):
        self.simulation_settings: SimulationSettings = SimulationSettings()
        _stdout = sys.stdout
        _stderr = sys.stderr
        sys.stdout = sys.stderr = None
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # Creates physical game window
        sys.stdout = _stdout
        sys.stderr = _stderr
        pg.display.set_caption("The Sickulator")
        pg.key.set_repeat(500, 100)  # Held key handler
        self.current = 0  # Current page index
        self.home = homeMenu(lambda : self._update_from_selection(2), lambda : self._update_from_selection(4))
        self.options = optionsMenu(self, lambda : self._update_from_selection(1))
        self.data_menu = dataMenu(lambda : self._update_from_selection(1), self.save_result_image)

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
        if index == 1:
            self.options.disable()
            self.data_menu.disable()
            self.home.enable()
            self.home.mainloop(self.screen)
        if index == 2:
            self.options.enable()
            self.options.mainloop(self.screen)
            self.home.disable()
        elif index == 3:
            self.home.disable()
            self.options.disable()
            self.run()
        elif index == 4:
            self.home.disable()
            self.options.disable()
            data_menu = dataMenu(lambda : self._update_from_selection(1), self.save_result_image)
            data_menu.mainloop(self.screen)

    def set_settings(self, simulation_settings: SimulationSettings):
        self.simulation_settings = simulation_settings

    def play_simulation(self, simulation_settings):
        self.set_settings(simulation_settings)
        self._update_from_selection(3)

    def end_simulation(self, daily_stats, cumulative_stats):
        self.save_to_results(daily_stats, cumulative_stats)
        has_image = True
        if len(daily_stats) > 0:
            self.save_result_image({'date': datetime.now(), 'infection_rate': self.simulation_settings.infection_rate,
                                    'daily_stats': daily_stats}, 'temp_results.png')
        else:
            has_image = False
        results = resultsMenu(daily_stats,cumulative_stats, has_image, lambda : self._update_from_selection(1))
        results.mainloop(self.screen)

    def save_to_results(self, daily_stats, cumulative_stats):
        obj = []
        location = path.dirname(os.path.realpath(__file__))
        file = path.join(location, 'data', 'data.txt')
        try:
            with open(file, "rb") as f:
                obj = pickle.load(f)
        except:
            print("No data.txt file found. Creating new file")
            if not os.path.isdir(path.join(location, 'data')):
                os.mkdir(path.join(location, 'data'))
        max_infection = 0
        for h, s, i, d in daily_stats:
            if (h + s == 0):
                continue
            max_infection = y if (y:=s/(h+s)) > max_infection else max_infection
        result = {'date': datetime.now(), 'daily_stats': daily_stats, 'cumulative_stats' : cumulative_stats, 'infection_rate' : self.simulation_settings.infection_rate}
        obj.append(result)
        with open(file, "wb") as f:
            pickle.dump(obj, f)


    def save_result_image(self, results, fileName):
        try:
            daily_stats = results['daily_stats']
            infection_rate = results['infection_rate']
            location = path.dirname(os.path.realpath(__file__))
            file = path.join(location,'data',fileName)
            if not os.path.isdir(path.join(location,'data')):
                os.mkdir(path.join(location,'data'))
            if len(daily_stats) > 1:
                x = range(len(daily_stats))
                #y = list(zip(*daily_stats))
                y = [[daily_stats[j][i] for j in range(len(daily_stats))] for i in range(len(daily_stats[0]))]
                #self.simulation_settings.infection_rate
                plt.clf()
                # Green, Red, Blue, Black #
                pal = ["#00ff40", "#f7020f", "#0a53f2", "#0a140c"]
                plt.stackplot(x, y, labels=['Healthy', 'Infected', 'Immune', 'Deceased'], colors=pal)
                plt.title('Agent Population with Infection Rate: ' + str(infection_rate) + '%')
                plt.legend(loc='upper left')
                plt.xlabel('Time (days of simulation passed)',)
                plt.ylabel('Number of agents')
                plt.savefig(file, dpi=100)
            elif len(daily_stats) == 1:
                label = "Day 0"
                plt.clf()
                # Green, Red, Blue, Black #
                pal = ["#00ff40", "#f7020f", "#0a53f2", "#0a140c"]
                plt.bar(label, daily_stats[0][0], label="Healthy", color=pal[0])
                plt.bar(label, daily_stats[0][1], label="Infected", color=pal[1])
                plt.bar(label, daily_stats[0][2], label="Immune", color=pal[2])
                plt.bar(label, daily_stats[0][3], label="Dead", color=pal[3])
                plt.title('Initial Stats')
                plt.legend(loc='upper left')
                plt.ylabel('Number of agents')
                plt.savefig(file, dpi=100)
        except Exception as e:
            print("Could not save result image")
            