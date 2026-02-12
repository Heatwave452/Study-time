import pygame
import math
import random  # ADD AT TOP
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
            return True
        return False

    def draw(self, surf):
        pygame.draw.circle(surf, COLORS["proj"], (int(self.pos.x), int(self.pos.y)), int(self.radius))

class BinaryBlade:
    """CS Hacker: melee with consecutive hit scaling"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 16
        self.speed = 135.0
        self.max_hp = 65
        self.hp = float(self.max_hp)
        self.base_damage = 9
        self.aggro_range = 400.0
        self.attack_range = 45.0
        self.attack_cooldown = 0.8
        self.attack_windup = 0.3
        
        self._atk_timer = 0.0
        self.state_timer = 0.0
        self.state = "idle"
        self.flash_timer = 0.0
        self.consecutive_hits = 1
        self._teleport_timer = 60.0
        
    def update(self, dt, player):
        self._atk_timer = max(0.0, self._atk_timer - dt)
        self.state_timer = max(0.0, self.state_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        self._teleport_timer -= dt
        
        dist = self.pos.distance_to(player.pos)
        
        if self._teleport_timer <= 0:
            direction = (player.pos - self.pos).normalize() if dist > 0 else pygame.Vector2(1, 0)
            self.pos = player.pos - direction * 60
            self._teleport_timer = 60.0
            self.consecutive_hits = 0
        
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
                    dmg = self.base_damage + self.consecutive_hits
                    player.take_damage(dmg)
                    self.consecutive_hits += 1
                else:
                    self.consecutive_hits = 0
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
        color = (200, 150, 255) if self.flash_timer > 0 else (180, 120, 255)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surf, (150, 100, 200), (int(self.pos.x), int(self.pos.y)), self.radius + 6, 1)
        
        hit_text = pygame.font.SysFont("arial", 12).render(str(self.consecutive_hits), True, (255, 255, 100))
        surf.blit(hit_text, (self.pos.x - 7, self.pos.y - 7))

class BugSwarm:
    """CS Bug Swarm: ranged enemy shooting error code projectiles"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 14
        self.speed = 125.0
        self.max_hp = 48
        self.hp = float(self.max_hp)
        self.base_damage = 7
        self.aggro_range = 500.0
        self.keep_distance = 240.0
        self.shoot_cd = 1.4
        self.proj_speed = 320.0
        self._shoot_timer = 0.0
        self.projectiles = []
        self.flash_timer = 0.0
        self._homing_spawn_timer = 0.0
        
    def update(self, dt, player):
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        self._homing_spawn_timer -= dt
        
        dist = self.pos.distance_to(player.pos)
        
        if dist < self.keep_distance * 0.8:
            dir = (self.pos - player.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        elif dist > self.keep_distance * 1.2 and dist <= self.aggro_range:
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        
        if dist <= self.aggro_range and self._shoot_timer <= 0.0:
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                v = dir.normalize() * self.proj_speed
                self.projectiles.append(Projectile(self.pos.copy(), v, 6, self.base_damage, 2.5))
                self._shoot_timer = self.shoot_cd
        
        if self._homing_spawn_timer <= 0:
            self._homing_spawn_timer = 4.0
            if dist <= self.aggro_range:
                for _ in range(random.randint(2, 3)):
                    angle = random.uniform(0, 6.28)
                    vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * 150
                    self.projectiles.append(Projectile(self.pos.copy(), vel, 5, self.base_damage - 1, 8.0))
        
        for p in self.projectiles:
            p.update(dt)
        # remove dead projectiles to prevent memory leak
        self.projectiles = [p for p in self.projectiles if p.alive_flag]
        
        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))
    
    def take_damage(self, dmg):
        self.hp = max(0.0, self.hp - dmg)
        self.flash_timer = 0.12
    
    def alive(self):
        return self.hp > 0
    
    def draw(self, surf):
        color = (200, 100, 150) if self.flash_timer > 0 else (180, 80, 140)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        for p in self.projectiles:
            if p.alive_flag:
                p.draw(surf)