import pygame
import random
import math
from config import PLAYER, COLORS, ARENA, WIDTH, HEIGHT
from utils import vec2_from_keys, clamp
from sprite_renderer import draw_player_sprite, draw_slash_effect

class Player:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 16
        self.speed = PLAYER["move_speed"]
        self.max_hp = PLAYER["max_hp"]
        self.hp = float(self.max_hp)
        self.melee_damage = PLAYER["melee_damage"]
        self.attack_cooldown = PLAYER["attack_cooldown"]
        self.attack_range = PLAYER["attack_range"]
        self.i_frames = PLAYER["i_frames"]
        self._atk_timer = 0.0
        self._ifr_timer = 0.0
        self.attacking = False
        self.attack_visual_timer = 0.0
        
        # Poison debuff system
        self.poison_timer = 0.0
        self.poison_damage_per_tick = 0.0
        self.poison_defense_reduction = 0.0
        
        # Dash ability
        self.dash_cooldown = 1.5
        self._dash_timer = 0.0
        self.is_dashing = False
        self.dash_direction = pygame.Vector2(1, 0)
        self.dash_speed = 600.0
        self.dash_duration = 0.3
        self._dash_duration_timer = 0.0
        self.dash_damage_reduction = 0.4
        
        # Crit system
        self.crit_chance = 0.15
        self.crit_multiplier = 2.0
        self.crit_timer = 0.0
        
        # Combo system
        self.combo_count = 0
        self.combo_timer = 0.0
        self.combo_timeout = 2.0
        self.max_combo = 0
        
        # Parry ability
        self.parry_cooldown = 2.0
        self._parry_timer = 0.0
        self.parrying = False
        self.parry_duration = 0.4
        self._parry_duration_timer = 0.0
        
        # NEW: Ultimate ability (Berserk Mode)
        self.ultimate_cooldown = 8.0
        self._ultimate_timer = 0.0
        self.berserk_active = False
        self.berserk_duration = 5.0
        self._berserk_timer = 0.0
        self.berserk_damage_mult = 2.5
        self.berserk_speed_mult = 1.5
        
        # NEW: Ultimate charge meter
        self.ultimate_charge = 0.0
        self.ultimate_max_charge = 100.0
        
        # Buffs
        self.damage_buff = 1.0
        self.speed_buff = 1.0
        
        # XP and Leveling System
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.total_kills = 0
        self.score = 0
        
        # Special attacks
        self.charged_attack_time = 0.0
        self.charged_attack_ready = False
        self.charged_attack_damage_mult = 3.0
        self.area_attack_cooldown = 5.0
        self._area_attack_timer = 0.0
        
        # Animation state
        self.animation_time = 0.0
        self.facing_angle = 0.0  # Direction player is facing
        self.slash_timer = 0.0  # For attack animation
        self.slash_angle = 0.0
        self.last_movement = pygame.Vector2(1, 0)  # Track last movement for facing
        self._area_attack_timer = 0.0
        
        # Cache fonts for performance
        self.combo_font = pygame.font.SysFont("arial", 16, bold=True)
        self.level_up_timer = 0.0  # For level up animation

    def apply_poison(self, duration, dps):
        self.poison_timer = max(self.poison_timer, duration)
        self.poison_damage_per_tick = dps
        self.poison_defense_reduction = 0.3

    def try_dash(self, direction):
        if self._dash_timer <= 0.0 and direction.length_squared() > 0:
            self._dash_timer = self.dash_cooldown
            self.is_dashing = True
            self._dash_duration_timer = self.dash_duration
            self.dash_direction = direction.normalize()
            return True
        return False

    def try_parry(self):
        if self._parry_timer <= 0.0:
            self._parry_timer = self.parry_cooldown
            self.parrying = True
            self._parry_duration_timer = self.parry_duration
            return True
        return False

    # NEW: Ultimate ability
    def try_ultimate(self):
        """Activate Berserk Mode - increased damage & speed"""
        if self.ultimate_charge >= self.ultimate_max_charge:
            self.berserk_active = True
            self._berserk_timer = self.berserk_duration
            self.ultimate_charge = 0.0
            return True
        return False

    def update(self, dt, keys):
        # Update animation time
        self.animation_time += dt
        
        # Movement with speed buff
        dir = vec2_from_keys(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        
        # Track facing direction
        if dir.length_squared() > 0:
            self.last_movement = dir.normalize()
            self.facing_angle = math.atan2(dir.y, dir.x)
        
        if self.is_dashing:
            self._dash_duration_timer -= dt
            self.pos += self.dash_direction * self.dash_speed * dt
            if self._dash_duration_timer <= 0:
                self.is_dashing = False
        else:
            # NEW: Apply berserk speed mult
            speed_mult = self.berserk_speed_mult if self.berserk_active else self.speed_buff
            self.pos += dir * self.speed * speed_mult * dt
        
        # Clamp to arena
        margin = ARENA["margin"]
        self.pos.x = clamp(self.pos.x, margin, WIDTH - margin)
        self.pos.y = clamp(self.pos.y, margin, HEIGHT - margin)
        
        # Timers
        self._atk_timer = max(0.0, self._atk_timer - dt)
        self._ifr_timer = max(0.0, self._ifr_timer - dt)
        self.attack_visual_timer = max(0.0, self.attack_visual_timer - dt)
        self._dash_timer = max(0.0, self._dash_timer - dt)
        self._parry_timer = max(0.0, self._parry_timer - dt)
        self._ultimate_timer = max(0.0, self._ultimate_timer - dt)
        self.crit_timer = max(0.0, self.crit_timer - dt)
        self.level_up_timer = max(0.0, self.level_up_timer - dt)
        self._area_attack_timer = max(0.0, self._area_attack_timer - dt)
        self.slash_timer = max(0.0, self.slash_timer - dt)
        self.crit_timer = max(0.0, self.crit_timer - dt)
        self.level_up_timer = max(0.0, self.level_up_timer - dt)
        self._area_attack_timer = max(0.0, self._area_attack_timer - dt)
        
        # NEW: Berserk mode
        if self.berserk_active:
            self._berserk_timer -= dt
            if self._berserk_timer <= 0:
                self.berserk_active = False
        
        # Parry duration
        if self.parrying:
            self._parry_duration_timer -= dt
            if self._parry_duration_timer <= 0:
                self.parrying = False
        
        # Combo timeout
        self.combo_timer -= dt
        if self.combo_timer <= 0:
            self.combo_count = 0
        
        # Apply poison damage
        if self.poison_timer > 0:
            self.poison_timer -= dt
            self.hp -= self.poison_damage_per_tick * dt
            if self.poison_timer <= 0:
                self.poison_defense_reduction = 0.0
        
        if self.attack_visual_timer == 0:
            self.attacking = False

    def try_attack(self):
        if self._atk_timer <= 0.0:
            self._atk_timer = self.attack_cooldown
            self.attacking = True
            self.attack_visual_timer = 0.12
            self.combo_timer = self.combo_timeout
            self.combo_count += 1
            self.max_combo = max(self.max_combo, self.combo_count)
            
            # Set slash animation
            self.slash_timer = 0.3  # Duration of slash animation
            self.slash_angle = self.facing_angle
            
            # Check for charged attack
            if self.charged_attack_ready:
                self.charged_attack_ready = False
                self.charged_attack_time = 0.0
            
            # NEW: Charge ultimate
            self.ultimate_charge = min(self.ultimate_max_charge, self.ultimate_charge + 10)
            return True
        return False
    
    def try_area_attack(self):
        """Area attack - hits all enemies in larger radius"""
        if self._area_attack_timer <= 0.0:
            self._area_attack_timer = self.area_attack_cooldown
            return True
        return False

    def get_damage(self):
        base_dmg = (self.melee_damage + (self.combo_count - 1) * 2) * self.damage_buff
        
        # Apply charged attack multiplier
        if self.charged_attack_ready:
            base_dmg *= self.charged_attack_damage_mult
        
        # NEW: Apply berserk multiplier
        if self.berserk_active:
            base_dmg *= self.berserk_damage_mult
        
        if random.random() < self.crit_chance:
            self.crit_timer = 0.15
            return int(base_dmg * self.crit_multiplier)
        return int(base_dmg)

    def take_damage(self, dmg):
        if self._ifr_timer > 0.0:
            return False
        
        if self.parrying:
            self.parrying = False
            return False
        
        if self.is_dashing:
            dmg = int(dmg * (1.0 - self.dash_damage_reduction))
        
        self.hp = max(0.0, self.hp - dmg)
        self._ifr_timer = self.i_frames
        
        # NEW: Charge ultimate on hit taken
        self.ultimate_charge = min(self.ultimate_max_charge, self.ultimate_charge + 5)
        return True

    def alive(self):
        return self.hp > 0
    
    def gain_xp(self, amount):
        """Gain XP and check for level up"""
        self.xp += amount
        self.score += amount
        
        if self.xp >= self.xp_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Level up and gain stat bonuses"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        
        # Stat increases
        self.max_hp += 10
        self.hp = min(self.max_hp, self.hp + 20)  # Heal 20 HP on level up
        self.melee_damage += 2
        self.attack_range += 2
        
        # Visual feedback
        self.level_up_timer = 2.0
        
        # Charge ultimate on level up
        self.ultimate_charge = min(self.ultimate_max_charge, self.ultimate_charge + 25)
    
    def add_kill(self):
        """Track kills for stats"""
        self.total_kills += 1

    def draw(self, surf):
        # Determine state for sprite rendering
        if self.is_dashing:
            sprite_state = 'dashing'
        elif self.parrying:
            sprite_state = 'parrying'
        elif self.attacking:
            sprite_state = 'attacking'
        else:
            sprite_state = 'normal'
        
        # NEW: Berserk glow with pulsing effect
        if self.berserk_active:
            for radius in [self.radius + 15, self.radius + 12, self.radius + 9]:
                alpha = 100 if radius == self.radius + 9 else 50
                glow_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 50, 50, alpha), (radius + 5, radius + 5), radius)
                surf.blit(glow_surf, (int(self.pos.x) - radius - 5, int(self.pos.y) - radius - 5))
        
        # Draw dash trail if dashing
        if self.is_dashing:
            glow_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 255, 200, 80), (self.radius * 1.5, self.radius * 1.5), self.radius + 5)
            surf.blit(glow_surf, (int(self.pos.x) - self.radius * 1.5, int(self.pos.y) - self.radius * 1.5))
        
        # Draw player sprite
        draw_player_sprite(surf, self.pos, self.radius, sprite_state, self.facing_angle, self.animation_time)
        
        # Draw slash effect when attacking
        if self.slash_timer > 0:
            progress = 1.0 - (self.slash_timer / 0.3)
            slash_color = (255, 100, 100) if self.crit_timer > 0 else (255, 200, 100)
            draw_slash_effect(surf, self.pos, self.slash_angle, self.attack_range, progress, slash_color)
        
        # Draw parry shield with glow
        if self.parrying:
            shield_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (255, 200, 100, 80), (self.radius * 1.5, self.radius * 1.5), self.radius + 10)
            surf.blit(shield_surf, (int(self.pos.x) - self.radius * 1.5, int(self.pos.y) - self.radius * 1.5))
            pygame.draw.circle(surf, (255, 200, 100), (int(self.pos.x), int(self.pos.y)), self.radius + 8, 3)
        
        # Draw poison indicator
        if self.poison_timer > 0:
            pygame.draw.circle(surf, COLORS["poison"], (int(self.pos.x), int(self.pos.y)), self.radius + 4, 2)
        
        # Draw combo counter
        if self.combo_count > 1:
            combo_color = (255, 255, 100) if self.crit_timer == 0 else (255, 100, 100)
            combo_text = self.combo_font.render(f"x{self.combo_count}", True, combo_color)
            surf.blit(combo_text, (self.pos.x + 18, self.pos.y - 22))
        
        # Draw dash cooldown
        if self._dash_timer > 0:
            cooldown_pct = 1.0 - (self._dash_timer / self.dash_cooldown)
            arc_radius = self.radius + 8
            pygame.draw.arc(surf, (150, 200, 255), 
                           (self.pos.x - arc_radius, self.pos.y - arc_radius, arc_radius * 2, arc_radius * 2),
                           0, cooldown_pct * 6.28, 2)
        
        # Draw parry cooldown
        if self._parry_timer > 0:
            cooldown_pct = 1.0 - (self._parry_timer / self.parry_cooldown)
            arc_radius = self.radius + 14
            pygame.draw.arc(surf, (255, 180, 100), 
                           (self.pos.x - arc_radius, self.pos.y - arc_radius, arc_radius * 2, arc_radius * 2),
                           0, cooldown_pct * 6.28, 2)