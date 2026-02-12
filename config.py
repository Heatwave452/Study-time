import pygame

# Display
WIDTH = 1000
HEIGHT = 700
FPS = 60

# Colors
COLORS = {
    "bg": (20, 20, 30),
    "arena": (100, 100, 150),
    "player": (100, 200, 255),
    "attack": (200, 100, 255),
    "enemy": (200, 100, 100),
    "enemy_windup": (255, 150, 100),
    "enemy_attack": (255, 100, 100),
    "ui_hp": (100, 200, 100),
    "ui_hp_back": (50, 50, 60),
    "door_open": (100, 255, 100),
    "door_closed": (200, 100, 100),
    "station": (200, 200, 100),
    "interact": (200, 200, 255),
    "proj": (255, 200, 100),
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