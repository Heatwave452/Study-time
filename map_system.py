import pygame, random
from enemy import MathSwordsman, MathArcher, ExamBoss
from computer_science_enemies import BinaryBlade, BugSwarm
from physics_enemies import KineticBrute, GravityManipulator
from chemistry_enemies import AcidicAlchemist
from biology_enemies import PoisonMite, BioEngineer
from history_enemies import AncientWarrior, ArtilleryCommander
from config import WIDTH, HEIGHT, ARENA, DOOR, REST_STOP, COLORS

class Room:
    def __init__(self, id, enemies=None, room_type="hall", description="", class_type="math", difficulty_mult=1.0):
        self.id = id
        self.room_type = room_type
        self.description = description
        self.class_type = class_type
        self.difficulty_mult = difficulty_mult
        self.cleared = False
        self.enemies = []

        door_w = DOOR["width"]
        door_h = DOOR["height"]
        x = WIDTH // 2 - door_w // 2
        y = ARENA["margin"] - DOOR["y_offset"]
        self.door_rect = pygame.Rect(x, y, door_w, door_h)
        self.door_open = False

        self.used_heal = False
        self.used_upgrade = False

    def spawn_enemies(self):
        """Spawn enemies for this room"""
        if self.cleared:
            return
        
        if len(self.enemies) > 0:
            return

        if self.room_type == "hall":
            n = random.randint(2, 4)  # Increased variety
            for i in range(n):
                self._spawn_class_enemy()
        
        elif self.room_type == "classroom":
            n = random.randint(4, 6)  # More enemies for harder rooms
            for i in range(n):
                self._spawn_class_enemy()
        
        elif self.room_type == "boss":
            # Spawn boss with some minions
            self.enemies.append(self._spawn_boss())
            # Add 2 minions
            for _ in range(2):
                self._spawn_class_enemy()
        
        elif self.room_type == "shop":
            # Rest stop has no enemies - mark as cleared immediately
            self.cleared = True
            self.door_open = True

    def _spawn_class_enemy(self):
        """Spawn enemy based on class type"""
        x = random.randint(ARENA["margin"]+80, WIDTH-ARENA["margin"]-80)
        y = random.randint(ARENA["margin"]+80, HEIGHT-ARENA["margin"]-80)
        
        enemy = None
        
        if self.class_type == "math":
            if random.random() < 0.4:
                enemy = MathArcher((x, y))
            else:
                enemy = MathSwordsman((x, y))
        
        elif self.class_type == "computer science":
            if random.random() < 0.5:
                enemy = BugSwarm((x, y))
            else:
                enemy = BinaryBlade((x, y))
        
        elif self.class_type == "physics":
            if random.random() < 0.4:
                enemy = GravityManipulator((x, y))
            else:
                enemy = KineticBrute((x, y))
        
        elif self.class_type == "chemistry":
            enemy = AcidicAlchemist((x, y))
        
        elif self.class_type == "biology":
            if random.random() < 0.4:
                enemy = BioEngineer((x, y))
            else:
                enemy = PoisonMite((x, y))
        
        elif self.class_type == "history":
            if random.random() < 0.5:
                enemy = ArtilleryCommander((x, y))
            else:
                enemy = AncientWarrior((x, y))
        
        else:
            # Fallback for unimplemented classes
            if random.random() < 0.4:
                enemy = MathArcher((x, y))
            else:
                enemy = MathSwordsman((x, y))
        
        # Apply difficulty multiplier to enemy stats
        if enemy and self.difficulty_mult != 1.0:
            enemy.max_hp = int(enemy.max_hp * self.difficulty_mult)
            enemy.hp = float(enemy.max_hp)
            enemy.base_damage = int(enemy.base_damage * self.difficulty_mult)
        
        self.enemies.append(enemy)

    def _spawn_boss(self):
        """Spawn boss with difficulty scaling"""
        boss = ExamBoss((WIDTH/2, HEIGHT/2 - 40))
        # Apply difficulty multiplier to boss stats
        if self.difficulty_mult != 1.0:
            boss.max_hp = int(boss.max_hp * self.difficulty_mult)
            boss.hp = float(boss.max_hp)
            boss.base_damage = int(boss.base_damage * self.difficulty_mult)
        return boss

    def check_cleared(self):
        if len(self.enemies) == 0:
            if self.room_type == "shop":
                # Shop is always cleared (no enemies)
                self.cleared = True
                self.door_open = True
                return True
            return False
        if all((not e.alive()) for e in self.enemies):
            self.cleared = True
            self.door_open = True
            return True
        return False


