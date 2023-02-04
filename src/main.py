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
        # initial world load
        self.player = player.Player(pygame.Vector2(), None, 8, "player", self)
        self.current_world = None
        self.current_map_rect = None
        self.load_world("tiled/everything.world")
        self.kill_dt = False
        # self.load_map("tiled/test_map.tmx")

    @scripting.ejecs_command
    def player_command(self, command):
        return self.player.command(command)

    def load_world(self, path, player_pos=START_SPOTS["default"]["pos"]):
        self.current_world = loader.load(path)
        for key, value in self.current_world.items():
            rect = pygame.Rect(key)
            if rect.collidepoint(player_pos):
                self.current_map_rect = rect
                self.load_map(self.current_world[key], player_pos, True)

    def load_map(self, tmx_data, player_pos, push=False):
        groups, event_script = mapping.load_map(tmx_data, self, player_pos)
        self.stack.push(game_state.MapState("game map", groups, self))

    def map_to_world_space(self, pos):
        return pygame.Vector2(self.current_map_rect.topleft) + pos

    def world_to_map_space(self, pos):
        return -pygame.Vector2(self.current_map_rect.topleft) + pos

    def change_map(self):
        # move player to world space
        player_rect = self.player.rect.copy()
        player_rect.center = self.map_to_world_space(player_rect.center)
        # get map which the player collides with
        map_key = None
        for key, tmx_data in self.current_world.items():
            map_rect = pygame.Rect(key)
            if map_rect != self.current_map_rect:
                if player_rect.colliderect(map_rect):
                    map_key = key
                    break
        if map_key is None:
            return False
        self.current_map_rect = pygame.Rect(map_key)
        # remove player from current sprite groups
        self.player.kill()
        # calculate player pos in terms of the new map
        print(player_rect.center)
        player_rect.center = self.world_to_map_space(player_rect.center)
        print(player_rect.center)
        # load new map with player at calculated pos
        self.player.kill()
        map_rect = self.current_map_rect.copy()
        map_rect.topleft = (0, 0)
        self.load_map(self.current_world[map_key], player_rect.center)
        # make sure player is inside the borders of the new map
        print(player_rect.center)
        self.player.limit(self.stack.get_current().main_group.map_rect, force=True)
        print(self.player.pos)
        # unset dt
        self.kill_dt = True
        return True

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
