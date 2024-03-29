import logging
import os

import pygame

import globals
import gui
from bush import event_binding, particle, sound, timer, util
from bush.mapping import world
from game_states import base, ui

logger = logging.getLogger(__name__)


class MapState(base.GameState):
    def __init__(self, filename, registry, properties):
        self.registry = registry
        self.sky = globals.engine.sky
        self.main_group = self.registry.get_group("main")
        self.particle_manager = particle.ParticleManager()
        self.map_properties = {}
        hud = gui.UIGroup()
        gui.HeartMeter(globals.player, pygame.Rect(8, 8, 192, 64), 1, hud)
        rect = pygame.Rect(0, 4, 64, 9)
        rect.right = globals.engine.screen_size.x - 4
        gui.MagicMeter(globals.player, rect, 1, hud)
        super().__init__(filename, gui=hud)
        self.input_handler.update_bindings(
            self.loader.load("data/player_bindings.json")
        )
        self.filename = filename
        self.reload_map()

    def update(self, dt=0.03):
        super().update(dt)
        self.sky.update(dt)
        self.particle_manager.update(dt)
        self.main_group.update(dt)

    def update_map(self):
        pass

    def handle_events(self):
        for event in pygame.event.get():
            super().handle_event(event)
            if event.type == event_binding.BOUND_EVENT:
                if event.name == "pause":
                    self._stack.push(
                        ui.PauseMenu(screen_surf=pygame.display.get_surface().convert())
                    )
            globals.player.event(event)

    def draw(self, surface, draw_player=True, offset=(0, 0)):
        if not draw_player:
            self.main_group.remove(globals.player)
        self.main_group.draw(surface, offset)
        self.main_group.add(globals.player)
        if self.main_group.debug_physics:
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                globals.player.get_interaction_rect().move(
                    -pygame.Vector2(self.main_group.cam_rect.topleft)
                ),
                1,
            )
        self.sky.render(surface)
        self.particle_manager.draw(
            surface, -pygame.Vector2(self.main_group.cam_rect.topleft)
        )
        super().draw(surface)

    def map_to_world(self, local_pos, map_name=None):
        return local_pos

    def reload_map(self):
        reload_map(self.main_group)
        self.sky.set_weather(
            self.map_properties.get("ambience", self.sky.WEATHERTYPE_DNCYCLE)
        )
        sound.glob_player.switch_track(self.map_properties.get("track", None))


