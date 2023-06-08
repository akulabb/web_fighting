import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT, BORDER
import pygame


SCREEN_HEIGHT = 970
SCREEN_WIDTH = 1280
RIGHT = False
LEFT = True


class Fighter(epg.Sprite):
    def __init__(self, x_pos, flip, wigth, height, ground_level, gravity, id, img=epg.GREEN):
        pos = (x_pos, ground_level - height / 2)
        super().__init__(pos=pos, w=wigth, h=height, img=img)
        self.gravity = gravity
        self.fall_speed = 0
        self.ground_level = ground_level
        self.skins_dir = flip
        self.jumping = False
        self.knife = None
        self.enemy = None
        self.id = id
        self.health_bar = HealthBar(id=self.id, health=100)
        
    def fights(self, enemy):
        self.enemy = enemy
        
    def moving(self):
    
        dx = 0
        dy = 0
        # controling
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            dx -= 10
            self.flip_skins(LEFT)
        if keystate[pygame.K_d]:
            dx += 10
            self.flip_skins(RIGHT)
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
            
        pos_x = self.pos[0] + dx
        pos_y = self.pos[1] + dy
        #self.move(RIGHT, dx)
        #self.move(DOWN, dy)
        self.move_to((pos_x, pos_y))
    
    def attack(self, ):
        attack_dist = self.size[0]
        if self.skins_dir:
            hit_x = self.pos[0] - attack_dist / 2
        else:
            hit_x = self.pos[0] + attack_dist / 2
        
        knife = epg.Sprite(img=epg.RED,
                                w=attack_dist,
                                h=self.size[1],
                                pos=(hit_x, self.pos[1]),
                                )
        if knife.taped(self.enemy):
            self.enemy.update_health(-5)
        epg.update()
        knife.kill()
        
    def flip_skins(self, flipped):
        if self.skins_dir is not flipped:
            self.flip(orig=False, x=True)
            self.skins_dir = flipped
    
    
    def update_health(self, health):
        self.health_bar.set_value(self.health_bar.value + health)


class HealthBar(epg.Label):
    WIDTH = 400
    HEIGHT = 40
    def __init__(self, id, health=100):
        POSITIONS = ((10, 10), (epg.WIDTH - 10 - self.WIDTH, 10))
        x, y = POSITIONS[id]
        super().__init__(text=id, x=x, y=y, val=health)
        
    
    def _get_surf(self, ):
        raito = self.WIDTH/100
        surface = pygame.Surface((self.WIDTH+4, self.HEIGHT+4))
        pygame.draw.rect(surface, epg.BLACK, (0, 0, self.WIDTH, self.HEIGHT))
        pygame.draw.rect(surface, epg.RED, (2, 2, self.WIDTH, self.HEIGHT))
        pygame.draw.rect(surface, epg.YELLOW, (2, 2, self.value * raito, self.HEIGHT))
        return surface