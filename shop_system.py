import pygame
from config import WIDTH, HEIGHT, COLORS

class RestStopMenu:
    def __init__(self, player, font):
        self.player = player
        self.font = font
        self.active = True
        self.buttons = []
        self.setup_buttons()

    def setup_buttons(self):
        self.buttons = [
            {"text": "Heal (free)", "rect": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50), "action": "heal"},
            {"text": "Upgrade Attack", "rect": pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 50), "action": "attack"},
            {"text": "Upgrade Speed", "rect": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50), "action": "speed"},
            {"text": "Continue", "rect": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 160, 200, 50), "action": "exit"}
        ]

    def draw(self, screen):
        # Dim background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))

        title = self.font.render("Rest Stop - Take a Break", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 60))

        for btn in self.buttons:
            rect = btn["rect"]
            pygame.draw.rect(screen, (70, 130, 180), rect, border_radius=8)
            txt = self.font.render(btn["text"], True, (255, 255, 255))
            screen.blit(txt, (rect.centerx - txt.get_width()/2, rect.centery - txt.get_height()/2))

    def handle_click(self, event_list):
        for e in event_list:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = pygame.mouse.get_pos()
                for btn in self.buttons:
                    if btn["rect"].collidepoint((mx, my)):
                        return btn["action"]
        return None

    def process_action(self, action):
        if action == "heal":
            self.player.hp = self.player.max_hp
        elif action == "attack":
            self.player.melee_damage += 3
        elif action == "speed":
            self.player.speed += 15
        elif action == "exit":
            self.active = False