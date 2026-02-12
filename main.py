import pygame, sys, random
from config import WIDTH, HEIGHT, FPS, COLORS, ARENA
from player import Player
from systems import HUD
from map_system import MapManager
from enemy import MathSwordsman, MathArcher
from computer_science_enemies import BinaryBlade, BugSwarm
from physics_enemies import KineticBrute, GravityManipulator
from chemistry_enemies import AcidicAlchemist
from utils import vec2_from_keys

class Button:
    def __init__(self, text, pos, size, font, color_idle, color_hover):
        self.text = text
        self.pos = pos
        self.size = size
        self.font = font
        self.color_idle = color_idle
        self.color_hover = color_hover
        self.rect = pygame.Rect(pos, size)
        self.hovered = False

    def draw(self, screen):
        color = self.color_hover if self.hovered else self.color_idle
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, event_list):
        return self.rect.collidepoint(mouse_pos) and any(
            e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in event_list
        )

def handle_player_attack(player, enemies):
    hits = 0
    if not player.attacking:
        return hits
    for e in enemies:
        if not e.alive():
            continue
        if player.pos.distance_to(e.pos) <= (player.attack_range + e.radius):
            dmg = player.get_damage()
            e.take_damage(dmg)
            hits += 1
    return hits

def update_enemy_projectiles(enemies, player):
    for e in enemies:
        if hasattr(e, "projectiles"):
            for p in e.projectiles:
                if p.alive_flag:
                    p.try_hit_player(player)

def game_loop(screen, clock, selected_classes, difficulty_year):
    font = pygame.font.SysFont("arial", 18)
    hud = HUD(font)
    player = Player((WIDTH / 2, HEIGHT / 2))
    map_manager = MapManager(selected_classes, difficulty_year)
    map_manager.load_map()
    elapsed = 0.0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed += dt
        event_list = pygame.event.get()

        for event in event_list:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    player.try_attack()
                if event.key == pygame.K_LSHIFT:
                    keys = pygame.key.get_pressed()
                    dir = vec2_from_keys(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
                    if dir.length_squared() > 0:
                        player.try_dash(dir)
                    else:
                        player.try_dash(pygame.Vector2(1, 0))
                if event.key == pygame.K_c:
                    player.try_parry()
                # NEW: Ultimate ability
                if event.key == pygame.K_q:
                    player.try_ultimate()

        keys = pygame.key.get_pressed()
        current_room = map_manager.current_room
        enemies = current_room.enemies

        if player.alive():
            player.update(dt, keys)
            handle_player_attack(player, enemies)

            for e in enemies:
                if e.alive():
                    e.update(dt, player)

            update_enemy_projectiles(enemies, player)

            pressed_e = any(e.type == pygame.KEYDOWN and e.key == pygame.K_e for e in event_list)
            map_manager.update_logic(player, dt, pressed_e)

        screen.fill(COLORS["bg"])
        pygame.draw.rect(screen, COLORS["arena"],
                         (ARENA["margin"], ARENA["margin"],
                          WIDTH - 2 * ARENA["margin"], HEIGHT - 2 * ARENA["margin"]), 2)

        for e in enemies:
            if e.alive():
                e.draw(screen)

        if player.alive():
            player.draw(screen)
        else:
            text = pygame.font.SysFont("arial", 42).render(
                "You fell asleep... again.", True, (255, 180, 180)
            )
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 24))

        hud.draw(screen, player, enemies, map_manager.room_index + 1, elapsed)
        map_manager.draw_overlay(screen)

        # UPDATED: Added [Q] Ultimate to hint
        hint = font.render("[WASD] Move [Space] Attack [Shift] Dash [C] Parry [Q] Ultimate [E] Interact", True, (200, 200, 220))
        screen.blit(hint, (WIDTH - hint.get_width() - 12, HEIGHT - 28))

        pygame.display.flip()
        
        if not player.alive() or (map_manager.room_index >= len(map_manager.rooms) - 1 and current_room.cleared):
            show_end_screen(screen, clock, player.alive() and current_room.cleared, elapsed, player.max_combo)
            return True
    
    return True

def show_end_screen(screen, clock, won, elapsed_time, max_combo):
    font_title = pygame.font.SysFont("arial", 48, bold=True)
    font_sub = pygame.font.SysFont("arial", 24)
    font_stats = pygame.font.SysFont("arial", 20)
    
    waiting = True
    while waiting:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                waiting = False
        
        screen.fill(COLORS["bg"])
        
        if won:
            title = font_title.render("YOU WOKE UP!", True, (100, 255, 100))
            subtitle = font_sub.render(f"Victory!", True, (200, 255, 200))
            stats = font_stats.render(f"Time: {int(elapsed_time)}s  |  Max Combo: {max_combo}", True, (200, 255, 200))
        else:
            title = font_title.render("GAME OVER", True, (255, 100, 100))
            subtitle = font_sub.render("You fell asleep...", True, (255, 200, 200))
            stats = font_stats.render(f"Time survived: {int(elapsed_time)}s  |  Max Combo: {max_combo}", True, (255, 200, 200))
        
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        stats_rect = stats.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        
        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)
        screen.blit(stats, stats_rect)
        
        pygame.display.flip()

