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
        self.speed = 10
        
    def fights(self, enemy):
        self.enemy = enemy
        
    def get_game_state(self, options):
    
        dx = 0
        dy = 0
        # controling
        if options.get('jump') == True and not self.jumping:
            self.fall_speed = -30
            self.jumping = True
        if options.get('hit') == True:
            self.attack()
#        options.get('jump') == True
        dx += options.get('move')
        self.flip_skins(options.get('direction'))
        #print(options.get('direction'))
        
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
        return {'coords' : (pos_x, pos_y),
                'health' : self.health_bar.value,
                }
            

    
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
            #print(903)
            self.flip(orig=False, x=True)
            self.skins_dir = flipped
    
    
    def update_health(self, health):
        self.health_bar.set_value(self.health_bar.value + health)
        
        
    
    def check_options(self, ):
        options = {'move' : 0,
                   'direction' : self.skins_dir,
                   'jump' : False,
                   'hit' : False,
                    }
                    
        keystate = pygame.key.get_pressed()
                    
        if keystate[pygame.K_a]:
            options['direction'] = LEFT
            options['move'] = -self.speed
        if keystate[pygame.K_d]:
            options['direction'] = RIGHT
            options['move'] = self.speed
        if keystate[pygame.K_SPACE]:
            options['jump'] = True
        if keystate[pygame.K_e]:
            options['hit'] = True
#        print(options)
        return options
    
    def moving(self, game_state):
        #print(game_state.get('coords'))
        self.move_to(game_state.get('coords'))
        self.health_bar.set_value(game_state.get('health'))


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
        
                          