class MapManager:
    def __init__(self, selected_classes=None, difficulty_year="Freshman"):
        self.selected_classes = selected_classes or ["Math", "Computer Science"]
        self.difficulty_year = difficulty_year
        self.rooms = []
        self.current_room = None
        self.room_index = 0
        self.font = pygame.font.SysFont("arial", 22)
        self.difficulty_multiplier = self._get_difficulty_multiplier()

    def _get_difficulty_multiplier(self):
        multipliers = {
            "Freshman": 1.0,
            "Sophomore": 1.2,
            "Junior": 1.4,
            "Senior": 1.6,
            "Graduate": 2.0
        }
        return multipliers.get(self.difficulty_year, 1.0)

    def load_map(self):
        """Generate 10-floor dungeon"""
        class_map = {
            "Math": "math",
            "Computer Science": "computer science",
            "Physics": "physics",
            "Chemistry": "chemistry",
            "Biology": "biology",
            "History": "history",
        }
        
        # Filter to only implemented classes
        valid_classes = [c for c in self.selected_classes if c in class_map]
        if not valid_classes:
            valid_classes = ["Math", "Computer Science"]
        self.selected_classes = valid_classes
        
        room_count = 0
        
        # FLOORS 1-4: Early waves (2 waves per class)
        for class_name in self.selected_classes:
            class_key = class_map.get(class_name, "math")
            for wave in range(1, 3):
                room_id = f"Floor {room_count + 1}: {class_name} Wave {wave}"
                room = Room(room_id, None, "hall", f"{class_name} wave {wave}", class_key, self.difficulty_multiplier)
                self.rooms.append(room)
                room_count += 1
        
        # FLOOR 5: Mini-bosses (1 per class)
        for class_name in self.selected_classes:
            class_key = class_map.get(class_name, "math")
            room_id = f"Floor {room_count + 1}: {class_name} Mini-Boss"
            room = Room(room_id, None, "boss", f"{class_name} mini-boss", class_key, self.difficulty_multiplier)
            self.rooms.append(room)
            room_count += 1
        
        # FLOOR 6: Rest Stop
        rest_stop_room = Room(f"Floor {room_count + 1}: Rest Stop", None, "shop", 
                             "Midterm break - heal and upgrade", "math", self.difficulty_multiplier)
        self.rooms.append(rest_stop_room)
        room_count += 1
        
        # FLOORS 7-9: Hard waves (2 waves per class)
        for class_name in self.selected_classes:
            class_key = class_map.get(class_name, "math")
            for wave in range(1, 3):
                room_id = f"Floor {room_count + 1}: {class_name} Hard Wave {wave}"
                # Apply additional 1.5x multiplier to hard floors
                hard_mult = self.difficulty_multiplier * 1.5
                room = Room(room_id, None, "classroom", f"Advanced {class_name} wave", class_key, hard_mult)
                self.rooms.append(room)
                room_count += 1
        
        # FLOOR 10: Final Boss
        final_class = self.selected_classes[0]
        class_key = class_map.get(final_class, "math")
        room_id = f"Floor {room_count + 1}: FINAL EXAM"
        # Apply 2x multiplier to final boss
        boss_mult = self.difficulty_multiplier * 2.0
        final_room = Room(room_id, None, "boss", "The ultimate test", class_key, boss_mult)
        self.rooms.append(final_room)
        
        self.current_room = self.rooms[0]
        self.current_room.spawn_enemies()

    def next_room(self, player):
        self.room_index += 1
        if self.room_index >= len(self.rooms):
            self.room_index = len(self.rooms) - 1
        self.current_room = self.rooms[self.room_index]
        self.current_room.spawn_enemies()
        player.pos.x = WIDTH / 2
        player.pos.y = HEIGHT - 100

    def update_logic(self, player, dt, player_pressed_e):
        room = self.current_room
        room.check_cleared()

        if room.room_type == "shop":
            hx, hy = REST_STOP["heal_pos"]
            ux, uy = REST_STOP["upgrade_pos"]
            use_r = REST_STOP["use_radius"]

            if (player.pos.distance_to((hx, hy)) <= use_r) and player_pressed_e and not room.used_heal:
                room.used_heal = True
                player.hp = player.max_hp

            if (player.pos.distance_to((ux, uy)) <= use_r) and player_pressed_e and not room.used_upgrade:
                room.used_upgrade = True
                player.melee_damage += REST_STOP["upgrade_attack_amount"]
                player.speed += REST_STOP["upgrade_speed_amount"]

        if room.door_open:
            if room.door_rect.collidepoint(int(player.pos.x), int(player.pos.y - player.radius)):
                self.next_room(player)

    def draw_overlay(self, screen):
        room = self.current_room
        name = self.font.render(room.id, True, (220, 220, 240))
        screen.blit(name, (WIDTH // 2 - name.get_width() // 2, 8))

        door_color = COLORS["door_open"] if room.door_open else COLORS["door_closed"]
        pygame.draw.rect(screen, door_color, room.door_rect)

        if room.room_type == "shop":
            hx, hy = REST_STOP["heal_pos"]
            ux, uy = REST_STOP["upgrade_pos"]
            pygame.draw.circle(screen, COLORS["station"], (int(hx), int(hy)), 16)
            pygame.draw.circle(screen, COLORS["station"], (int(ux), int(uy)), 16)
            hint = self.font.render("Rest Stop: [E] to Heal or Upgrade", True, COLORS["interact"])
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 36))
            
            if self.current_room.used_heal:
                used = self.font.render("Heal used", True, (200, 160, 160))
                screen.blit(used, (hx - used.get_width() // 2, hy - 40))
            if self.current_room.used_upgrade:
                used2 = self.font.render("Upgrade used", True, (200, 160, 160))
                screen.blit(used2, (ux - used2.get_width() // 2, uy - 40))