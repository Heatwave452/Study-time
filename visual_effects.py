import pygame
import random


class DamageNumber:
    """Floating damage number that appears when hitting enemies"""
    def __init__(self, pos, damage, is_crit=False):
        self.pos = pygame.Vector2(pos)
        self.damage = damage
        self.is_crit = is_crit
        self.lifetime = 1.0
        self.velocity = pygame.Vector2(
            random.uniform(-20, 20),
            random.uniform(-80, -40)
        )
        self.font = pygame.font.SysFont("arial", 20 if is_crit else 16, bold=True)
        self.alive = True
    
    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        
        self.pos += self.velocity * dt
        # Slow down
        self.velocity.y += 100 * dt
    
    def draw(self, surf):
        if not self.alive:
            return
        
        alpha = int(255 * min(1.0, self.lifetime / 1.0))
        color = (255, 100, 100) if self.is_crit else (255, 200, 100)
        text = f"-{self.damage}" + (" CRIT!" if self.is_crit else "")
        
        damage_surf = self.font.render(text, True, color)
        damage_surf.set_alpha(alpha)
        surf.blit(damage_surf, (int(self.pos.x) - damage_surf.get_width()//2, 
                                int(self.pos.y)))


class HitParticle:
    """Small particle effect when hitting enemies"""
    def __init__(self, pos, color=(255, 200, 100)):
        self.pos = pygame.Vector2(pos)
        angle = random.uniform(0, 6.28)
        speed = random.uniform(50, 150)
        self.velocity = pygame.Vector2(
            speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x,
            speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
        )
        self.lifetime = 0.5
        self.color = color
        self.size = random.randint(2, 4)
        self.alive = True
    
    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        
        self.pos += self.velocity * dt
        # Slow down
        self.velocity *= 0.95
    
    def draw(self, surf):
        if not self.alive:
            return
        
        alpha = int(255 * (self.lifetime / 0.5))
        color_with_alpha = (*self.color[:3], alpha)
        
        # Draw as circle
        pygame.draw.circle(surf, self.color, 
                          (int(self.pos.x), int(self.pos.y)), self.size)


class LevelUpEffect:
    """Visual effect for level up"""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.particles = []
        self.lifetime = 2.0
        
        # Create particles in a circle
        for i in range(20):
            angle = (i / 20) * 6.28
            speed = 100
            velocity = pygame.Vector2(
                speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x,
                speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            )
            self.particles.append({
                'pos': pygame.Vector2(pos),
                'vel': velocity,
                'lifetime': 1.5
            })
        
        self.alive = True
    
    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        
        for p in self.particles:
            p['lifetime'] -= dt
            if p['lifetime'] > 0:
                p['pos'] += p['vel'] * dt
                p['vel'] *= 0.96
    
    def draw(self, surf):
        if not self.alive:
            return
        
        for p in self.particles:
            if p['lifetime'] > 0:
                alpha = int(255 * (p['lifetime'] / 1.5))
                size = int(4 * (p['lifetime'] / 1.5))
                pygame.draw.circle(surf, (255, 215, 0), 
                                  (int(p['pos'].x), int(p['pos'].y)), size)
