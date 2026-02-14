"""
Sprite Renderer Module - Provides functions to draw sprite-like characters and effects
instead of simple circles. Creates more polished, game-like visuals.
"""
import pygame
import math
from config import COLORS


def draw_player_sprite(surf, pos, radius, state, facing_angle=0, animation_time=0):
    """
    Draw a humanoid player sprite with animations
    
    Args:
        surf: Surface to draw on
        pos: (x, y) position
        radius: Base size of the sprite
        state: 'normal', 'dashing', 'parrying', 'attacking'
        facing_angle: Angle the player is facing (0 = right)
        animation_time: Time for animation cycles
    """
    x, y = int(pos[0]), int(pos[1])
    
    # Body parts
    body_height = radius * 2
    body_width = radius * 1.2
    head_radius = radius * 0.6
    
    # Animation bobbing
    bob = math.sin(animation_time * 8) * 2 if state == 'normal' else 0
    
    # Calculate facing direction for flipping
    flip = facing_angle > math.pi / 2 and facing_angle < 3 * math.pi / 2
    direction = -1 if flip else 1
    
    # Color based on state
    if state == 'dashing':
        body_color = (100, 255, 200)
        outline_color = (50, 200, 150)
    elif state == 'parrying':
        body_color = (255, 200, 100)
        outline_color = (200, 150, 50)
    elif state == 'attacking':
        body_color = COLORS["player"]
        outline_color = (50, 150, 200)
    else:
        body_color = COLORS["player"]
        outline_color = (50, 150, 200)
    
    # Draw shadow
    shadow_surf = pygame.Surface((radius * 3, radius // 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect())
    surf.blit(shadow_surf, (x - radius * 1.5, y + radius * 1.5))
    
    # Legs
    leg_width = radius * 0.4
    leg_height = radius * 0.8
    leg_offset = radius * 0.3
    
    # Animated leg positions
    leg_swing = math.sin(animation_time * 10) * 3 if state == 'normal' else 0
    
    # Left leg
    left_leg = [
        (x - leg_offset * direction, y + bob),
        (x - leg_offset * direction, y + leg_height + bob),
        (x - (leg_offset - leg_width) * direction, y + leg_height + bob + leg_swing),
        (x - (leg_offset - leg_width) * direction, y + bob)
    ]
    pygame.draw.polygon(surf, outline_color, left_leg)
    pygame.draw.polygon(surf, body_color, left_leg, 0)
    
    # Right leg
    right_leg = [
        (x + leg_offset * direction, y + bob),
        (x + leg_offset * direction, y + leg_height + bob),
        (x + (leg_offset - leg_width) * direction, y + leg_height + bob - leg_swing),
        (x + (leg_offset - leg_width) * direction, y + bob)
    ]
    pygame.draw.polygon(surf, outline_color, right_leg)
    pygame.draw.polygon(surf, body_color, right_leg, 0)
    
    # Body (torso)
    torso_rect = pygame.Rect(x - body_width // 2, y - body_height // 2 + bob, body_width, body_height)
    pygame.draw.rect(surf, outline_color, torso_rect.inflate(4, 4), border_radius=int(radius * 0.3))
    pygame.draw.rect(surf, body_color, torso_rect, border_radius=int(radius * 0.3))
    
    # Arms
    arm_length = radius * 1.2
    arm_width = radius * 0.3
    
    if state == 'attacking':
        # Swing arm animation
        arm_angle = facing_angle + math.pi / 4
    else:
        arm_angle = facing_angle
    
    # Arm positions
    arm_start_x = x + direction * (body_width // 2)
    arm_start_y = y - body_height // 4 + bob
    
    arm_end_x = arm_start_x + math.cos(arm_angle) * arm_length
    arm_end_y = arm_start_y + math.sin(arm_angle) * arm_length
    
    # Draw arm
    pygame.draw.line(surf, outline_color, (arm_start_x, arm_start_y), (arm_end_x, arm_end_y), int(arm_width + 2))
    pygame.draw.line(surf, body_color, (arm_start_x, arm_start_y), (arm_end_x, arm_end_y), int(arm_width))
    
    # Head
    head_y = y - body_height // 2 - head_radius + bob
    pygame.draw.circle(surf, outline_color, (x, head_y), int(head_radius + 2))
    pygame.draw.circle(surf, body_color, (x, head_y), int(head_radius))
    
    # Eyes
    eye_offset = head_radius * 0.3
    eye_radius = head_radius * 0.2
    pygame.draw.circle(surf, (255, 255, 255), (int(x - eye_offset * direction), int(head_y - eye_radius)), int(eye_radius))
    pygame.draw.circle(surf, (255, 255, 255), (int(x + eye_offset * direction), int(head_y - eye_radius)), int(eye_radius))
    pygame.draw.circle(surf, (0, 0, 0), (int(x - eye_offset * direction), int(head_y - eye_radius)), int(eye_radius * 0.6))
    pygame.draw.circle(surf, (0, 0, 0), (int(x + eye_offset * direction), int(head_y - eye_radius)), int(eye_radius * 0.6))


def draw_enemy_sprite(surf, pos, radius, enemy_type, state, animation_time=0):
    """
    Draw an enemy sprite based on type
    
    Args:
        surf: Surface to draw on
        pos: (x, y) position
        radius: Base size
        enemy_type: 'math', 'cs', 'physics', 'chemistry', 'biology', 'history'
        state: 'idle', 'windup', 'swing', 'attack'
        animation_time: Time for animations
    """
    x, y = int(pos[0]), int(pos[1])
    
    if enemy_type == 'math':
        draw_math_enemy(surf, x, y, radius, state, animation_time)
    elif enemy_type == 'cs':
        draw_cs_enemy(surf, x, y, radius, state, animation_time)
    elif enemy_type == 'physics':
        draw_physics_enemy(surf, x, y, radius, state, animation_time)
    elif enemy_type == 'chemistry':
        draw_chemistry_enemy(surf, x, y, radius, state, animation_time)
    elif enemy_type == 'biology':
        draw_biology_enemy(surf, x, y, radius, state, animation_time)
    elif enemy_type == 'history':
        draw_history_enemy(surf, x, y, radius, state, animation_time)
    else:
        # Default enemy
        draw_default_enemy(surf, x, y, radius, state, animation_time)


def draw_math_enemy(surf, x, y, radius, state, animation_time):
    """Draw a scholar/student-like enemy for math"""
    # Body color based on state
    if state == 'windup':
        color = COLORS["enemy_windup"]
    elif state == 'swing' or state == 'attack':
        color = COLORS["enemy_attack"]
    else:
        color = COLORS["enemy"]
    
    bob = math.sin(animation_time * 5) * 1.5
    
    # Shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (x - radius, y + radius, radius * 2, radius * 0.5))
    
    # Robe body (triangle-ish)
    robe_points = [
        (x, y - radius * 1.5 + bob),  # Top
        (x - radius * 1.2, y + radius + bob),  # Bottom left
        (x + radius * 1.2, y + radius + bob)   # Bottom right
    ]
    pygame.draw.polygon(surf, (80, 60, 60), robe_points)
    pygame.draw.polygon(surf, color, robe_points, 0)
    
    # Head (circular)
    head_y = y - radius * 1.2 + bob
    pygame.draw.circle(surf, (100, 80, 80), (x, int(head_y)), int(radius * 0.8))
    pygame.draw.circle(surf, color, (x, int(head_y)), int(radius * 0.7))
    
    # Book in hands
    book_rect = pygame.Rect(x - radius * 0.5, y - radius * 0.3 + bob, radius, radius * 0.6)
    pygame.draw.rect(surf, (100, 80, 50), book_rect)
    pygame.draw.rect(surf, (150, 120, 70), book_rect, 2)
    
    # Glasses
    pygame.draw.circle(surf, (200, 200, 200), (int(x - radius * 0.25), int(head_y)), int(radius * 0.2), 2)
    pygame.draw.circle(surf, (200, 200, 200), (int(x + radius * 0.25), int(head_y)), int(radius * 0.2), 2)


def draw_cs_enemy(surf, x, y, radius, state, animation_time):
    """Draw a hacker/robot-like enemy for CS"""
    if state == 'windup':
        color = COLORS["enemy_windup"]
    elif state == 'swing' or state == 'attack':
        color = COLORS["enemy_attack"]
    else:
        color = COLORS["enemy"]
    
    pulse = math.sin(animation_time * 8) * 0.1 + 0.9
    
    # Shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (x - radius, y + radius, radius * 2, radius * 0.5))
    
    # Robot body (rectangular with rounded corners)
    body_rect = pygame.Rect(x - radius * 0.8, y - radius * 0.8, radius * 1.6, radius * 1.8)
    pygame.draw.rect(surf, (60, 60, 80), body_rect, border_radius=5)
    pygame.draw.rect(surf, color, body_rect, 0, border_radius=5)
    
    # Head (square)
    head_size = radius * 0.9
    head_rect = pygame.Rect(x - head_size // 2, y - radius * 1.8, head_size, head_size)
    pygame.draw.rect(surf, (70, 70, 90), head_rect, border_radius=3)
    pygame.draw.rect(surf, color, head_rect, 0, border_radius=3)
    
    # Visor/Screen (glowing)
    visor_color = (0, int(255 * pulse), int(200 * pulse))
    visor_rect = pygame.Rect(x - head_size // 3, y - radius * 1.5, head_size * 0.6, head_size * 0.3)
    pygame.draw.rect(surf, visor_color, visor_rect)
    
    # Binary code effect
    for i in range(3):
        code_y = y - radius * 0.4 + i * (radius * 0.3)
        pygame.draw.line(surf, (0, 200, 150), (x - radius * 0.6, int(code_y)), (x + radius * 0.6, int(code_y)), 1)


def draw_physics_enemy(surf, x, y, radius, state, animation_time):
    """Draw an energy being for physics"""
    if state == 'windup':
        color = COLORS["enemy_windup"]
    elif state == 'swing' or state == 'attack':
        color = COLORS["enemy_attack"]
    else:
        color = COLORS["enemy"]
    
    pulse = math.sin(animation_time * 10) * 0.15 + 0.85
    
    # Energy core (glowing)
    core_radius = int(radius * pulse)
    glow_surf = pygame.Surface((core_radius * 3, core_radius * 3), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*color, 80), (core_radius * 1.5, core_radius * 1.5), core_radius * 1.5)
    surf.blit(glow_surf, (x - core_radius * 1.5, y - core_radius * 1.5))
    
    pygame.draw.circle(surf, (255, 255, 255), (x, y), core_radius, 2)
    pygame.draw.circle(surf, color, (x, y), core_radius)
    
    # Orbiting particles
    for i in range(4):
        angle = animation_time * 5 + i * (math.pi / 2)
        orbit_x = x + math.cos(angle) * radius * 1.5
        orbit_y = y + math.sin(angle) * radius * 1.5
        pygame.draw.circle(surf, color, (int(orbit_x), int(orbit_y)), int(radius * 0.2))


def draw_chemistry_enemy(surf, x, y, radius, state, animation_time):
    """Draw an alchemist for chemistry"""
    if state == 'windup':
        color = COLORS["enemy_windup"]
    elif state == 'swing' or state == 'attack':
        color = COLORS["enemy_attack"]
    else:
        color = COLORS["enemy"]
    
    bob = math.sin(animation_time * 5) * 1.5
    
    # Shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (x - radius, y + radius, radius * 2, radius * 0.5))
    
    # Robe (similar to math but different color scheme)
    robe_points = [
        (x, y - radius * 1.5 + bob),
        (x - radius * 1.2, y + radius + bob),
        (x + radius * 1.2, y + radius + bob)
    ]
    pygame.draw.polygon(surf, (80, 60, 80), robe_points)
    pygame.draw.polygon(surf, color, robe_points, 0)
    
    # Head with hood
    head_y = y - radius * 1.2 + bob
    pygame.draw.circle(surf, (100, 60, 100), (x, int(head_y)), int(radius * 0.8))
    pygame.draw.circle(surf, color, (x, int(head_y)), int(radius * 0.7))
    
    # Potion flask
    flask_points = [
        (x - radius * 0.2, y + bob),
        (x - radius * 0.3, y + radius * 0.5 + bob),
        (x + radius * 0.3, y + radius * 0.5 + bob),
        (x + radius * 0.2, y + bob)
    ]
    pygame.draw.polygon(surf, (100, 255, 100), flask_points)
    pygame.draw.polygon(surf, (50, 200, 50), flask_points, 2)


def draw_biology_enemy(surf, x, y, radius, state, animation_time):
    """Draw a creature for biology"""
    if state == 'windup':
        color = COLORS["enemy_windup"]
    elif state == 'swing' or state == 'attack':
        color = COLORS["enemy_attack"]
    else:
        color = COLORS["enemy"]
    
    squish = math.sin(animation_time * 8) * 0.1 + 1.0
    
    # Shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (x - radius, y + radius, radius * 2, radius * 0.5))
    
    # Blob body
    blob_rect = pygame.Rect(x - radius, y - radius * squish, radius * 2, radius * 2 * squish)
    pygame.draw.ellipse(surf, (100, 80, 100), blob_rect)
    pygame.draw.ellipse(surf, color, blob_rect, 0)
    
    # Multiple eyes
    for i, eye_x_offset in enumerate([-radius * 0.4, radius * 0.4]):
        eye_y = y - radius * 0.3 * squish
        pygame.draw.circle(surf, (255, 255, 255), (int(x + eye_x_offset), int(eye_y)), int(radius * 0.25))
        pygame.draw.circle(surf, (50, 200, 50), (int(x + eye_x_offset), int(eye_y)), int(radius * 0.15))


def draw_history_enemy(surf, x, y, radius, state, animation_time):
    """Draw a warrior for history"""
    if state == 'windup':
        color = COLORS["enemy_windup"]
    elif state == 'swing' or state == 'attack':
        color = COLORS["enemy_attack"]
    else:
        color = COLORS["enemy"]
    
    bob = math.sin(animation_time * 5) * 1.5
    
    # Shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (x - radius, y + radius, radius * 2, radius * 0.5))
    
    # Armored body
    body_rect = pygame.Rect(x - radius * 0.8, y - radius * 0.5 + bob, radius * 1.6, radius * 1.5)
    pygame.draw.rect(surf, (120, 100, 80), body_rect, border_radius=3)
    pygame.draw.rect(surf, color, body_rect, 0, border_radius=3)
    
    # Helmet
    helmet_points = [
        (x - radius * 0.7, y - radius * 1.5 + bob),
        (x - radius * 0.8, y - radius * 0.5 + bob),
        (x + radius * 0.8, y - radius * 0.5 + bob),
        (x + radius * 0.7, y - radius * 1.5 + bob)
    ]
    pygame.draw.polygon(surf, (150, 130, 100), helmet_points)
    pygame.draw.polygon(surf, color, helmet_points, 0)
    
    # Visor
    visor_rect = pygame.Rect(x - radius * 0.5, y - radius * 1.2 + bob, radius, radius * 0.3)
    pygame.draw.rect(surf, (50, 50, 50), visor_rect)
    
    # Shield
    shield_center = (int(x + radius * 1.2), int(y + bob))
    pygame.draw.circle(surf, (180, 160, 120), shield_center, int(radius * 0.8))
    pygame.draw.circle(surf, (200, 180, 140), shield_center, int(radius * 0.6))


def draw_default_enemy(surf, x, y, radius, state, animation_time):
    """Draw a default enemy shape"""
    if state == 'windup':
        color = COLORS["enemy_windup"]
    elif state == 'swing' or state == 'attack':
        color = COLORS["enemy_attack"]
    else:
        color = COLORS["enemy"]
    
    pygame.draw.circle(surf, (100, 80, 80), (x, y), radius + 2)
    pygame.draw.circle(surf, color, (x, y), radius)


def draw_slash_effect(surf, pos, angle, size, progress, color=(255, 200, 100)):
    """
    Draw an attack slash effect
    
    Args:
        surf: Surface to draw on
        pos: Center position
        angle: Angle of the slash
        size: Size of the slash
        progress: Animation progress (0.0 to 1.0)
        color: Color of the slash
    """
    if progress <= 0 or progress >= 1:
        return
    
    alpha = int(255 * (1 - progress))
    slash_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    
    # Draw arc slash
    start_angle = angle - math.pi / 4
    end_angle = angle + math.pi / 4
    
    # Create slash as a series of lines forming an arc
    steps = 10
    for i in range(steps):
        t = i / steps
        current_angle = start_angle + (end_angle - start_angle) * t
        
        start_dist = size * 0.3
        end_dist = size * (0.8 + progress * 0.5)
        
        start_x = size + math.cos(current_angle) * start_dist
        start_y = size + math.sin(current_angle) * start_dist
        end_x = size + math.cos(current_angle) * end_dist
        end_y = size + math.sin(current_angle) * end_dist
        
        line_alpha = int(alpha * (1 - t * 0.5))
        pygame.draw.line(slash_surf, (*color, line_alpha), (start_x, start_y), (end_x, end_y), 3)
    
    surf.blit(slash_surf, (int(pos[0]) - size, int(pos[1]) - size))


def draw_projectile_trail(surf, start_pos, end_pos, color, thickness=2):
    """Draw a trail behind a projectile"""
    # Draw gradient trail
    steps = 5
    for i in range(steps):
        t = i / steps
        alpha = int(150 * (1 - t))
        
        trail_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
        trail_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
        
        trail_thickness = int(thickness * (1 - t * 0.5))
        if trail_thickness > 0:
            trail_surf = pygame.Surface((trail_thickness * 2, trail_thickness * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*color, alpha), (trail_thickness, trail_thickness), trail_thickness)
            surf.blit(trail_surf, (int(trail_x) - trail_thickness, int(trail_y) - trail_thickness))
