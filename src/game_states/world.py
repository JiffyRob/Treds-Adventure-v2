import pygame

import globals
import gui
from bush import event_binding, particle
from game_states import base, ui


class MapState(base.GameState):
    def __init__(self, map_name, registry, soundtrack=None):
        self.registry = registry
        self.sky = globals.engine.sky
        self.main_group = self.registry.get_group("main")
        self.soundtrack = soundtrack
        self.particle_manager = particle.ParticleManager()
        if self.soundtrack is not None:
            self.music_player.play(self.soundtrack)
        hud = gui.UIGroup()
        gui.HeartMeter(globals.player, pygame.Rect(8, 8, 192, 64), 1, hud)
        rect = pygame.Rect(0, 4, 64, 9)
        rect.right = globals.engine.screen_size.x - 4
        gui.MagicMeter(globals.player, rect, 1, hud)
        super().__init__(map_name, gui=hud)
        self.input_handler.update_bindings(
            self.loader.load("data/player_bindings.json")
        )

    def update(self, dt=0.03):
        super().update(dt)
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


class WorldState(base.GameState):
    pass  # TODO
