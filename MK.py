import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT
import pygame as pg
from fighter import Fighter
import connection

epg.AUTO_UPDATE = False
SCREEN_HEIGHT = epg.HEIGHT = 970
SCREEN_WIDTH = epg.WIDTH = 1280
FPS = 30
BALL_IMAGE_PATH = 'photos/ball.png'
EARTH_IMAGE_PATH = 'photos/earth.png'

HEIGHT_HALF = int(SCREEN_HEIGHT/2)
WIDTH_HALF = int(SCREEN_WIDTH/2)
epg.AUTO_UPDATE = False

GRAVITY = 2
#EARTH = 716

FIGHTER_IMAGE_PATH = 'C:\\Users\\Akula\\Desktop\\pytho\\Pygame\\wed_fighting\\photos\\fighter.png'

SERVER = 'localhost'
PORT = 5555

def update():
    epg.update()
    if epg.close_window():
        exit()
    epg.tick(FPS)
    

screen = epg.Screen(EARTH_IMAGE_PATH, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

server = connection.Conection(SERVER, PORT)

x_pos, y_pos, player_wigth, player_height = server.get_start()

#print(x_pos, ground_level)

ground_level = SCREEN_HEIGHT - 254

fighter1 = Fighter(img=FIGHTER_IMAGE_PATH,
                   x_pos=x_pos,
                   y_pos=y_pos,
                   flip = False,
                   wigth=player_wigth, 
                   height=player_height,
                   ground_level=ground_level,
                   gravity=GRAVITY,
                   id=0
                   )

fighter2 = Fighter(x_pos=300,
                   y_pos=y_pos,
                   flip = True,
                   wigth=player_wigth, 
                   height=player_height,
                   ground_level=ground_level,
                   gravity=GRAVITY,
                   id=1
                   )





fall_speed = 0
horiz_speed = 0

fighter1.fights(fighter2)


def main():
    while fighter1.health_bar.value > 0 and fighter2.health_bar.value > 0:
        options = fighter1.check_options()
        game_state = fighter1.get_game_state(options)
        server.send(options)
        fighter1.moving(game_state)
        update()
        

        

main()