def class_selection_screen(screen, clock, font_small, font_button):
    all_classes = ["Math", "Computer Science", "Physics", "Chemistry", "Biology", "History"]
    years = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
    selected_classes = []
    selected_year = "Freshman"
    
    selecting = True
    while selecting:
        dt = clock.tick(FPS) / 1000.0
        event_list = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in event_list:
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                selecting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, cls in enumerate(all_classes):
                    x = 50 + (i % 3) * 310
                    y = 120 + (i // 3) * 85
                    rect = pygame.Rect(x, y, 280, 65)
                    if rect.collidepoint(mouse_pos):
                        if cls in selected_classes:
                            selected_classes.remove(cls)
                        elif len(selected_classes) < 4:
                            selected_classes.append(cls)
                
                for i, year in enumerate(years):
                    x = 150 + i * 120
                    y = 380
                    rect = pygame.Rect(x, y, 100, 50)
                    if rect.collidepoint(mouse_pos):
                        selected_year = year
                
                start_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT - 80, 240, 60)
                if start_rect.collidepoint(mouse_pos) and len(selected_classes) >= 2:
                    selecting = False
        
        screen.fill(COLORS["bg"])
        
        title = font_button.render("Select Classes & Difficulty", True, (255, 200, 100))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        class_label = font_small.render("Available Classes:", True, (200, 200, 200))
        screen.blit(class_label, (50, 90))
        
        for i, cls in enumerate(all_classes):
            x = 50 + (i % 3) * 310
            y = 120 + (i // 3) * 85
            is_selected = cls in selected_classes
            color = (100, 170, 230) if is_selected else (70, 130, 180)
            rect = pygame.Rect(x, y, 280, 65)
            pygame.draw.rect(screen, color, rect, border_radius=6)
            text = font_small.render(cls, True, (255, 255, 255))
            screen.blit(text, (rect.centerx - text.get_width()/2, rect.centery - text.get_height()/2))
        
        difficulty_label = font_small.render("Difficulty:", True, (200, 200, 200))
        screen.blit(difficulty_label, (50, 350))
        
        for i, year in enumerate(years):
            x = 150 + i * 120
            y = 380
            is_selected = year == selected_year
            color = (100, 170, 230) if is_selected else (70, 130, 180)
            rect = pygame.Rect(x, y, 100, 50)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            text = font_small.render(year[:6], True, (255, 255, 255))
            screen.blit(text, (rect.centerx - text.get_width()/2, rect.centery - text.get_height()/2))
        
        start_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT - 80, 240, 60)
        can_start = len(selected_classes) >= 2
        color = (100, 200, 100) if can_start else (100, 100, 100)
        pygame.draw.rect(screen, color, start_rect, border_radius=6)
        text = font_button.render("START" if can_start else "Need 2+ Classes", True, (255, 255, 255))
        screen.blit(text, (start_rect.centerx - text.get_width()/2, start_rect.centery - text.get_height()/2))
        
        info = font_small.render(f"Selected: {', '.join(selected_classes) if selected_classes else 'None'}", 
                               True, (200, 200, 200))
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 150))
        
        pygame.display.flip()
    
    return selected_classes if len(selected_classes) >= 2 else None, selected_year

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Study Time — College Dream RPG")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("arial", 54, bold=True)
    font_small = pygame.font.SysFont("arial", 28)
    font_tiny = pygame.font.SysFont("arial", 16)

    play_btn = Button("PLAY", (WIDTH // 2 - 100, HEIGHT // 2 - 40), (200, 60),
                      font_small, (70, 130, 180), (100, 170, 230))
    quit_btn = Button("QUIT", (WIDTH // 2 - 100, HEIGHT // 2 + 40), (200, 60),
                      font_small, (180, 70, 70), (230, 100, 100))

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        event_list = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        for event in event_list:
            if event.type == pygame.QUIT:
                running = False

        play_btn.is_hovered(mouse_pos)
        quit_btn.is_hovered(mouse_pos)

        if play_btn.is_clicked(mouse_pos, event_list):
            selected_classes, selected_year = class_selection_screen(screen, clock, font_tiny, font_small)
            if selected_classes:
                result = game_loop(screen, clock, selected_classes, selected_year)
                if not result:
                    running = False
        
        if quit_btn.is_clicked(mouse_pos, event_list):
            running = False

        screen.fill((25, 25, 35))
        title = font_big.render("Study Time", True, (255, 255, 255))
        subtitle = font_tiny.render("A College Student's Final Exam Dream", True, (200, 200, 200))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 - 80))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 3 - 20))
        play_btn.draw(screen)
        quit_btn.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()