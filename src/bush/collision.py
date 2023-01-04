import pygame


def collide_rect(rect1, rect2):
    return rect1.colliderect(rect2)


def collide_mask(mask1, mask2):
    return mask1.overlap(mask2)


def collide_rect_mask(rect, mask, mask_pos=(0, 0)):
    rect_mask = pygame.Mask(rect.size, True)
    return mask.overlap(rect_mask, rect.topleft - pygame.Vector2(mask_pos))


def collides(thing1, thing2):
    type_dict = {
        (pygame.Rect, pygame.Rect): collide_rect,
        (pygame.Mask, pygame.Mask): collide_mask,
        (pygame.Mask, pygame.Rect): lambda a, b: collide_rect_mask(b, a),
        (pygame.Rect, pygame.Mask): collide_mask,
    }
    return bool(type_dict[type(thing1), type(thing2)](thing1, thing2))
