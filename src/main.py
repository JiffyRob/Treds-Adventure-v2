"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
# normal imports
import pygame

import mapping
from bush import asset_handler, color, event_binding, util
from bush.ai import scripting, state

pygame.init()
loader = asset_handler.glob_loader

STATE_GAMEPLAY = 0
STATE_EVENT = 1
STATE_MAINMENU = 2
STATE_PAUSEMENU = 3


class Game:
    def __init__(self):
        # Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(640, 480)
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.running = False
        self.bgcolor = color.GREY
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        # game control state
        self.groups = None
        self.main_group = None
        self.player = None
        self.stack = state.StateStack()
        self.stack.push(STATE_GAMEPLAY)
        self.input_handler = event_binding.EventHandler({})
        self.input_handler.update_bindings(loader.load("data/input_bindings.json"))
        self.controller = None
        self.controller_api = {"command-player": self.player_command}
        # initial map load
        self.load_map("tiled/test_map.tmx")
        # test script load
        self.load_script("scripts/test_ejecs.json")

    @controller.ejecs_command
    def player_command(self, command):
        return self.player.command(command)

    def load_script(self, script_path):
        script = loader.load(script_path)
        self.controller = controller.EJECSController(script, self.controller_api)
        self.stack.push(STATE_EVENT)

    def load_map(self, path, replace=False):
        self.groups, event_script = mapping.load_map(path, self.screen_size)
        self.main_group = self.groups["main"]
        self.player = self.groups["player"].sprite
        if replace:
            self.stack.replace(STATE_GAMEPLAY)
        else:
            self.stack.push(STATE_GAMEPLAY)
        if event_script:
            self.game_event(event_script)
            self.stack.push(STATE_EVENT)

    def update_sprites(self, dt):
        self.main_group.update(dt)

    def draw_sprites(self):
        self.main_group.draw(self.screen)

    def handle_state(self):
        if self.stack.get_current() == STATE_EVENT:
            self.controller.run()
            if self.controller.finished():
                self.stack.pop()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if self.stack.get_current() == STATE_GAMEPLAY:
                self.input_handler.process_event(event)
                self.player.event(event)

    def run(self):
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        self.screen.fill(self.bgcolor)

        self.running = True
        dt = 0
        self.clock.tick()  # keeps first frame from jumping
        while self.running:
            self.handle_events()
            self.screen.fill(self.bgcolor)
            self.handle_state()
            self.update_sprites(dt)
            self.draw_sprites()
            pygame.display.flip()
            dt = self.clock.tick(self.fps) / 1000

        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
