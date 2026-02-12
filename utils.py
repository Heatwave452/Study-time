import pygame
import math

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def vec2_from_keys(keys, key_up, key_down, key_left, key_right):
    x = (keys[key_right] - keys[key_left])
    y = (keys[key_down] - keys[key_up])
    v = pygame.Vector2(x, y)
    if v.length_squared() > 0:
        return v.normalize()
    return v

def draw_text(surf, text, pos, font, color):
    text_surf = font.render(text, True, color)
    surf.blit(text_surf, pos)

def circle_hit(x1, y1, r1, x2, y2, r2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx*dx + dy*dy)
    return dist < (r1 + r2)

def draw_triangle(surface, center, angle_rad, size, color):
    """Draw a simple isosceles triangle pointing along angle_rad"""
    cx, cy = center
    forward = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))
    right = pygame.Vector2(-forward.y, forward.x)
    p1 = pygame.Vector2(cx, cy) + forward * size
    p2 = pygame.Vector2(cx, cy) - forward * (size * 0.6) + right * (size * 0.6)
    p3 = pygame.Vector2(cx, cy) - forward * (size * 0.6) - right * (size * 0.6)
    pygame.draw.polygon(surface, color, [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)])