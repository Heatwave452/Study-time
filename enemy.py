import pygame
import math
import random
from config import (MATH_SWORDSMAN, MATH_ARCHER, EXAM_BOSS,
                    COLORS, WIDTH, HEIGHT, ARENA)
from utils import clamp, circle_hit, draw_triangle
from sprite_renderer import draw_enemy_sprite, draw_projectile_trail

# ---------------------------
# Math Archer projectile
# ---------------------------
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

        # simple wall bounce prevention: kill if outside arena
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
        # small pointing triangle for direction feel
        angle = math.atan2(self.vel.y, self.vel.x)
        draw_triangle(surf, (self.pos.x, self.pos.y), angle, self.radius + 6, COLORS["proj"])


# ---------------------------
# Math Swordsman (melee) with visible attack
# ---------------------------
class MathSwordsman:
    """
    Walks toward player. When in attack range, it does a visible windup before applying damage.
    Line length: +1 every 20s; if reaches 5, next hit deals double damage and resets to 1.
    """
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 16
        self.speed = MATH_SWORDSMAN["move_speed"]
        self.max_hp = MATH_SWORDSMAN["max_hp"]
        self.hp = float(self.max_hp)
        self.base_damage = MATH_SWORDSMAN["base_damage"]
        self.aggro_range = MATH_SWORDSMAN["aggro_range"]
        self.attack_range = MATH_SWORDSMAN["attack_range"]
        self.attack_cooldown = MATH_SWORDSMAN["attack_cooldown"]
        self.attack_windup = MATH_SWORDSMAN["attack_windup"]
        self._atk_timer = 0.0

        # line-length mechanic
        self.line_len = 1
        self._line_timer = 0.0
        self._line_tick = MATH_SWORDSMAN["line_len_tick"]
        
        # Animation
        self.animation_time = 0.0

        # attack state visuals
        self.state = "idle"  # idle, windup, swing
        self.state_timer = 0.0
        self.flash_timer = 0.0

    def update(self, dt, player):
        # Animation time
        self.animation_time += dt
        
        # line length growth
        self._line_timer += dt
        if self._line_timer >= self._line_tick:
            self._line_timer -= self._line_tick
            self.line_len = min(5, self.line_len + 1)

        # cooldown
        self._atk_timer = max(0.0, self._atk_timer - dt)
        self.state_timer = max(0.0, self.state_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)

        # behavior
        dist = self.pos.distance_to(player.pos)

        if self.state == "idle":
            # move toward player if far
            if dist > self.attack_range * 0.9 and dist <= self.aggro_range:
                direction = (player.pos - self.pos)
                if direction.length_squared() > 0:
                    self.pos += direction.normalize() * self.speed * dt
            # start windup if in range and off cooldown
            if dist <= self.attack_range and self._atk_timer <= 0.0:
                self.state = "windup"
                self.state_timer = self.attack_windup

        elif self.state == "windup":
            # do nothing but show windup
            if self.state_timer <= 0.0:
                # apply damage if still in range
                if dist <= (self.attack_range + player.radius):
                    dmg = self.base_damage
                    if self.line_len >= 5:
                        dmg *= 2
                        self.line_len = 1
                    player.take_damage(dmg)
                self.state = "swing"
                self.state_timer = 0.15
                self._atk_timer = self.attack_cooldown

        elif self.state == "swing":
            if self.state_timer <= 0.0:
                self.state = "idle"

        # clamp to arena
        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))

    def take_damage(self, dmg):
        self.hp = max(0.0, self.hp - dmg)
        self.flash_timer = 0.12

    def alive(self):
        return self.hp > 0

    def draw(self, surf):
        # Draw using sprite renderer
        draw_enemy_sprite(surf, self.pos, self.radius, 'math', self.state, self.animation_time)
        
        # Flash effect when hit
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            alpha = int(150 * (self.flash_timer / 0.12))
            pygame.draw.circle(flash_surf, (255, 255, 255, alpha), (self.radius * 2, self.radius * 2), self.radius * 2)
            surf.blit(flash_surf, (int(self.pos.x) - self.radius * 2, int(self.pos.y) - self.radius * 2))
        
        # HP bar
        hp_pct = self.hp / self.max_hp
        bar_w = 40
        bar_h = 4
        bar_x = self.pos.x - bar_w/2
        bar_y = self.pos.y - self.radius - 24
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, COLORS["ui_hp"], (bar_x, bar_y, bar_w * hp_pct, bar_h))
        
        # visualize line length ticks
        x = int(self.pos.x); y = int(self.pos.y + self.radius + 8)
        for i in range(self.line_len):
            pygame.draw.line(surf, (230, 230, 255), (x - 18 + i*8, y), (x - 14 + i*8, y), 2)


