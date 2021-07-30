import math
import os
from os import path

import pygame
from sickulator.agent import *
from sickulator.tiles import *
from sickulator.sprites import *
import pygame_gui
from pygame_gui.elements import text
from math import floor, ceil
import random
import sys
import pytmx
from sickulator.buildings import *
import random
from sickulator.path_finder import PathFinder
from sickulator.settings import DAY_LENGTH, NIGHT_LENGTH


class Simulation:
    def __init__(self, game):
        Agent.health_counts = [0, 0, 0, 0]
        self.game = game
        self.screen = game.screen
        self.load_data()
        self.show = False
        self.clock = pg.time.Clock()
        self.multiplier = 1
        self.day = 0
        self.simulation_settings = game.simulation_settings
        self.multiplier = 1
        self.show_popup = False
        self.show_sprite_popup = False
        self.paused = False
        self.selected_sprite = None
        self.selected_label = None
        self.daily_stats = []  # [Healthy, Infected, Immune, Dead]
        self.cumulative_stats = [
            0,
            0,
            0,
            self.simulation_settings.agent_count,
        ]  # [Total Killed, Total Immune, Total Infected, Total agents]
        self.path_finder = PathFinder(self.grid)
        self.isDaytime = True
        self.infected_today = 0
        self.camera_point = None
        self.new()

    def enable_popup(self):
        self.show = True

    def load_data(self):
        """Load all assets"""
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, "map")
        self.map = TiledMap(path.join(map_folder, "agentcityO.tmx"))
        # following 2 lines added for generate_path_grid() function
        self.path_map = TiledMap(path.join(map_folder, "path_Map.tmx"))
        self.grid = self.generate_path_grid()
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.camera_sprite = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.player = Player(self, 32, 24)

        # num_agents = 10
        self.families = []
        self.agents = []

        self.homes = []  # create_homes from buildings; better suited here
        for x in range(0, len(home_addresses) - 1):
            new_building = Building(
                int(home_addresses[x][0]),
                int(home_addresses[x][1]),
                home_rectangles[x],
                "inside",
                x,
                self,
                building_class="Home",
            )
            self.homes.append(new_building)

        self.buildings = (
            []
        )  # create_buildings from buildings; better suited here
        for x in range(len(building_addresses)):
            if x < 12:  # index of park addresses start on 6
                self.buildings.append(
                    Building(
                        int(building_addresses[x][0]),
                        int(building_addresses[x][1]),
                        building_rectangles[x],
                        "inside",
                        x,
                        self,
                    )
                )
            else:
                self.buildings.append(
                    Building(
                        int(building_addresses[x][0]),
                        int(building_addresses[x][1]),
                        building_rectangles[x],
                        "outside",
                        x,
                        self,
                    )
                )
        num_of_families = math.ceil(
            self.simulation_settings.agent_count
            / self.simulation_settings.family_size
        )
        for x in range(
            0,
            num_of_families,
        ):  # creates families = number of agents / family_size setting, rounded up (so no agents are left out)
            new_home = self.homes[random.randint(0, len(self.homes)) - 1]
            self.families.append(Family(self, new_home))

        index = 0
        rng = np.random.default_rng()
        random_samples = rng.random(self.simulation_settings.agent_count * 3)
        random_index = 0
        for agent in range(
            0, self.simulation_settings.agent_count
        ):  # puts agents in families; fills families before moving to new ones
            family_to_fill = self.families[
                int(index / self.simulation_settings.family_size)
            ]
            preferences = (
                random_samples[random_index : random_index + 3]
                / random_samples[random_index : random_index + 3].sum()
                * DAY_LENGTH
            )
            random_index += 3
            new_agent = Agent(
                self,
                family_to_fill,
                family_to_fill.home.pos[0],
                family_to_fill.home.pos[1],
                family_to_fill.home.id,
                id=agent,
                preferences=preferences,
            )
            if index == 0:
                new_agent.health_state = HealthState.INFECTED
            family_to_fill.add_agent(new_agent)
            self.agents.append(new_agent)
            index += 1

        generate_schedules(self.agents)

        for agent in self.agents:
            agent.daily_update(True)

        for tile_object in self.map.tmxdata.objects:

            if tile_object.name == "wall":
                Obstacle(
                    self,
                    tile_object.x,
                    tile_object.y,
                    tile_object.width,
                    tile_object.height,
                )

        self.camera = Camera(self.map.width, self.map.height)

        location = path.dirname(os.path.realpath(__file__))
        file = path.join(location, "theme.json")
        self.gui = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path=file)
        self.gui.preload_fonts([{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])
        self.make_gui()

    def make_gui(self):
        bottom_bar = pygame_gui.elements.UIPanel(
            relative_rect=pg.Rect((0, HEIGHT - 60), (WIDTH, 60)),
            starting_layer_height=0,
            manager=self.gui,
        )

        self.info_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((0, 0), (50, 50)),
            text="Info",
            manager=self.gui,
            container=bottom_bar,
        )

        self.timer = pygame_gui.elements.UILabel(
            relative_rect=pg.Rect((100, 0), (100, 50)),
            text="Day: 0",
            container=bottom_bar,
            manager=self.gui,
        )
        self.speed_label = pygame_gui.elements.UILabel(
            relative_rect=pg.Rect((200, 0), (150, 50)),
            text="Speed Controls:",
            container=bottom_bar,
            manager=self.gui,
        )
        self.half_speed_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((350, 0), (50, 50)),
            text="0.5x",
            manager=self.gui,
            container=bottom_bar,
        )
        self.normal_speed_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((400, 0), (50, 50)),
            text="*1x*",
            manager=self.gui,
            container=bottom_bar,
        )
        self.double_speed_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((450, 0), (50, 50)),
            text="2x",
            manager=self.gui,
            container=bottom_bar,
        )
        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((500, 0), (50, 50)),
            text="Pause",
            manager=self.gui,
            container=bottom_bar,
        )
        self.info = pygame_gui.elements.UIPanel(
            relative_rect=pg.Rect((0, 0), (350, HEIGHT - 80)),
            starting_layer_height=0,
            manager=self.gui,
            visible=False,
        )
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((350 - 30, 0), (30, 30)),
            text="X",
            manager=self.gui,
            container=self.info,
            visible=False,
        )

        self.description = pygame_gui.elements.UITextBox(
            html_text="""<body>THE SICKULATOR<br>The Sickulator is an agent-based simulator which visualizes the spread of disease in a small city. <br> <b>Controls: </b> <br> Arrow keys to move camera <br> Click sprite for additional info and to follow. <br><br> Agents begin every day at home with their family and create a schedule for the day. Each agent has prefernces for what they like to do (Work, Shop, Socialize). Initially, one agent is infected. The health status of an agent is represented by their color. Green is healthy, red is infected, blue is immune, and dark grey is deceased.</body>""",
            relative_rect=pg.Rect((0, 0), (300, 400)),
            container=self.info,
            manager=self.gui,
            layer_starting_height=2,
        )

        self.status = pygame_gui.elements.UITextBox(
            relative_rect=pg.Rect((0, 550), (300, 200)),
            html_text=f"""<body></body>""",
            container=self.info,
            manager=self.gui,
            layer_starting_height=2,
        )

        self.end_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((WIDTH - 150, 0), (120, 50)),
            container=bottom_bar,
            manager=self.gui,
            text="End Simulation",
        )

        self.sprite_status = pygame_gui.elements.UIPanel(
            relative_rect=pg.Rect((WIDTH - 260, 30), (240, 130)),
            starting_layer_height=0,
            manager=self.gui,
            visible=False,
        )

        self.sprite_description = pygame_gui.elements.UITextBox(
            html_text=f"""<body>Healthy:  {Agent.health_counts[0]}<br>Infected: {Agent.health_counts[1]}</body>""",
            relative_rect=pg.Rect((2, 2), (230, 120)),
            container=self.sprite_status,
            manager=self.gui,
            layer_starting_height=2,
        )

        self.sprite_close_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((240 - 30, 0), (30, 30)),
            text="X",
            manager=self.gui,
            container=self.sprite_status,
            visible=False,
            starting_height=3,
        )

    def toggle_info(self, val):
        self.show_popup = val
        self.info.visible = val
        self.close_button.visible = val
        self.description.visible = val
        self.status.visible = val

    def toggle_sprite_status(self, val):
        self.show_sprite_popup = val
        self.sprite_status.visible = val
        self.sprite_description.visible = val
        self.sprite_close_button.visible = val

    def update_sprite_status(self):
        l = []

        if self.selected_label == "agent":
            states = ["Healthy", "Infected", "Immune", "Dead"]
            preferences = list(map( lambda x: round(x/DAY_LENGTH, 2), self.selected_sprite.preferences))
            l = [
                self.selected_sprite.name,
                states[self.selected_sprite.health_state.value],
                f"Birthday: {self.selected_sprite.birthday}",
                f"Prefs: {preferences}",
                f"Inside: {self.selected_sprite.inside}"
            ]
        elif self.selected_label == "building" or self.selected_label == "home":
            l = [
                "Class: " + self.selected_sprite.building_class,
                f"Type: {self.selected_sprite.type}",
                f"Visitors: {len(self.selected_sprite.agents)}",
                f"Infected {self.selected_sprite.infected_count}",
            ]
        details = ""
        for item in l:
            details += f"{item}<br>"
        self.sprite_description.html_text = f"<body>{details}</body>"
        try:
            self.sprite_description.rebuild()
        except:
            pass

    def update_status(self):
        self.status.html_text = f"""<body>Healthy:  {Agent.health_counts[0]}<br>Infected: {Agent.health_counts[1]}<br
>Immune:   {Agent.health_counts[2]}<br>Dead:     {Agent.health_counts[3]}</body> """
        self.status.rebuild()  # This might not be proper

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        self.time = 0
        self.day_duration = 0
        self.daily_stats.append(Agent.health_counts.copy())
        while self.playing:
            self.true_dt = self.clock.tick(FPS) / 1000
            if self.paused == False:
                self.dt = self.true_dt * self.multiplier
                # self.dt = 0.1
                self.time += self.dt
                self.day_duration += self.dt
                self.update()
            self.camera_sprite.update()
            self.camera.update(self.player)
            self.events()
            if self.show_popup:
                self.update_status()
            if self.show_sprite_popup:
                self.update_sprite_status()
            self.draw()
            self.gui.update(self.dt)
            self.gui.draw_ui(self.screen)
            pg.display.flip()
            pg.display.update()

    def update(self):
        # update portion of the game loop

        self.all_sprites.update()
        if self.day_duration >= DAY_LENGTH:
            # Change to new day
            #print("waiting for agents to be home...")
            all_agents_home = False
            for agent in self.agents:
                if not agent.is_home:
                    break
            else:
                #print("all agents home!")
                all_agents_home = True

            if all_agents_home:
                self.cumulative_stats[2] += self.infected_today
                self.infected_today = 0
                self.isDaytime = True
                self.day += 1
                self.day_duration = 0
                if self.day > self.simulation_settings.simulation_duration:
                    self.end_game()
                self.timer.set_text("Day: " + str(self.day))
                generate_schedules(self.agents)

                for agent in self.agents:
                    agent.daily_update()
                for building in self.buildings:
                    building.reset_building()
                self.daily_stats.append(Agent.health_counts.copy())
                self.agents = [
                    agent
                    for agent in self.agents
                    if agent.health_state != HealthState.DEAD
                ]
                return
            # Day changes to night
            if self.isDaytime:
                self.isDaytime = False

                # possibly teleport agents back
                for fam in range(
                    0, len(self.families)
                ):  # reproduction start at night when they come home
                    num_healthy = 0
                    sum_work = 0
                    sum_food = 0
                    sum_social = 0
                    # if it been enough days since theyve had a kid
                    for member in range(0, len(self.families[fam].agents)):
                        if (
                            self.families[fam]
                            .agents[member]
                            .health_state_but_works()
                            == 0
                            or self.families[fam]
                            .agents[member]
                            .health_state_but_works()
                            == 2
                        ):
                            # sum all the traits of healthy and immune
                            sum_work += (
                                self.families[fam].agents[member].preferences[0]
                            )
                            sum_food += (
                                self.families[fam].agents[member].preferences[1]
                            )
                            sum_social += (
                                self.families[fam].agents[member].preferences[2]
                            )
                            num_healthy += 1

                    if random.random() <= (
                        float(self.simulation_settings.reproduction_rate) / 100
                    ) * float(num_healthy):
                        # slider reproduction rate multiplied by number of healthy agents
                        # child genes averaged from healthy members in parent family
                        child_preferences = np.array(
                            [
                                sum_work / float(num_healthy),
                                sum_food / float(num_healthy),
                                sum_social / float(num_healthy),
                            ]
                        )
                        # print("\nChild: ", "\nWork Preference: " + str(round(child_preferences[0] * 100, 2)) + "%", "\nFood Peference: " + str(round(child_preferences[1] * 100, 2)) + "%", "\nSocial Preference: " + str(round(child_preferences[2] * 100, 2)) + "%")
                        if (
                            len(self.families[fam].agents)
                            < self.simulation_settings.family_size and len(self.agents) < 70
                        ):
                            # if family is not full, make new member of same family
                            child = Agent(
                                self,
                                self.families[fam],
                                self.families[fam].home.pos[0],
                                self.families[fam].home.pos[1],
                                self.families[fam].home.id,
                                id=self.cumulative_stats[3] + 1,
                                health_state=HealthState.HEALTHY,
                                preferences=child_preferences,
                            )

                            self.families[fam].add_agent(child)
                            self.agents.append(child)
                            self.spawn_agent()
                        else:
                            roomy_fam_found = False
                            for fam_checking in range(0, len(self.families)):
                                if (
                                    len(self.families[fam_checking].agents)
                                    < self.simulation_settings.family_size
                                ):
                                    child = Agent(
                                        self,
                                        self.families[fam_checking],
                                        self.families[fam_checking].home.pos[0],
                                        self.families[fam_checking].home.pos[1],
                                        self.families[fam_checking].home.id,
                                        id=self.cumulative_stats[3] + 1,
                                        health_state=HealthState.HEALTHY,
                                        preferences=child_preferences,
                                    )
                                    self.families[fam_checking].add_agent(child)
                                    self.agents.append(child)
                                    self.spawn_agent()
                                    roomy_fam_found = True
                                    break

                            if not roomy_fam_found:
                                # if family is full, make new family and take 1 member from old family to put into new family as a caretaker
                                new_home = self.homes[
                                    random.randint(0, len(self.homes)) - 1
                                ]
                                self.families.append(Family(self, new_home))
                                self.families[-1].add_agent(
                                    self.families[fam].agents.pop(0)
                                )  # removes first agent from old fam and adds to new
                                child = Agent(
                                    self,
                                    self.families[fam],
                                    self.families[fam].home.pos[0],
                                    self.families[fam].home.pos[1],
                                    self.families[fam].home.id,
                                    id=self.cumulative_stats[3] + 1,
                                    health_state=HealthState.HEALTHY,
                                    preferences=child_preferences,
                                )

                                self.families[fam].add_agent(child)
                                self.agents.append(child)
                                self.spawn_agent()
                            else:
                                roomy_fam_found = False
                                for fam_checking in range(
                                    0, len(self.families)
                                ):
                                    if (
                                        len(self.families[fam_checking].agents)
                                        < self.simulation_settings.family_size
                                    ):
                                        child = Agent(
                                            self,
                                            self.families[fam_checking],
                                            self.families[
                                                fam_checking
                                            ].home.pos[0],
                                            self.families[
                                                fam_checking
                                            ].home.pos[1],
                                            self.families[fam_checking].home.id,
                                            id=self.cumulative_stats[3] + 1,
                                            health_state=HealthState.HEALTHY,
                                            preferences=child_preferences,
                                        )
                                        self.families[fam_checking].add_agent(
                                            child
                                        )
                                        self.agents.append(child)
                                        self.spawn_agent()
                                        roomy_fam_found = True
                                        break

                                if not roomy_fam_found:
                                    # if family is full, make new family and take 1 member from old family to put into new family as a caretaker
                                    new_home = self.homes[
                                        random.randint(0, len(self.homes)) - 1
                                    ]
                                    self.families.append(Family(self, new_home))
                                    self.families[-1].add_agent(
                                        self.families[fam].agents.pop(0)
                                    )  # removes first agent from old fam and adds to new

                                    child = Agent(
                                        self,
                                        self.families[-1],
                                        self.families[-1].home.pos[0],
                                        self.families[-1].home.pos[1],
                                        self.families[-1].home.id,
                                        id=self.cumulative_stats[3] + 1,
                                        health_state=HealthState.HEALTHY,
                                        preferences=child_preferences,
                                    )
                                    self.families[-1].add_agent(child)
                                    self.families[
                                        -1
                                    ].reproduction_days = (
                                        self.simulation_settings.reproduction_cooldown
                                    )
                                    self.agents.append(child)
                                    self.spawn_agent()
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
                    elif event.ui_element == self.sprite_close_button:
                        self.toggle_sprite_status(False)
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
                    elif event.ui_element == self.pause_button:
                        self.toggle_pause()
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
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all sprites that are under the mouse cursor
                clicked_agents = [
                    s
                    for s in self.agents
                    if self.camera.apply_rect(s.rect).collidepoint(pos)
                ]
                if (
                    len(clicked_agents) > 0
                    and clicked_agents[0].inside == False
                ):
                    agent = clicked_agents[0]
                    self.selected_label = "agent"
                    self.selected_sprite = agent

                    if (self.camera_point != None):
                        self.camera_point.selected = False
                    self.camera_point = agent
                    agent.selected = True
                    self.toggle_sprite_status(True)
                else:
                    clicked_buildings = [
                        s
                        for s in self.buildings
                        if self.camera.apply_rect(s.rect).collidepoint(pos)
                    ]
                    if len(clicked_buildings) > 0:
                        building = clicked_buildings[0]
                        self.selected_label = "building"
                        self.selected_sprite = building
                        self.toggle_sprite_status(True)
                    else:
                        clicked_homes = [
                            s
                            for s in self.homes
                            if self.camera.apply_rect(s.rect).collidepoint(pos)
                        ]
                        if len(clicked_homes) > 0:
                            home = clicked_homes[0]
                            self.selected_label = "home"
                            self.selected_sprite = home
                            self.toggle_sprite_status(True)
        return events

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.pause_button.set_text("Pause")
        else:
            self.paused = True
            self.pause_button.set_text("Play")

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # self.screen.fill(BGCOLOR)
        try:
            self.screen.blit(self.map_img, self.camera.apply(self.map))
        except:
            pass
        # self.draw_grid()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

    def end_game(self):
        self.playing = False
        self.game.end_simulation(self.daily_stats, self.cumulative_stats)

    def quit(self):
        pg.quit()

    # Should create a 2D array out of path_MapO.tmx #
    def generate_path_grid(self):
        grid = [
            [0 for x in range(int(self.path_map.width / 16))]
            for y in range(int(self.path_map.height / 16))
        ]
        for layer in self.path_map.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    grid[y][x] = gid

        return grid

    def spawn_agent(self):
        self.cumulative_stats[3] = self.cumulative_stats[3] + 1

    def kill_agent(self):
        """Gets called when agent dies to disease"""
        self.cumulative_stats[0] = self.cumulative_stats[0] + 1

    def immunize_agent(self):
        self.cumulative_stats[1] = self.cumulative_stats[1] + 1
