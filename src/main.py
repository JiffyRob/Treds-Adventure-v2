"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import startup

print("assets loaded")

import asyncio
import queue

import pygame

import custom_mapper
import game_state
import gui
import menu
import sky
from bush import asset_handler, joy_cursor, save_state, sound_manager, util
from bush.ai import state

loader = asset_handler.glob_loader
START_SPOTS = loader.load("data/player_start_positions.json")
sound_manager.music_player.add_tracks(
    {
        key: asset_handler.join(loader.base, path)
        for key, path in loader.load("data/music_tracks.json", cache=False).items()
    }
)


class Game:
    def __init__(self):
        # Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(480, 320)
        self.caption = "Tred's Adventure"
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 30 * (not util.is_pygbag())  # no framerate limiting on browser
        self.running = False
        self.bgcolor = (20, 27, 27)
        self.screen = pygame.display.set_mode(
            util.rvec(self.screen_size), pygame.SCALED | pygame.RESIZABLE
        )
        cursor_images = loader.load_sprite_sheet(
            "hud/cursor.png",
            (16, 16),
        )
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
            asset_handler.join(loader.base, "data/saves"),
            "test_level.tmx",
            save_hook=self.save_state,
            load_hook=self.load_new_state,
        )
        # day/night
        self.sky = sky.WeatherCycle(self.screen_size)
        # initial map load
        self.kill_dt = False
        self.map_loader = custom_mapper.MapLoader(self, self.state)
        self.current_map = None
        self.player = None
        self.stack.push(game_state.MainMenu(self))
        # dialogs
        self.dialog_queue = queue.Queue()
        self.current_dialog = None

    def dialog(self, text, answers, on_finish=lambda interrupted: None):
        self.dialog_queue.put((text, answers, on_finish))

    def load_new_state(self, _):
        map_path = self.state.get("map", "engine")
        self.stack.clear()
        self.stack.push(game_state.MainMenu(self))
        self.player = None
        self.load_map(map_path, START_SPOTS.get(map_path, (0, 0)), push=True)

    def save_state(self, _):
        self.player.save_data()

    def load_map(self, tmx_path, player_pos, push=None):
        self.current_map = tmx_path
        if self.player is not None:
            self.player.save_data()
        groups, track, event_script = self.map_loader.load_map(
            tmx_path, self, player_pos
        )
        self.player = groups["player"].sprite
        if push is False or (push is None and self.stack.get_current() != "MainMenu"):
            self.stack.pop()
        self.stack.push(game_state.MapState("game map", groups, self, track))
        event_script = None
        if event_script:
            self.stack.push(
                game_state.ScriptedMapState("game map", groups, self, event_script)
            )

    def toggle_fullscreen(self):
        if not util.is_pygbag():
            pygame.display.toggle_fullscreen()

    def tick(self):
        dt = self.clock.tick(self.fps) / 1000
        if self.kill_dt:
            dt = 0
        self.kill_dt = False
        return dt

    async def run(self):
        self.screen = pygame.display.set_mode(
            util.rvec(self.screen_size), pygame.SCALED | pygame.RESIZABLE, vsync=0
        )
        pygame.display.set_caption(self.caption)

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
        print("QUIT", self.stack)
        self.running = False


if __name__ == "__main__":
    asyncio.run(Game().run())
