import pygame

from bush import asset_handler


def splash():
    """Loads all assets and such behind an (ugly) splash screen"""
    pygame.init()
    font = pygame.font.SysFont(".", 48)
    screen = pygame.display.set_mode((480, 320), pygame.SCALED | pygame.NOFRAME)
    text = font.render("Loading assets...", False, "white")
    rect = text.get_rect(center=(240, 160))
    screen.blit(text, rect.topleft)
    pygame.display.flip()

    # load assets
    loader = asset_handler.glob_loader
    loader.base = "assets"
    loader.cache_folder()