class WorldState(base.GameState):
    STATE_MAP = 0
    STATE_TRANSITIION = 1

    def __init__(self, filename, map_loader, initial_map=None, initial_pos=None):
        # mapping
        self.world = world.World(self.loader.load(os.path.join("tiled/maps", filename)))
        self.map_loader = map_loader
        self.map_properties = {}
        self.sky = globals.engine.sky
        self.particle_manager = particle.ParticleManager()
        self.registry = None
        self.main_group = None
        self.map_rect = None
        self.map_name = None
        self.state = self.STATE_MAP
        # transitions
        # map1 is the map to be transitioned out of
        # map2 is the map to be transitioned into
        self.map1_start = None
        self.map1_dest = None
        self.map1_group = None
        self.map2_offset = None
        self.player_offset = None
        self.player_motion_ratio = None
        self.player_dest = None
        self.transition_timer = timer.Timer(0)
        self.ambience = None

        hud = gui.UIGroup()
        gui.HeartMeter(globals.player, pygame.Rect(8, 8, 192, 64), 1, hud)
        rect = pygame.Rect(0, 4, 64, 9)
        rect.right = globals.engine.screen_size.x - 4
        gui.MagicMeter(globals.player, rect, 1, hud)
        rect = pygame.Rect(8, 0, 16, 16)
        rect.bottom = globals.engine.screen_size.y - 8
        gui.ToolGauge(rect, 1, hud)
        super().__init__(filename, gui=hud)
        self.input_handler.update_bindings(
            self.loader.load("data/player_bindings.json")
        )
        if initial_map is not None:
            self.load_map(initial_map)
        elif initial_pos is not None:
            name = self.world.name_collidepoint(initial_pos)
            player_pos = (
                pygame.Vector2(initial_pos) - self.world.name_to_rect[name][0:2]
            )
            self.load_map(name)
            globals.player.pos = player_pos
        else:
            self.load_map(self.world.name_collidepoint((0, 0)))

        self.filename = filename
        self.reload_map()

    def load_map(self, map_name):
        self.map_name = map_name
        self.registry, self.map_properties = self.map_loader(
            self.world.get_map_by_name(map_name)
        )
        self.map_rect = pygame.Rect(self.world.get_rect_by_name(map_name))
        self.main_group = self.registry.get_group("main")
        self.reload_map()

    def reload_map(self):
        reload_map(self.main_group)
        self.sky.set_weather(
            self.map_properties.get("ambience", self.sky.WEATHERTYPE_DNCYCLE)
        )
        sound.glob_player.switch_track(self.map_properties.get("track", None))

    def update_map(self):
        player_facing = util.string_direction_to_vec(globals.player.facing)
        pos = player_facing * 16 + globals.player.pos + self.map_rect.topleft
        new_map = self.world.name_collidepoint(pos)
        if new_map not in {None, self.map_name}:
            logger.info(f"Switch map from {self.map_name} to {new_map}")
            self.state = self.STATE_TRANSITIION
            self.player_offset = globals.player.pos.copy() - (
                pygame.Vector2(globals.player.rect.size) // 2
            )
            old_map_rect = self.map_rect
            self.map1_group = self.main_group
            self.load_map(new_map)
            self.player_dest = pos - self.map_rect.topleft
            self.map1_dest = -(
                self.main_group.cam_rect_centered(self.player_dest).topleft
                + pygame.Vector2(self.map_rect.topleft)
                - old_map_rect.topleft
            )
            self.map1_start = -pygame.Vector2(self.map1_group.cam_rect.topleft)
            self.map2_offset = (
                pygame.Vector2(self.map_rect.topleft) - old_map_rect.topleft
            )
            motion_index = list(player_facing).index(max(player_facing))
            self.player_motion_ratio = (
                (self.map1_dest - self.map1_start).length()
                - globals.player.rect.size[motion_index]
            ) / (self.map1_dest - self.map1_start).length()
            self.transition_timer = timer.Timer(1000, self.finish_transition)
            self.main_group.update(0)

    def finish_transition(self):
        self.state = self.STATE_MAP

        globals.player.pos = self.player_dest
        self.map1_start = None
        self.map1_dest = None
        self.map1_group = None
        self.map2_offset = None
        self.player_offset = None
        self.player_dest = None
        self.transition_timer = timer.Timer(0)
        self.main_group.add(globals.player)

    def update(self, dt=0.03):
        super().update(dt)
        self.transition_timer.update()
        if self.state == self.STATE_MAP:
            self.sky.update(dt)
            self.particle_manager.update(dt)
            self.main_group.update(dt)

    def handle_events(self):
        for event in pygame.event.get():
            super().handle_event(event)
            if event.type == event_binding.BOUND_EVENT:
                if event.name == "pause":
                    self._stack.push(
                        ui.PauseMenu(screen_surf=pygame.display.get_surface().convert())
                    )
            globals.player.event(event)

    def draw(self, surface, offset=(0, 0)):
        if self.state == self.STATE_MAP:
            self.main_group.draw(surface, offset)
            if self.main_group.debug_physics:
                pygame.draw.rect(
                    surface,
                    (255, 0, 0),
                    globals.player.get_interaction_rect().move(
                        -pygame.Vector2(self.main_group.cam_rect.topleft)
                    ),
                    1,
                )
            self.particle_manager.draw(
                surface, -pygame.Vector2(self.main_group.cam_rect.topleft)
            )
        else:
            self.main_group.remove(globals.player)
            percent_complete = self.transition_timer.percent_complete()
            map1_pos = self.map1_start.lerp(self.map1_dest, percent_complete)
            self.map1_group.draw(surface, offset=map1_pos)
            self.main_group.draw(surface, offset=map1_pos + self.map2_offset)
            surface.blit(
                globals.player.image,
                self.map1_start.lerp(
                    self.map1_dest, percent_complete * self.player_motion_ratio
                )
                + self.player_offset,
            )
        self.sky.render(surface)
        super().draw(surface)

    def map_to_world(self, local_pos, map_name=None):
        if map_name is None:
            map_name = self.map_name
        return pygame.Vector2(local_pos) + self.world.name_to_rect[map_name][:2]


def reload_map(sprite_group):
    for sprite in sprite_group.sprites():
        if hasattr(sprite, "reload"):
            sprite.reload()
