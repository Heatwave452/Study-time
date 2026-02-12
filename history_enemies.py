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


class AncientWarrior:
    """History melee: Heavily armored with shield bash stun"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 18
        self.speed = 85.0
        self.max_hp = 55
        self.hp = float(self.max_hp)
        self.base_damage = 12
        self.aggro_range = 400.0
        self.attack_range = 45.0
        self.attack_cooldown = 1.0
        self.attack_windup = 0.4
        self._atk_timer = 0.0
        self.state = "idle"  # idle, windup, swing
        self.state_timer = 0.0
        self.flash_timer = 0.0
        
        # Shield bash ability
        self.bash_cooldown = 6.0
        self._bash_timer = 0.0
    
    def update(self, dt, player):
        self._atk_timer = max(0.0, self._atk_timer - dt)
        self._bash_timer = max(0.0, self._bash_timer - dt)
        self.state_timer = max(0.0, self.state_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        
        dist = self.pos.distance_to(player.pos)
        
        if self.state == "idle":
            # Move toward player slowly (heavily armored)
            if dist > self.attack_range * 0.9 and dist <= self.aggro_range:
                direction = (player.pos - self.pos)
                if direction.length_squared() > 0:
                    self.pos += direction.normalize() * self.speed * dt
            
            # Start attack if in range
            if dist <= self.attack_range and self._atk_timer <= 0.0:
                # Use shield bash if available and close
                if self._bash_timer <= 0.0 and dist <= self.attack_range * 0.7:
                    self.state = "bash"
                    self.state_timer = 0.3
                    self._bash_timer = self.bash_cooldown
                else:
                    self.state = "windup"
                    self.state_timer = self.attack_windup
        
        elif self.state == "bash":
            if self.state_timer <= 0.0:
                if dist <= (self.attack_range + player.radius):
                    player.take_damage(self.base_damage * 1.5)
                    # TODO: Apply stun effect when implemented
                self.state = "idle"
                self._atk_timer = self.attack_cooldown
        
        elif self.state == "windup":
            if self.state_timer <= 0.0:
                if dist <= (self.attack_range + player.radius):
                    player.take_damage(self.base_damage)
                self.state = "swing"
                self.state_timer = 0.15
                self._atk_timer = self.attack_cooldown
        
        elif self.state == "swing":
            if self.state_timer <= 0.0:
                self.state = "idle"
        
        # Clamp to arena
        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))
    
    def take_damage(self, dmg):
        # Heavy armor reduces damage by 20%
        reduced_dmg = dmg * 0.8
        self.hp = max(0.0, self.hp - reduced_dmg)
        self.flash_timer = 0.12
    
    def alive(self):
        return self.hp > 0
    
    def draw(self, surf):
        # Draw ancient warrior with shield
        color = (220, 180, 120) if self.flash_timer > 0 else (150, 120, 80)
        if self.state == "windup":
            color = COLORS["enemy_windup"]
        elif self.state == "bash":
            color = (255, 200, 100)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw shield
        shield_offset = 8
        pygame.draw.circle(surf, (100, 100, 120), 
                          (int(self.pos.x - shield_offset), int(self.pos.y)), 
                          self.radius // 2, 2)
        
        # HP bar
        hp_pct = self.hp / self.max_hp
        bar_w = 50
        bar_h = 5
        bar_x = self.pos.x - bar_w/2
        bar_y = self.pos.y - self.radius - 10
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, COLORS["ui_hp"], (bar_x, bar_y, bar_w * hp_pct, bar_h))


class ArtilleryCommander:
    """History ranged: Calls down cannon fire and summons foot soldiers"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 14
        self.speed = 95.0
        self.max_hp = 40
        self.hp = float(self.max_hp)
        self.base_damage = 10
        self.aggro_range = 550.0
        self.keep_distance = 300.0
        self.shoot_cd = 2.0
        self.proj_speed = 200.0
        self._shoot_timer = 0.0
        self.projectiles = []
        self.flash_timer = 0.0
    
    def update(self, dt, player):
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        
        dist = self.pos.distance_to(player.pos)
        
        # Kiting behavior - stay at distance
        if dist < self.keep_distance * 0.7:
            dir = (self.pos - player.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        elif dist > self.keep_distance * 1.3 and dist <= self.aggro_range:
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        
        # Fire cannon shot (slow but powerful)
        if dist <= self.aggro_range and self._shoot_timer <= 0.0:
            # Predict player position slightly for better aim
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                v = dir.normalize() * self.proj_speed
                # Create larger, slower projectile
                self.projectiles.append(Projectile(self.pos.copy(), v, 8, self.base_damage, 4.0))
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
        # Draw artillery commander
        color = (200, 150, 100) if self.flash_timer > 0 else (140, 100, 60)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw cannon symbol
        pygame.draw.line(surf, (80, 80, 80), 
                        (self.pos.x, self.pos.y),
                        (self.pos.x + self.radius, self.pos.y - 5), 3)
        
        # HP bar
        hp_pct = self.hp / self.max_hp
        bar_w = 45
        bar_h = 4
        bar_x = self.pos.x - bar_w/2
        bar_y = self.pos.y - self.radius - 8
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, COLORS["ui_hp"], (bar_x, bar_y, bar_w * hp_pct, bar_h))
        
        # Draw projectiles
        for p in self.projectiles:
            if p.alive_flag:
                # Draw cannonballs darker
                pygame.draw.circle(surf, (60, 60, 60), 
                                 (int(p.pos.x), int(p.pos.y)), p.radius)
