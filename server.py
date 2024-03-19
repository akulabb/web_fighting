import socket
import threading
import time
import json


SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
GROUND_LEVEL = SCREEN_HEIGHT - 254              #716
START_POSITIONS = (int(SCREEN_WIDTH / 5), 
                   int(SCREEN_WIDTH - SCREEN_WIDTH / 5),
                   int(SCREEN_WIDTH / 5 * 2),
                   int(SCREEN_WIDTH / 5 * 3)
                   )

SERVER = 'localhost'
PORT = 5555

ATTACK_DELAY = 40

PLAYER_SIZE = (280, 180)

GRAVITY = 2

start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start_socket.bind((SERVER, PORT))
start_socket.listen(2)
print('Сервер запущен')

players = {0 : None,
		   1 : None,
		   2 : None,
		   3 : None,
		   }

active_players_num = 0

class Player:
    def __init__(self, id, socket, gravity):
        self.action_delay = 0
        self.action = 0     # 0 = stay, 1 = go, 2 = jump, 3 = attack, 4 hitted, 5 = dead
        self.id = id
        self.dir = self.id % 2 or False            # True влево, False вправо
        self.health = 100
        self.y_pos = int(GROUND_LEVEL - PLAYER_SIZE[1] / 2)
        self.rect = Rect(PLAYER_SIZE, 
                         START_POSITIONS[self.id], 
                         self.y_pos
                         )
        self.socket = socket
        self.fall_speed = 0
        self.jumping = False
        self.gravity = gravity
    
    def attack(self,):
        self.action = 3
        self.action_delay = ATTACK_DELAY
        attack_dist = self.rect.width
        if self.dir:
            hit_x = self.rect.center_x - attack_dist / 2
        else:
            hit_x = self.rect.center_x + attack_dist / 2
        
        hit = Rect(PLAYER_SIZE,
                     hit_x,
                     self.y_pos,
                     )
        
        print('starting apply hitted')
        for hitted_enemy in hit.get_hitted(self.id): 
            hitted_enemy.hitted()
            print('attack:enemy id', hitted_enemy.id)
    
    def hitted(self):
        self.health -= 5
        print('hitted:health', self.health)
    
    def apply_options(self, options):
        dx = 0
        dy = 0
        # controling
        if options.get('jump') and not self.jumping:
            self.fall_speed = -30
            self.jumping = True
        if options.get('hit') and not self.action_delay:
            print('call attack')
            self.attack()
        dx += options.get('move')
       # print('controling: dx=', dx, 'dy=', dy)
        #print(options.get('direction'))
        
        # gravitation
    #    elif self.rect.bottom < GROUND_LEVEL:
        self.fall_speed += self.gravity
        dy = self.fall_speed
    #    print('gravitation: dx=', dx, 'dy=', dy)
        
        # удержание спрайта в пределах экрана
        if (self.rect.left + dx) < 0:       #левая граница экрана
            dx = -self.rect.left
         #   print('left range: dx=', dx)
        elif self.rect.right + dx > SCREEN_WIDTH:   #правая граница
            dx = SCREEN_WIDTH - self.rect.right
        #    print('right range: dx=', dx)
        if (self.rect.bottom + dy) > GROUND_LEVEL:
            dy = (GROUND_LEVEL - self.rect.bottom)
            self.fall_speed = 0
            self.jumping = False
       #     print('self.rect.bottom = ', self.rect.bottom)
      #      print('ground_range: dy=', dy)
        
     #   print('frame range: dx=', dx, 'dy=', dy)
        pos_x = self.rect.center_x + dx
        pos_y = self.rect.center_y + dy
        if self.action_delay:
            self.action_delay -= 1
        self.rect.update(pos_x, pos_y)
        
    def get_self_state(self):
        return (self.rect.center_x, self.rect.center_y, self.health, self.action, )
    

class Rect:
    def __init__(self, size, center_x, center_y, ):
        self.width, self.height = size
        self.center_x = center_x
        self.center_y = center_y
        self.update(center_x, center_y)
    
    def update(self, center_x, center_y):
        self.top = int(center_y - self.height / 2)
        self.bottom = int(center_y + self.height / 2)
        self.right = int(center_x + self.width / 2)
        self.left = int(center_x - self.width / 2)
        self.center_x = center_x
        self.center_y = center_y    
    
    def get_hitted(self, my_player_id):
        enemies = []
        for id, player in players.items():
            if player and not id == my_player_id:
                if (player.rect.right >= self.left and
                        player.rect.left <= self.right and
                        player.rect.top <= self.bottom and
                        player.rect.bottom >= self.top):
                    print('enemys append')
                    enemies.append(player)
        return enemies
        

def remove_player(id):
	players[id].socket.close()
	players[id] = None
	print('игрок закончился с id : ', id)


def threaded_player(current_player):
    print('Игрок создан с id : ', current_player.id)
    start_state = {'current_player_id' : current_player.id}
    global active_players_num
    while active_players_num < 2:
        print(active_players_num, 'кол-во игроков')
        time.sleep(1)
    for id, player in players.items():
        if player:
            start_state[id] = (player.dir,
                               player.rect.center_x, 
                               player.rect.center_y, 
                               player.rect.width,
                               player.rect.height,
                               )
    str_start_state = json.dumps(start_state)
    current_player.socket.send(str_start_state.encode())
    print('player', current_player.id, 'start state:', str_start_state)
    while True:                                                 #главный цикл игры
        try:
            raw_options = current_player.socket.recv(1024)
            str_options = raw_options.decode()
            options = json.loads(str_options)
        except Exception as err:
            print('Потерянно соеденение с : ', current_player.id, 'игрок отключился')
            break
        current_player.apply_options(options)
        players_state = {}
        for id, player in players.items():
            if player:
                players_state[id] = player.get_self_state()
 #       players_state
        try:
            str_players_state = json.dumps(players_state)
            byte_players_state = str_players_state.encode()
            current_player.socket.send(byte_players_state)
        except Exception as err:
            print('connection error : ', err)
    remove_player(current_player.id)
    active_players_num -= 1


while True:
    player_socket, adress = start_socket.accept()
    print('Подключился игрок с адресом : ', adress)
    for id, player_in_slot in players.items():
        if not player_in_slot:
            player = Player(id, player_socket, GRAVITY)
            players[id] = player
            active_players_num += 1
            threading.Thread(target=threaded_player, args=(player,)).start()
            break
    else:
        print('Максимальное кичество игроков')
        player_socket.close()
        