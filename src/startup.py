import pygame

from bush import asset_handler

# make a splash screen.  Not only gives feedback to user, but allows pygame.Surface.convert()
pygame.init()
font = pygame.font.SysFont(None, 48)
screen = pygame.display.set_mode((480, 320), pygame.SCALED | pygame.NOFRAME)
text = font.render("Loading assets...", False, "white")
rect = text.get_rect(center=(240, 160))
screen.blit(text, rect.topleft)
pygame.display.flip()

# load assets
loader = asset_handler.glob_loader
loader.base = "assets"
loader.cache_folder()
