"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import random

import pygame

import custom_mapper
import environment
import game_state
import player
import sky
from bush import asset_handler, color, joy_cursor, util
from bush.ai import scripting, state

pygame.init()
loader = asset_handler.glob_loader

START_SPOTS = loader.load("data/player_start_positions.json")


class Game:
    def __init__(self):
        # Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(640, 480)
        self.caption = "Tred's Adventure"
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.running = False
        self.bgcolor = color.GREY
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        cursor_images = loader.load(
            "resources/misc/cursor.png",
            loader=asset_handler.load_spritesheet,
            frame_size=(16, 16),
        )
        self.cursor = joy_cursor.JoyCursor(
            pygame.transform.scale2x(cursor_images[not bool(random.randint(0, 100))]),
            pygame.Vector2(4, 2),
        )
        self.cursor_group = pygame.sprite.GroupSingle(self.cursor)
        self.cursor.hide()
        # game control state
        self.stack = state.StateStack()
        # day/night
        self.sky = sky.Sky(self.screen_size)
        # initial map load
        self.player = player.Player(
            pygame.Vector2(), None, 8, "player", self, environment.EnvironmentHandler()
        )
        self.kill_dt = False
        self.map_loader = custom_mapper.MapLoader(self.screen_size, self.player)
        self.load_map("test_map.tmx", START_SPOTS["default"]["pos"])

    @scripting.ejecs_command
    def player_command(self, command):
        return self.player.command(command)

    def load_map(self, tmx_data, player_pos, push=False):
        groups, event_script = self.map_loader.load_map(tmx_data, self, player_pos)
        if not push:
            self.stack.pop()
        self.stack.push(game_state.MapState("game map", groups, self))
        event_script = None
        if event_script:
            self.stack.push(
                game_state.ScriptedMapState("game map", groups, self, event_script)
            )

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()

    def tick(self):
        dt = self.clock.tick(self.fps) / 1000
        if self.kill_dt:
            dt = 0
        self.kill_dt = False
        return dt

    def run(self):
        self.screen = pygame.display.set_mode(
            util.rvec(self.screen_size), 0, vsync=True
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
            current_state.update(dt)
            self.cursor_group.update(dt)
            current_state.draw(self.screen)
            self.cursor_group.draw(self.screen)
            current_state.handle_events()
            pygame.display.flip()
            dt = self.tick()

        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
