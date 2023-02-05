"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import pygame

import game_state
import mapping
import player
import sky
from bush import asset_handler, color, event_binding, util
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
        # game control state
        self.stack = state.StateStack()
        # day/night
        self.sky = sky.Sky(self.screen_size)
        # initial map load
        self.player = player.Player(pygame.Vector2(), None, 8, "player", self)
        self.kill_dt = False
        self.load_map("test_map.tmx", START_SPOTS["default"]["pos"])

    @scripting.ejecs_command
    def player_command(self, command):
        return self.player.command(command)

    def load_map(self, tmx_data, player_pos, push=False):
        groups, event_script = mapping.load_map(tmx_data, self, player_pos)
        if not push:
            self.stack.pop()
        self.stack.push(game_state.MapState("game map", groups, self))
        if event_script:
            self.stack.push(
                game_state.ScriptedMapState("game map", groups, self, event_script)
            )

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()

    def run(self):
        self.screen = pygame.display.set_mode(
            util.rvec(self.screen_size), 0, vsync=True
        )
        pygame.display.set_caption(self.caption)
        pygame.mouse.set_visible(False)

        self.running = True
        dt = 0
        self.clock.tick()  # keeps first frame from jumping
        while self.running:
            current_state = self.stack.get_current()
            if current_state is None:
                self.quit()
                continue
            current_state.update(dt)
            current_state.draw(self.screen)
            current_state.handle_events()
            pygame.display.flip()
            dt = self.clock.tick(self.fps) / 1000
            if self.kill_dt:
                dt = 0
            self.kill_dt = False

        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
