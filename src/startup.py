import asyncio

import pygame

import environment
import gui
import items
import particle_util
from bush import asset_handler


async def splash():
    screen = pygame.display.set_mode((480, 320), pygame.SCALED | pygame.NOFRAME)
    font = pygame.font.SysFont("serif", 48)
    text = font.render("loading...", False, "white").convert_alpha()
    text_rect = text.get_rect()
    text_rect.center = (240, 160)
    color = pygame.Color(37, 190, 42)
    while True:
        screen.fill(color)
        screen.blit(text, text_rect)
        pygame.display.flip()
        color.hsla = (color.hsla[0] + 1, *color.hsla[1:])
        await asyncio.sleep(0)


async def setup():
    setting = True
    splash_task = asyncio.create_task(splash())
    asset_handler.AssetHandler.set_global_home("assets")
    await asset_handler.glob_loader.cache_folder_async()
    environment.init()
    gui.init()
    items.init()
    particle_util.init()
    splash_task.cancel()
    await asyncio.sleep(0)
