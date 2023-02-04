"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import pygame
import pygame_menu

import mapping
import menu_theme
import player
import sky
from bush import asset_handler, color, event_binding, util
from bush.ai import scripting, state

pygame.init()
loader = asset_handler.glob_loader

STATE_GAMEPLAY = 0
STATE_EVENT = 1
STATE_MAINMENU = 2
STATE_PAUSEMENU = 3
STATE_TRANSITION = 4

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

    def load_script(self, script_path):
        script = loader.load(script_path)
        self.scripting = scripting.EJECSController(script, self.scripting_api)
        self.stack.push(STATE_EVENT)

    def load_world(self, path, player_pos=START_SPOTS["default"]["pos"]):
        self.current_world = loader.load(path)
        for key, value in self.current_world.items():
            rect = pygame.Rect(key)
            if rect.collidepoint(player_pos):
                self.current_map_rect = rect
                self.load_map(self.current_world[key], player_pos)

    def load_map(self, tmx_data, player_pos, force_push=False):
        groups, event_script = mapping.load_map(tmx_data, self, player_pos)
        self.groups = groups
        self.main_group = groups["main"]
        if self.stack.get_current() != STATE_GAMEPLAY or force_push:
            self.stack.push(STATE_GAMEPLAY)
        if event_script:
            self.load_script(event_script)
            self.stack.push(STATE_EVENT)

    def map_to_world_space(self, pos):
        return pygame.Vector2(self.current_map_rect.topleft) + pos

    def world_to_map_space(self, pos):
        return -pygame.Vector2(self.current_map_rect.topleft) + pos

    def change_map(self):
        print("map change")
        # move player to world space
        player_rect = self.player.rect.copy()
        print("map -> world space")
        print(player_rect.center)
        player_rect.center = self.map_to_world_space(player_rect.center)
        print(player_rect.center)
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
        print("world -> new map space")
        print(player_rect.center)
        player_rect.center = self.world_to_map_space(player_rect.center)
        print(player_rect.center)
        # load new map with player at calculated pos
        self.player.kill()
        map_rect = self.current_map_rect.copy()
        map_rect.topleft = (0, 0)
        self.load_map(self.current_world[map_key], player_rect.center)
        # make sure player is inside the borders of the new map
        print("player limiting")
        print(player_rect.center)
        self.player.limit(self.main_group.map_rect, force=True)
        print(self.player.pos)
        # unset dt
        self.kill_dt = True

        # transition animation
        darkness = 1
        adder = 6
        original = self.screen.copy()
        while darkness > 0:
            screen_surf = original.copy()
            darken_surf = pygame.Surface(screen_surf.get_size())
            overlay_color = (darkness, darkness, darkness)
            darken_surf.fill(overlay_color)
            screen_surf.blit(darken_surf, (0, 0), None, pygame.BLEND_RGB_SUB)
            self.screen.blit(screen_surf, (0, 0))
            darkness += adder
            if darkness >= 250:
                adder *= -1
                darkness += adder
            pygame.display.flip()
            self.clock.tick(30)
        return True

    def update_sprites(self, dt):
        self.sky.update(dt)
        self.main_group.update(dt)

    def draw_sprites(self):
        if self.stack.get_current() == STATE_GAMEPLAY:
            self.screen.fill(self.bgcolor)
            self.main_group.draw(self.screen)
            self.sky.render(self.screen)
        if self.stack.get_current() == STATE_PAUSEMENU:
            self.pausemenu.draw(self.screen)
            self.player.velocity = pygame.Vector2()

    def handle_state(self):
        if self.stack.get_current() == STATE_EVENT:
            self.scripting.run()
            if self.scripting.finished():
                self.stack.pop()

    def pause(self):
        if not self.pausemenu.is_enabled():
            self.pausemenu.enable()
        if self.stack.get_current() != STATE_PAUSEMENU:
            self.stack.push(STATE_PAUSEMENU)

    def unpause(self):
        if self.pausemenu.is_enabled():
            self.pausemenu.disable()
        if self.stack.get_current() == STATE_PAUSEMENU:
            self.stack.pop()
        pygame.display.set_caption(self.caption)

    def handle_events(self):
        for event in pygame.event.get():
            self.input_handler.process_event(event)
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.pausemenu.is_enabled():
                        self.unpause()
                    else:
                        self.quit()
                if event.key == pygame.K_p:
                    self.pause()
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            if self.stack.get_current() == STATE_GAMEPLAY:
                self.player.event(event)
            if self.stack.get_current() == STATE_PAUSEMENU:
                self.pausemenu.update([event])

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
            self.handle_events()
            if self.stack.get_current() in {STATE_GAMEPLAY, STATE_EVENT}:
                self.handle_state()
                self.update_sprites(dt)
                self.draw_sprites()
                pygame.display.flip()
            if self.stack.get_current() == STATE_PAUSEMENU:
                self.pausemenu.draw(self.screen)
            if self.stack.get_current() == STATE_MAINMENU:
                ...
            self.handle_state()
            pygame.display.flip()
            dt = self.clock.tick(self.fps) / 1000
            if self.kill_dt:
                dt = 0
            self.kill_dt = False

        pygame.quit()
        self.screen = None

    def exit_pausemenu(self):
        self.stack.pop()
        pygame.display.set_caption(self.caption)

    def quit(self):
        self.running = False


Game().run()
