import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT, BORDER
import pygame


SCREEN_HEIGHT = 970
SCREEN_WIDTH = 1280


class Fighter(epg.Sprite):
    def __init__(self, x_pos, wigth, height, ground_level, gravity):
        pos = (x_pos, ground_level - height / 2)
        super().__init__(pos=pos, w=wigth, h=height)
        self.gravity = gravity
        self.fall_speed = 0
        self.ground_level = ground_level
        self.jumping = False
        self.knife = None
        self.enemy = None
        
    def fights(self, enemy):
        self.enemy = enemy
        
    def moving(self):
    
        dx = 0
        dy = 0
        # controling
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            dx -= 10
        if keystate[pygame.K_d]:
            dx += 10
        if keystate[pygame.K_SPACE] and not self.jumping:
            self.fall_speed = -30
            self.jumping = True
        if keystate[pygame.K_e]:
            self.attack()
        
        # gravitation
        self.fall_speed += self.gravity
        dy = self.fall_speed
        
        # удержание спрайта в пределах экрана
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        elif self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right
        if self.rect.bottom + dy > self.ground_level:
            dy -= self.rect.bottom + dy - self.ground_level
            self.fall_speed = 0
            self.jumping = False
            
        
        self.move(RIGHT, dx)
        self.move(DOWN, dy)
    
    def attack(self, ):
        attack_dist = self.size[0]
        self.knife = epg.Sprite(img=epg.RED,
                                w=attack_dist,
                                h=self.size[1],
                                pos=(self.pos[0] + attack_dist / 2, self.pos[1]),
                                )
        if self.knife.taped(self.enemy):
            print('hit')
        
    