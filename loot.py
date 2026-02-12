import pygame
import random
import math
from config import WIDTH, HEIGHT, ARENA, COLORS

class Loot:
    """Dropped items from defeated enemies"""
    def __init__(self, pos, loot_type):
        self.pos = pygame.Vector2(pos)
        self.loot_type = loot_type  # "health" or "damage"
        self.radius = 8
        self.value = 15 if loot_type == "health" else 2
        self.pickup_range = 50
        self.pulse_timer = 0.0
        self.alive_flag = True
        self.ttl = 10.0  # Disappear after 10 seconds
        
    def update(self, dt, player):
        self.pulse_timer += dt
        self.ttl -= dt
        
        if self.ttl <= 0:
            self.alive_flag = False
            return
        
        # Auto pickup if close
        if player.pos.distance_to(self.pos) < self.pickup_range:
            self.pickup(player)
    
    def pickup(self, player):
        if self.loot_type == "health":
            player.hp = min(player.max_hp, player.hp + self.value)
        elif self.loot_type == "damage":
            player.damage_buff = min(2.0, player.damage_buff + self.value * 0.01)
        self.alive_flag = False
    
    def draw(self, surf):
        if not self.alive_flag:
            return
        
        # Pulse effect
        pulse = 0.5 + 0.5 * math.sin(self.pulse_timer * 4.0)
        size = int(self.radius * (0.8 + pulse * 0.4))
        
        if self.loot_type == "health":
            pygame.draw.circle(surf, (100, 255, 100), (int(self.pos.x), int(self.pos.y)), size)
            pygame.draw.circle(surf, (150, 255, 150), (int(self.pos.x), int(self.pos.y)), size, 2)
        else:
            pygame.draw.circle(surf, (255, 150, 100), (int(self.pos.x), int(self.pos.y)), size)
            pygame.draw.circle(surf, (255, 200, 150), (int(self.pos.x), int(self.pos.y)), size, 2)