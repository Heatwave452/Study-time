import pygame

# Display
WIDTH = 1000
HEIGHT = 700
FPS = 60

# Colors - Enhanced modern palette
COLORS = {
    "bg": (15, 20, 35),  # Darker, richer background
    "bg_accent": (25, 35, 60),  # Accent background
    "arena": (120, 140, 200),  # Brighter arena border
    "player": (80, 180, 255),  # Vibrant cyan-blue player
    "player_glow": (100, 220, 255),  # Glow effect
    "attack": (255, 120, 200),  # Vibrant magenta attack
    "enemy": (255, 80, 80),  # Bright red enemy
    "enemy_windup": (255, 180, 100),  # Orange windup
    "enemy_attack": (255, 100, 100),  # Red attack
    "ui_hp": (120, 255, 120),  # Bright green HP
    "ui_hp_back": (40, 50, 65),  # Better contrast background
    "ui_xp": (120, 200, 255),  # Bright cyan XP
    "ui_gold": (255, 215, 0),  # Gold accent
    "door_open": (100, 255, 150),  # Bright green door
    "door_closed": (255, 100, 100),  # Red closed door
    "station": (255, 220, 100),  # Bright yellow station
    "interact": (150, 200, 255),  # Bright blue interact
    "proj": (255, 200, 100),  # Orange projectile
    "poison": (150, 255, 100),  # Bright green poison
    "history": (220, 180, 130),  # Warm history color
    "menu_accent": (80, 120, 200),  # Menu accent blue
    "menu_hover": (100, 150, 230),  # Menu hover effect
    "button_shadow": (10, 15, 25),  # Button shadow
}

# Player config
PLAYER = {
    "move_speed": 300,
    "max_hp": 100,
    "melee_damage": 12,
    "attack_cooldown": 0.35,
    "attack_range": 38,
    "i_frames": 0.12,
}

# Math Swordsman
MATH_SWORDSMAN = {
    "move_speed": 100.0,
    "max_hp": 25,
    "base_damage": 8,
    "aggro_range": 400.0,
    "attack_range": 40.0,
    "attack_cooldown": 0.8,
    "attack_windup": 0.35,
    "line_len_tick": 20.0,
}

# Math Archer
MATH_ARCHER = {
    "move_speed": 90.0,
    "max_hp": 20,
    "base_damage": 6,
    "aggro_range": 500.0,
    "keep_distance": 250.0,
    "shoot_cooldown": 1.2,
    "projectile_speed": 250.0,
    "projectile_radius": 6,
    "close_shield_trigger": 80.0,
    "close_shield_duration": 1.5,
    "close_shield_cooldown": 3.0,
}

# Exam Boss
EXAM_BOSS = {
    "max_hp": 200,
    "base_damage": 15,
    "move_speed": 110.0,
    "attack_cooldown": 1.5,
    "attack_windup": 0.35,
}

# Arena
ARENA = {
    "margin": 30,
}

# Door
DOOR = {
    "width": 60,
    "height": 20,
    "y_offset": 10,
}

# Rest Stop
REST_STOP = {
    "heal_pos": (200, 350),
    "upgrade_pos": (800, 350),
    "use_radius": 40,
    "heal_amount": 100,
    "upgrade_attack_amount": 3,
    "upgrade_speed_amount": 15,
}