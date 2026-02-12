import pygame
from config import COLORS, WIDTH
from utils import draw_text

class HUD:
    def __init__(self, font):
        self.font = font

    def draw(self, surf, player, enemies, wave, elapsed):
        maxw = 240
        hpw = int(maxw * (player.hp / player.max_hp))
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (16, 16, maxw, 18), border_radius=6)
        pygame.draw.rect(surf, COLORS["ui_hp"], (16, 16, hpw, 18), border_radius=6)
        draw_text(surf, f"HP: {int(player.hp)}/{player.max_hp}", (20, 18), self.font, (240, 240, 255))
        
        # Level and XP bar
        draw_text(surf, f"Level: {player.level}", (16, 44), self.font, (255, 215, 0))
        xp_bar_w = 240
        xp_w = int(xp_bar_w * (player.xp / player.xp_to_next_level))
        pygame.draw.rect(surf, COLORS["ui_hp_back"], (16, 65, xp_bar_w, 12), border_radius=4)
        pygame.draw.rect(surf, (100, 200, 255), (16, 65, xp_w, 12), border_radius=4)
        draw_text(surf, f"XP: {player.xp}/{player.xp_to_next_level}", (20, 65), self.font, (240, 240, 255))
        
        alive_enemies = len([e for e in enemies if e.alive()])
        draw_text(surf, f"Enemies: {alive_enemies}", (16, 86), self.font, (200, 200, 220))
        draw_text(surf, f"Floor: {wave}", (16, 110), self.font, (200, 200, 220))
        draw_text(surf, f"Kills: {player.total_kills} | Score: {player.score}", (16, 134), self.font, (200, 200, 220))
        
        # Combo display with max combo tracker
        if player.combo_count > 1:
            combo_text = f"COMBO x{player.combo_count} (MAX: {player.max_combo})"
            draw_text(surf, combo_text, (WIDTH//2 - 100, 20), self.font, (255, 255, 100))
        
        # Level up notification
        if player.level_up_timer > 0:
            level_up_text = f"LEVEL UP! Now Level {player.level}!"
            level_up_surf = pygame.font.SysFont("arial", 32, bold=True).render(level_up_text, True, (255, 215, 0))
            alpha = int(255 * min(1.0, player.level_up_timer / 2.0))
            level_up_surf.set_alpha(alpha)
            surf.blit(level_up_surf, (WIDTH//2 - level_up_surf.get_width()//2, HEIGHT//3))
        
        # Ability cooldowns with labels
        dash_status = "READY ✓" if player._dash_timer == 0 else f"{player._dash_timer:.1f}s"
        parry_status = "READY ✓" if player._parry_timer == 0 else f"{player._parry_timer:.1f}s"
        
        draw_text(surf, f"[Shift] Dash: {dash_status}", (16, 158), self.font, (150, 200, 255))
        draw_text(surf, f"[C] Parry: {parry_status}", (16, 182), self.font, (255, 180, 100))
        
        # NEW: Ultimate charge display
        ultimate_pct = int((player.ultimate_charge / player.ultimate_max_charge) * 100)
        ultimate_color = (255, 100, 100) if ultimate_pct == 100 else (255, 200, 100)
        draw_text(surf, f"[Q] Ultimate: {ultimate_pct}%", (16, 206), self.font, ultimate_color)
        
        # NEW: Berserk indicator
        if player.berserk_active:
            berserk_text = f"BERSERK MODE! {player._berserk_timer:.1f}s"
            draw_text(surf, berserk_text, (WIDTH//2 - 80, 50), self.font, (255, 50, 50))
        
        # Buff indicators
        y_offset = 230
        if player.damage_buff > 1.0:
            draw_text(surf, f"DMG BUFF: +{int((player.damage_buff-1)*100)}%", (16, y_offset), self.font, (255, 150, 150))
            y_offset += 24
        if player.speed_buff > 1.0:
            draw_text(surf, f"SPD BUFF: +{int((player.speed_buff-1)*100)}%", (16, y_offset), self.font, (150, 255, 150))
            y_offset += 24
        
        # Debuff indicators
        if player.poison_timer > 0:
            draw_text(surf, f"POISONED: {player.poison_timer:.1f}s", (16, y_offset), self.font, (100, 255, 100))
            y_offset += 24