import pygame
import math
import random
from config import WIDTH, HEIGHT, ARENA, COLORS
from utils import clamp, circle_hit
from sprite_renderer import draw_enemy_sprite

class Projectile:
    def __init__(self, pos, vel, radius, damage, ttl=3.0, orbiting=False):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius = radius
        self.damage = damage
        self.ttl = ttl
        self.alive_flag = True
        self.orbiting = orbiting
        self.orbit_angle = 0.0
        self.orbit_time = 0.0

    def update(self, dt, player_pos=None):
        if not self.alive_flag:
            return
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive_flag = False
            return
        
        if self.orbiting and player_pos:
            self.orbit_time += dt
            self.orbit_angle += 4.5 * dt
            
            # Orbit for 2 seconds, then fly towards player
            if self.orbit_time < 2.0:
                radius = 90
                self.pos.x = player_pos.x + math.cos(self.orbit_angle) * radius
                self.pos.y = player_pos.y + math.sin(self.orbit_angle) * radius
            else:
                # Chase player after orbit
                direction = (player_pos - self.pos)
                if direction.length_squared() > 0:
                    self.vel = direction.normalize() * 250
                self.pos += self.vel * dt
        else:
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
        color = (180, 220, 255) if self.orbiting else (100, 180, 255)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), int(self.radius))
        if self.orbiting:
            pygame.draw.circle(surf, (150, 200, 255), (int(self.pos.x), int(self.pos.y)), int(self.radius) + 2, 1)

class KineticBrute:
    """Physics melee: absorbs damage while moving, releases on attack"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 18
        self.speed = 85.0
        self.max_hp = 85
        self.hp = float(self.max_hp)
        self.base_damage = 12
        self.aggro_range = 450.0
        self.attack_range = 50.0
        self.attack_cooldown = 1.0
        self.attack_windup = 0.35
        
        self._atk_timer = 0.0
        self.state_timer = 0.0
        self.state = "idle"
        self.flash_timer = 0.0
        self.absorbed_damage = 0.0
        self.was_moving_last_frame = False
        self.moving_timer = 0.0
        
    def update(self, dt, player):
        self._atk_timer = max(0.0, self._atk_timer - dt)
        self.state_timer = max(0.0, self.state_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        
        dist = self.pos.distance_to(player.pos)
        moved_this_frame = False
        
        if self.state == "idle":
            if dist > self.attack_range * 0.9 and dist <= self.aggro_range:
                direction = (player.pos - self.pos)
                if direction.length_squared() > 0:
                    self.pos += direction.normalize() * self.speed * dt
                    moved_this_frame = True
                    self.moving_timer = 0.3
            
            if dist <= self.attack_range and self._atk_timer <= 0.0:
                self.state = "windup"
                self.state_timer = self.attack_windup
        
        elif self.state == "windup":
            if self.state_timer <= 0.0:
                if dist <= (self.attack_range + player.radius):
                    dmg = self.base_damage + int(self.absorbed_damage * 1.5)
                    player.take_damage(dmg)
                    self.absorbed_damage = 0
                self.state = "swing"
                self.state_timer = 0.15
                self._atk_timer = self.attack_cooldown
        
        elif self.state == "swing":
            if self.state_timer <= 0.0:
                self.state = "idle"
        
        self.moving_timer = max(0.0, self.moving_timer - dt)
        self.was_moving_last_frame = moved_this_frame or self.moving_timer > 0
        
        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))
    
    def take_damage(self, dmg):
        if self.was_moving_last_frame:
            reduction = dmg * 0.65
            self.absorbed_damage += reduction
            actual_dmg = dmg - reduction
            self.hp = max(0.0, self.hp - actual_dmg)
        else:
            self.hp = max(0.0, self.hp - dmg)
        self.flash_timer = 0.12
    
    def alive(self):
        return self.hp > 0
    
    def draw(self, surf):
        color = (200, 120, 100) if self.flash_timer > 0 else (160, 90, 70)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw state indicator
        if self.state == "windup":
            pygame.draw.circle(surf, (255, 200, 0), (int(self.pos.x), int(self.pos.y)), self.radius + 8, 2)
        
        # Show absorbed damage stored
        if self.absorbed_damage > 2:
            pygame.draw.circle(surf, (255, 150, 0), (int(self.pos.x), int(self.pos.y)), self.radius + 12, 2)
            absorbed_text = pygame.font.SysFont("arial", 11, bold=True).render(f"+{int(self.absorbed_damage)}", True, (255, 200, 100))
            surf.blit(absorbed_text, (self.pos.x - absorbed_text.get_width()//2, self.pos.y - 35))

class GravityManipulator:
    """Physics ranged: fires orbiting projectiles that chase after"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 16
        self.speed = 115.0
        self.max_hp = 70
        self.hp = float(self.max_hp)
        self.base_damage = 9
        self.aggro_range = 520.0
        self.keep_distance = 280.0
        self.shoot_cd = 1.3
        self._shoot_timer = 0.0
        self.projectiles = []
        self.flash_timer = 0.0
        self.burst_timer = 0.0
        self.burst_mode = False
        
    def update(self, dt, player):
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        self.burst_timer -= dt
        
        dist = self.pos.distance_to(player.pos)
        
        # Burst mode every 6 seconds
        if self.burst_timer <= 0:
            self.burst_mode = True
            self.burst_timer = 6.0
        
        if self.burst_mode and self.burst_timer > 5.0:
            self.burst_mode = False
        
        # Kiting behavior
        if dist < self.keep_distance * 0.7:
            dir = (self.pos - player.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        elif dist > self.keep_distance * 1.3 and dist <= self.aggro_range:
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        
        # Shoot orbiting projectiles
        if dist <= self.aggro_range and self._shoot_timer <= 0.0:
            if self.burst_mode:
                # Fire 3 projectiles in burst
                for angle_offset in [0, 2.09, 4.19]:
                    v = pygame.Vector2(math.cos(angle_offset) * 200, math.sin(angle_offset) * 200)
                    proj = Projectile(self.pos.copy(), v, 7, self.base_damage, 4.5, orbiting=True)
                    self.projectiles.append(proj)
                self._shoot_timer = 0.5
            else:
                # Normal single projectile
                v = pygame.Vector2(0, 280)
                proj = Projectile(self.pos.copy(), v, 8, self.base_damage, 4.0, orbiting=True)
                self.projectiles.append(proj)
                self._shoot_timer = self.shoot_cd
        
        for p in self.projectiles:
            p.update(dt, player.pos)
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
        color = (150, 180, 220) if self.flash_timer > 0 else (120, 150, 200)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw burst indicator
        if self.burst_mode and int(self.burst_timer * 5) % 2 == 0:
            pygame.draw.circle(surf, (100, 200, 255), (int(self.pos.x), int(self.pos.y)), self.radius + 6, 2)
        
        # Draw projectiles
        for p in self.projectiles:
            if p.alive_flag:
                p.draw(surf)