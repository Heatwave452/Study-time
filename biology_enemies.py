import pygame
import random
import math
from config import WIDTH, HEIGHT, ARENA, COLORS


class Projectile:
    def __init__(self, pos, vel, radius, damage, lifetime=3.0):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius = radius
        self.damage = damage
        self.lifetime = lifetime
        self.alive_flag = True

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt
        
        # check arena bounds
        margin = ARENA["margin"]
        if (self.pos.x < margin or self.pos.x > WIDTH - margin or
            self.pos.y < margin or self.pos.y > HEIGHT - margin):
            self.alive_flag = False
        
        if self.lifetime <= 0:
            self.alive_flag = False

    def try_hit_player(self, player):
        if not self.alive_flag:
            return
        dist = self.pos.distance_to(player.pos)
        if dist <= (self.radius + player.radius):
            player.take_damage(self.damage)
            self.alive_flag = False

    def draw(self, surf):
        pygame.draw.circle(surf, COLORS["proj"], (int(self.pos.x), int(self.pos.y)), self.radius)


class PoisonMite:
    """Biology melee: Small, fast enemy that applies poison"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 10
        self.speed = 180.0
        self.max_hp = 20
        self.hp = float(self.max_hp)
        self.base_damage = 5
        self.aggro_range = 450.0
        self.attack_range = 35.0
        self.attack_cooldown = 0.6
        self.attack_windup = 0.25
        self._atk_timer = 0.0
        self.state = "idle"  # idle, windup, swing
        self.state_timer = 0.0
        self.flash_timer = 0.0
        
        # Poison application
        self.poison_duration = 3.0
        self.poison_dps = 2.0
    
    def update(self, dt, player):
        self._atk_timer = max(0.0, self._atk_timer - dt)
        self.state_timer = max(0.0, self.state_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        
        dist = self.pos.distance_to(player.pos)
        
        if self.state == "idle":
            # Move toward player
            if dist > self.attack_range * 0.9 and dist <= self.aggro_range:
                direction = (player.pos - self.pos)
                if direction.length_squared() > 0:
                    self.pos += direction.normalize() * self.speed * dt
            
            # Start attack if in range
            if dist <= self.attack_range and self._atk_timer <= 0.0:
                self.state = "windup"
                self.state_timer = self.attack_windup
        
        elif self.state == "windup":
            if self.state_timer <= 0.0:
                if dist <= (self.attack_range + player.radius):
                    player.take_damage(self.base_damage)
                    # Apply poison debuff
                    player.apply_poison(self.poison_duration, self.poison_dps)
                self.state = "swing"
                self.state_timer = 0.12
                self._atk_timer = self.attack_cooldown
        
        elif self.state == "swing":
            if self.state_timer <= 0.0:
                self.state = "idle"
        
        # Clamp to arena
        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))
    
    def take_damage(self, dmg):
        self.hp = max(0.0, self.hp - dmg)
        self.flash_timer = 0.12
    
    def alive(self):
        return self.hp > 0
    
    def draw(self, surf):
        # Draw small poison mite
        color = (100, 255, 100) if self.flash_timer > 0 else (50, 180, 50)
        if self.state == "windup":
            color = COLORS["enemy_windup"]
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # HP bar
        hp_pct = self.hp / self.max_hp
        bar_w = 30
        bar_h = 4
        bar_x = self.pos.x - bar_w/2
        bar_y = self.pos.y - self.radius - 8
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, COLORS["ui_hp"], (bar_x, bar_y, bar_w * hp_pct, bar_h))


class BioEngineer:
    """Biology ranged: Shoots projectiles that heal enemies or poison player"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 13
        self.speed = 110.0
        self.max_hp = 35
        self.hp = float(self.max_hp)
        self.base_damage = 6
        self.aggro_range = 500.0
        self.keep_distance = 220.0
        self.shoot_cd = 1.6
        self.proj_speed = 280.0
        self._shoot_timer = 0.0
        self._heal_timer = 0.0
        self.heal_cooldown = 5.0
        self.projectiles = []
        self.flash_timer = 0.0
    
    def update(self, dt, player):
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self._heal_timer = max(0.0, self._heal_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        
        dist = self.pos.distance_to(player.pos)
        
        # Kiting behavior
        if dist < self.keep_distance * 0.8:
            dir = (self.pos - player.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        elif dist > self.keep_distance * 1.2 and dist <= self.aggro_range:
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        
        # Shoot poison projectile at player
        if dist <= self.aggro_range and self._shoot_timer <= 0.0:
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                v = dir.normalize() * self.proj_speed
                self.projectiles.append(Projectile(self.pos.copy(), v, 5, self.base_damage, 2.5))
                self._shoot_timer = self.shoot_cd
        
        # Update projectiles
        for p in self.projectiles:
            p.update(dt)
        # Remove dead projectiles to prevent memory leak
        self.projectiles = [p for p in self.projectiles if p.alive_flag]
        
        # Clamp to arena
        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))
    
    def take_damage(self, dmg):
        self.hp = max(0.0, self.hp - dmg)
        self.flash_timer = 0.12
    
    def alive(self):
        return self.hp > 0
    
    def draw(self, surf):
        # Draw bio engineer
        color = (150, 255, 150) if self.flash_timer > 0 else (80, 200, 80)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        # Draw cross symbol
        cross_size = 6
        pygame.draw.line(surf, (255, 255, 255), 
                        (self.pos.x - cross_size, self.pos.y),
                        (self.pos.x + cross_size, self.pos.y), 2)
        pygame.draw.line(surf, (255, 255, 255), 
                        (self.pos.x, self.pos.y - cross_size),
                        (self.pos.x, self.pos.y + cross_size), 2)
        
        # HP bar
        hp_pct = self.hp / self.max_hp
        bar_w = 40
        bar_h = 4
        bar_x = self.pos.x - bar_w/2
        bar_y = self.pos.y - self.radius - 8
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, COLORS["ui_hp"], (bar_x, bar_y, bar_w * hp_pct, bar_h))
        
        # Draw projectiles
        for p in self.projectiles:
            if p.alive_flag:
                p.draw(surf)
