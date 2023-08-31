"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import startup

startup.splash()  # later modules load assets that are pulled in from here

import asyncio
import functools
import queue

import pygame

import custom_mapper
import globals
import gui
import menu
import sky
from bush import asset_handler, joy_cursor, save_state, sound_manager, util
from bush.ai import state
from game_objects import player
from game_states import ui, world

loader = asset_handler.glob_loader
START_SPOTS = loader.load("data/player_start_positions.json")
sound_manager.music_player.add_tracks(
    {
        key: asset_handler.join(asset_handler.AssetHandler.base, path)
        for key, path in loader.load("data/music_tracks.json", cache=False).items()
    }
)


class Game:
    def __init__(self):
        # Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(320, 240)
        self.caption = "Tred's Adventure"
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 30 * (not util.is_pygbag())  # no framerate limiting on browser
        self.running = False
        self.bgcolor = (20, 27, 27)
        try:
            self.screen = pygame.display.set_mode(
                util.rvec(self.screen_size),
                pygame.SCALED * (not util.is_pygbag()) | pygame.RESIZABLE,
                vsync=1,
            )
        except pygame.error:
            self.screen = pygame.display.set_mode(
                util.rvec(self.screen_size),
                pygame.SCALED * (not util.is_pygbag()) | pygame.RESIZABLE,
            )
        cursor_images = loader.load_spritesheet("hud/cursor.png", (16, 16))
        self.cursor = joy_cursor.JoyCursor(
            pygame.transform.scale2x(cursor_images[0]),
            pygame.Vector2(4, 2),
            alternate=pygame.transform.scale2x(cursor_images[1]),
            alternate_chance=0.01,
        )
        self.cursor_group = pygame.sprite.GroupSingle(self.cursor)
        # game control state
        self.stack = state.StateStack()
        self.state = save_state.LeveledGameState(
            "data/saves",
            "test_level.tmx",
            save_hook=self.save_state,
            load_hook=self.load_new_state,
        )
        # day/night
        self.sky = sky.WeatherCycle(self.screen_size)
        # initial map load
        self.dt_mult = 1
        self.map_loader = custom_mapper.MapLoader()
        # dialogs
        self.dialog_queue = queue.Queue()
        self.current_dialog = None
        # global state setting
        self.current_map = None
        globals.engine = self
        globals.player = player.Player()

    def time_phase(self, mult):
        """Phase time for one frame"""
        self.dt_mult = mult

    def dialog(self, text, answers=(), on_finish=lambda answer: None):
        """Run an interactive dialog.
        Text is the prompt, if any answers are given they will be displayed, and then the on kill will be called with the answer given"""
        self.dialog_queue.put((text, answers, on_finish))

    def spawn_particles(self, particles):
        """Spawn a list of particles to the global particle manager"""
        self.stack.get_current().particle_manager.add(particles)

    def load_new_state(self, _):
        """Called when a new save is opened"""
        globals.player.load_data()
        self.map_loader.clear_cache()  # new save, all previous stuff gone
        map_path = self.state.get("map", "engine")
        self.stack.clear()
        self.stack.push(ui.MainMenu())
        if "tmx" in map_path:
            self.load_map(map_path, START_SPOTS.get(map_path, (30, 30)))
        else:
            self.load_world(map_path, START_SPOTS.get(map_path, (30, 30)))

    def save_state(self, _):
        """Save game state to save file"""
        globals.player.save_data()

    def load_map(self, tmx_path, player_pos=None):
        """Load map at given path, relative to the "tiled" asset directory.

        If the player position is given the player will spawn there.  Else it will use the default specified by the map"""
        print(tmx_path)
        groups, properties = self.map_loader.load(tmx_path, player_pos)
        self.stack.push(
            world.MapState("game map", groups, properties.get("track", None))
        )

    def load_world(self, world_path, player_pos=None):
        """Load world at given path, relative to the "tiled" asset directory.

        If the player position is given the player will spawn there.  Else it will use the default specified by the map"""
        self.stack.push(
            world.WorldState(
                world_path,
                functools.partial(self.map_loader.load, player_pos=player_pos),
                initial_pos=player_pos,
            )
        )

    def toggle_fullscreen(self):
        """Attempt to switch to full screen mode"""
        if not util.is_pygbag():
            pygame.display.toggle_fullscreen()

    def tick(self):
        """Handles a frame change.  Do not call this unless you know what yo uare doing"""
        dt = self.clock.tick(self.fps) / 1000
        dt *= self.dt_mult
        self.dt_mult = 1
        return dt

    async def run(self):
        """Starts up a game and runs it until finished"""
        globals.engine = self  # set the global engine reference
        globals.player = player.Player()
        pygame.display.set_caption(self.caption)
        self.stack.push(ui.MainMenu())  # load the MainMenu
        self.running = True
        dt = 0
        self.tick()  # prevents large dt on first frame
        while self.running:
            current_state = self.stack.get_current()
            if current_state is None:
                self.quit()
                continue
            if self.current_dialog is not None and not self.current_dialog.alive():
                self.current_dialog = None
            if not self.dialog_queue.empty() and self.current_dialog is None:
                text, answers, on_kill = self.dialog_queue.get()
                self.current_dialog = gui.Dialog(
                    text,
                    answers,
                    on_kill,
                    menu.get_dialog_rect(self.screen_size),
                    1,
                    self.stack.get_current().gui,
                )
            current_state.update(dt)
            self.cursor_group.update(dt)
            self.screen.fill(self.bgcolor)
            current_state.draw(self.screen)
            self.cursor_group.draw(self.screen)
            current_state.handle_events()
            pygame.display.flip()
            await asyncio.sleep(0)
            dt = self.tick()

        print("exiting game")
        pygame.quit()
        self.screen = None

    def quit(self):
        """Exit game, if allowed on current platform"""
        print("QUIT", self.stack)
        self.running = False or util.is_pygbag()  # don't quit in pygbag


if __name__ == "__main__":
    asyncio.run(Game().run())