# ---------------------------
# Math Archer (ranged)
# ---------------------------
class MathArcher:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 15
        self.speed = MATH_ARCHER["move_speed"]
        self.max_hp = MATH_ARCHER["max_hp"]
        self.hp = float(self.max_hp)
        self.base_damage = MATH_ARCHER["base_damage"]
        self.aggro_range = MATH_ARCHER["aggro_range"]
        self.keep_distance = MATH_ARCHER["keep_distance"]
        self.shoot_cd = MATH_ARCHER["shoot_cooldown"]
        self.proj_speed = MATH_ARCHER["projectile_speed"]
        self.proj_radius = MATH_ARCHER["projectile_radius"]
        self._shoot_timer = 0.0

        self.shield_active = False
        self.shield_timer = 0.0
        self.shield_cd = 0.0
        self.shield_dur = MATH_ARCHER["close_shield_duration"]
        self.shield_cooldown_total = MATH_ARCHER["close_shield_cooldown"]
        self.shield_trigger = MATH_ARCHER["close_shield_trigger"]
        
        self.projectiles = []
        self.flash_timer = 0.0
        self.state = "idle"
        self.animation_time = 0.0

    def update(self, dt, player):
        # Animation time
        self.animation_time += dt
        
        # timers
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        if self.shield_active:
            self.shield_timer = max(0.0, self.shield_timer - dt)
            if self.shield_timer <= 0.0:
                self.shield_active = False
                self.shield_cd = self.shield_cooldown_total
        else:
            self.shield_cd = max(0.0, self.shield_cd - dt)

        # distance control
        dist = self.pos.distance_to(player.pos)
        if dist < self.keep_distance * 0.9:
            # kite away
            dir = (self.pos - player.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt
        elif dist > self.keep_distance * 1.15 and dist <= self.aggro_range:
            # move closer (within aggro)
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                self.pos += dir.normalize() * self.speed * dt

        # shield if player too close
        if dist <= self.shield_trigger and not self.shield_active and self.shield_cd <= 0.0:
            self.shield_active = True
            self.shield_timer = self.shield_dur

        # shoot at player
        if dist <= self.aggro_range and self._shoot_timer <= 0.0:
            dir = (player.pos - self.pos)
            if dir.length_squared() > 0:
                v = dir.normalize() * self.proj_speed
                self.projectiles.append(
                    Projectile(self.pos, v, self.proj_radius, self.base_damage)
                )
                self._shoot_timer = self.shoot_cd

        # update projectiles
        for p in self.projectiles:
            p.update(dt)
        # remove dead projectiles to prevent memory leak
        self.projectiles = [p for p in self.projectiles if p.alive_flag]

        margin = ARENA["margin"]
        self.pos.x = max(margin, min(WIDTH - margin, self.pos.x))
        self.pos.y = max(margin, min(HEIGHT - margin, self.pos.y))

    def take_damage(self, dmg):
        if self.shield_active:
            # shield blocks damage
            return
        self.hp = max(0.0, self.hp - dmg)
        self.flash_timer = 0.12

    def alive(self):
        return self.hp > 0

    def draw(self, surf):
        # Draw sprite
        draw_enemy_sprite(surf, self.pos, self.radius, 'math', self.state, self.animation_time)
        
        # Shield active indicator
        if self.shield_active:
            pygame.draw.circle(surf, (160, 255, 220), (int(self.pos.x), int(self.pos.y)), self.radius + 8, 3)
        
        # Flash effect when hit
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            alpha = int(150 * (self.flash_timer / 0.12))
            pygame.draw.circle(flash_surf, (255, 255, 255, alpha), (self.radius * 2, self.radius * 2), self.radius * 2)
            surf.blit(flash_surf, (int(self.pos.x) - self.radius * 2, int(self.pos.y) - self.radius * 2))
        
        # HP bar
        hp_pct = self.hp / self.max_hp
        bar_w = 40
        bar_h = 4
        bar_x = self.pos.x - bar_w/2
        bar_y = self.pos.y - self.radius - 24
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, COLORS["ui_hp"], (bar_x, bar_y, bar_w * hp_pct, bar_h))
        
        # Draw projectiles
        for p in self.projectiles:
            if p.alive_flag:
                p.draw(surf)


