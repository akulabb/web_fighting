import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT
import pygame as pg
from fighter import Fighter

epg.AUTO_UPDATE = False
SCREEN_HEIGHT = 970
SCREEN_WIDTH = 1280
FPS = 30
BALL_IMAGE_PATH = 'photos/ball.png'
EARTH_IMAGE_PATH = 'photos/earth.png'

HEIGHT_HALF = int(SCREEN_HEIGHT/2)
WIDTH_HALF = int(SCREEN_WIDTH/2)
epg.AUTO_UPDATE = False

GRAVITY = 2
EARTH = 716

def update():
    epg.update()
    if epg.close_window():
        exit()
    epg.tick(FPS)
    

screen = epg.Screen(EARTH_IMAGE_PATH, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
fighter1 = Fighter(x_pos=80,
                   wigth=120, 
                   height=280,
                   ground_level=EARTH,
                   gravity=GRAVITY
                   )

fighter2 = Fighter(x_pos=300,
                   wigth=120, 
                   height=280,
                   ground_level=EARTH,
                   gravity=GRAVITY
                   )


fall_speed = 0
horiz_speed = 0

fighter1.fights(fighter2)

def main():
    while True:
        fighter1.moving()
        update()
        if fighter1.knife:
            fighter1.knife.kill()
        

main()

