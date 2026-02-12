import pygame
import math
from config import WIDTH, HEIGHT, ARENA, COLORS
from utils import clamp, circle_hit

class Projectile:
    def __init__(self, pos, vel, radius, damage, ttl=3.0):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius = radius
        self.damage = damage
        self.ttl = ttl
        self.alive_flag = True

    def update(self, dt):
        if not self.alive_flag:
            return
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive_flag = False
            return
        self.pos += self.vel * dt
        if (self.pos.x < ARENA["margin"] or self.pos.x > WIDTH - ARENA["margin"] or
            self.pos.y < ARENA["margin"] or self.pos.y > HEIGHT - ARENA["margin"]):
            self.alive_flag = False

    def try_hit_player(self, player):
        if not self.alive_flag:
            return False
        if circle_hit(self.pos.x, self.pos.y, self.radius, player.pos.x, player.pos.y, player.radius):
            self.alive_flag = False
            player.take_damage(self.damage)
            if hasattr(player, 'apply_poison'):
                player.apply_poison(5.0, 2)
            return True
        return False

    def draw(self, surf):
        pygame.draw.circle(surf, (100, 255, 100), (int(self.pos.x), int(self.pos.y)), int(self.radius))

class AcidicAlchemist:
    """Chemistry melee: applies poison debuff"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 16
        self.speed = 125.0
        self.max_hp = 70
        self.hp = float(self.max_hp)
        self.base_damage = 8
        self.aggro_range = 420.0
        self.attack_range = 45.0
        self.attack_cooldown = 0.95
        self.attack_windup = 0.35
        
        self._atk_timer = 0.0
        self.state_timer = 0.0
        self.state = "idle"
        self.flash_timer = 0.0
        
    def update(self, dt, player):
        self._atk_timer = max(0.0, self._atk_timer - dt)
        self.state_timer = max(0.0, self.state_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        
        dist = self.pos.distance_to(player.pos)
        
        if self.state == "idle":
            if dist > self.attack_range * 0.9 and dist <= self.aggro_range:
                direction = (player.pos - self.pos)
                if direction.length_squared() > 0:
                    self.pos += direction.normalize() * self.speed * dt
            
            if dist <= self.attack_range and self._atk_timer <= 0.0:
                self.state = "windup"
                self.state_timer = self.attack_windup
        
        elif self.state == "windup":
            if self.state_timer <= 0.0:
                if dist <= (self.attack_range + player.radius):
                    player.take_damage(self.base_damage)
                    if hasattr(player, 'apply_poison'):
                        player.apply_poison(6.0, 1)
                self.state = "swing"
                self.state_timer = 0.15
                self._atk_timer = self.attack_cooldown
        
        elif self.state == "swing":
            if self.state_timer <= 0.0:
                self.state = "idle"
        
        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))
    
    def take_damage(self, dmg):
        self.hp = max(0.0, self.hp - dmg)
        self.flash_timer = 0.12
    
    def alive(self):
        return self.hp > 0
    
    def draw(self, surf):
        color = (150, 200, 100) if self.flash_timer > 0 else (120, 180, 80)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surf, (100, 150, 60), (int(self.pos.x), int(self.pos.y)), self.radius + 6, 1)