# ---------------------------
# Exam Boss
# ---------------------------
class ExamBoss(MathSwordsman):
    """Boss version of Math Swordsman — faster, tougher, and stronger."""
    def __init__(self, pos):
        super().__init__(pos)
        self.max_hp = EXAM_BOSS["max_hp"]
        self.hp = float(self.max_hp)
        self.base_damage = EXAM_BOSS["base_damage"]
        self.speed = EXAM_BOSS["move_speed"]
        self.attack_cooldown = EXAM_BOSS["attack_cooldown"]
        self.attack_windup = EXAM_BOSS["attack_windup"]
        self.radius = 28
        
        # NEW: Phase system for boss
        self.phase = 1  # Phase 1: 100-67%, Phase 2: 67-34%, Phase 3: 34-0%
        self.projectiles = []  # NEW: Boss can shoot projectiles in phase 3

    def update(self, dt, player):
        # Update phase based on HP
        hp_pct = self.hp / self.max_hp
        if hp_pct < 0.34:
            self.phase = 3
        elif hp_pct < 0.67:
            self.phase = 2
        else:
            self.phase = 1
        
        # Call parent update (handles movement and melee attacks)
        super().update(dt, player)
        
        # NEW: Phase 3 ranged attack
        if self.phase == 3:
            if not hasattr(self, '_shoot_timer'):
                self._shoot_timer = 0.0
            self._shoot_timer = max(0.0, self._shoot_timer - dt)
            
            dist = self.pos.distance_to(player.pos)
            if dist <= self.aggro_range * 1.2 and self._shoot_timer <= 0.0:
                # Fire 3 projectiles in a spread
                for angle_offset in [-0.4, 0, 0.4]:
                    dir = (player.pos - self.pos).normalize()
                    vel_x = dir.x * 200 * math.cos(angle_offset) - dir.y * 200 * math.sin(angle_offset)
                    vel_y = dir.x * 200 * math.sin(angle_offset) + dir.y * 200 * math.cos(angle_offset)
                    proj = Projectile(self.pos.copy(), pygame.Vector2(vel_x, vel_y), 8, self.base_damage - 3)
                    self.projectiles.append(proj)
                self._shoot_timer = 1.5
        
        # Update projectiles
        for p in self.projectiles:
            p.update(dt)

    def draw(self, surf):
        # Draw boss sprite (larger math enemy)
        draw_enemy_sprite(surf, self.pos, self.radius, 'math', self.state, self.animation_time)
        
        # Flash effect when hit
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            alpha = int(150 * (self.flash_timer / 0.12))
            pygame.draw.circle(flash_surf, (255, 255, 255, alpha), (self.radius * 2, self.radius * 2), self.radius * 2)
            surf.blit(flash_surf, (int(self.pos.x) - self.radius * 2, int(self.pos.y) - self.radius * 2))
        
        # NEW: Phase indicator ring
        phase_color = (255, 255, 100) if self.phase == 3 else (255, 200, 100) if self.phase == 2 else (255, 150, 100)
        pygame.draw.circle(surf, phase_color, (int(self.pos.x), int(self.pos.y)), self.radius + 14, 3)
        
        # NEW: Phase text
        phase_text = pygame.font.SysFont("arial", 14, bold=True).render(f"Phase {self.phase}", True, phase_color)
        surf.blit(phase_text, (self.pos.x - phase_text.get_width()//2, self.pos.y - 45))
        
        # NEW: HP bar (larger for boss)
        hp_pct = self.hp / self.max_hp
        bar_w = 70
        bar_h = 6
        bar_x = self.pos.x - bar_w/2
        bar_y = self.pos.y - self.radius - 60
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, COLORS["ui_hp"], (bar_x, bar_y, bar_w * hp_pct, bar_h))
        
        # Draw projectiles
        for p in self.projectiles:
            if p.alive_flag:
                p.draw(surf)