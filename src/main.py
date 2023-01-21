"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import pygame
import pygame_menu

import mapping
import menu_theme
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
        self.caption = "Tred's Adventure"
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
        self.scripting = None
        self.scripting_api = {"command-player": self.player_command}
        # menus
        self.pausemenu = pygame_menu.Menu(
            "Paused",
            self.screen_size.x * 0.7,
            self.screen_size.y - 64,
            theme=menu_theme.menu_theme,
            mouse_visible=False,
        )
        self.pausemenu.add.button("Resume", self.exit_pausemenu)
        self.pausemenu.add.button("Quit", self.quit)
        self.pausemenu.set_onclose(self.exit_pausemenu)
        # initial map load
        self.load_map("tiled/test_map.tmx")

    @scripting.ejecs_command
    def player_command(self, command):
        return self.player.command(command)

    def load_script(self, script_path):
        script = loader.load(script_path)
        self.scripting = scripting.EJECSController(script, self.scripting_api)
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
        if self.stack.get_current() == STATE_GAMEPLAY:
            self.main_group.update(dt)

    def draw_sprites(self):
        if self.stack.get_current() == STATE_GAMEPLAY:
            self.screen.fill(self.bgcolor)
            self.main_group.draw(self.screen)
        if self.stack.get_current() == STATE_PAUSEMENU:
            self.pausemenu.draw(self.screen)
            self.player.velocity = pygame.Vector2()

    def handle_state(self):
        if self.stack.get_current() == STATE_EVENT:
            self.scripting.run()
            if self.scripting.finished():
                self.stack.pop()

    def handle_events(self):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_ESCAPE:
                    if self.stack.get_current() in {STATE_GAMEPLAY, STATE_MAINMENU}:
                        self.quit()
                    else:
                        pass  # self.stack.pop()
                if event.key == pygame.K_p:
                    self.stack.push(STATE_PAUSEMENU)
                    self.pausemenu.enable()

            if self.stack.get_current() == STATE_GAMEPLAY:
                self.input_handler.process_event(event)
                self.player.event(event)
            events.append(event)
        if self.stack.get_current() == STATE_PAUSEMENU:
            self.pausemenu.update(events)

    def run(self):
        self.screen = pygame.display.set_mode(
            util.rvec(self.screen_size), pygame.SCALED, vsync=True
        )
        pygame.display.set_caption(self.caption)
        pygame.mouse.set_visible(False)

        self.running = True
        dt = 0
        self.clock.tick()  # keeps first frame from jumping
        while self.running:
            self.handle_events()
            self.handle_state()
            self.update_sprites(dt)
            self.draw_sprites()
            pygame.display.flip()
            dt = self.clock.tick(self.fps) / 1000

        pygame.quit()
        self.screen = None

    def exit_pausemenu(self):
        self.stack.pop()
        pygame.display.set_caption(self.caption)

    def quit(self):
        self.running = False


Game().run()
