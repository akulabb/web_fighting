import socket
import threading
import time
import json

ERROR = -1

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
GROUND_LEVEL = SCREEN_HEIGHT - 150              #716
START_POSITIONS = (int(SCREEN_WIDTH / 5), 
                   int(SCREEN_WIDTH - SCREEN_WIDTH / 5),
                   int(SCREEN_WIDTH / 5 * 2),
                   int(SCREEN_WIDTH / 5 * 3)
                   )

SERVER = 'localhost'
PORT = 5555


STAY = 0
GO = 1
JUMP = 2
ATTACK = 3
HITTED = 4
DEAD = 5


ATTACK_DELAY = 5
HITTED_DELAY = 5

PLAYER_SIZE = (130, 130)

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

game_started = False

max_players_num = 0
connected_players_num = 0
alive_players_num = 0

class Player:
    def __init__(self, id, socket, gravity):
        self.attack_delay = 0
        self.hitted_delay = 0
        self.action = STAY     # 0 = stay, 1 = go, 2 = jump, 3 = attack, 4 hitted, 5 = dead
        self.id = id
        self.dir = bool(self.id % 2) or False            # True влево, False вправо
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
        self.attack_delay = ATTACK_DELAY
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
        global alive_players_num
        self.hitted_delay = HITTED_DELAY
        if self.health > 0:
            self.health -= 5
            self.action = HITTED
        if self.health < 1 and self.action != DEAD:
            self.action = DEAD
            alive_players_num -= 1
            print(f'player: {self.id} dead, alive_players_num{alive_players_num}')
        print('hitted:health', self.health)
    
    def apply_options(self, options):
        dx = 0
        dy = 0
        # gravitation
        self.fall_speed += self.gravity
        dy = self.fall_speed
        
        # удержание спрайта в пределах экрана
        if (self.rect.left + dx) < 0:       #левая граница экрана
            dx = -self.rect.left
        elif self.rect.right + dx > SCREEN_WIDTH:   #правая граница
            dx = SCREEN_WIDTH - self.rect.right
        if (self.rect.bottom + dy) > GROUND_LEVEL:
            dy = (GROUND_LEVEL - self.rect.bottom)
            self.fall_speed = 0
            self.jumping = False
        
        # controling
        if self.action != DEAD:
            if self.hitted_delay:
                self.action = HITTED
                self.hitted_delay -= 1
            else:
                self.action = STAY
                if options.get('move'):
                    self.action = GO
                if options.get('jump') and not self.jumping:
                    self.fall_speed = -30
                    self.jumping = True
                    self.action = JUMP
                if options.get('hit') and not self.attack_delay:
                    print('call attack')
                    self.action = ATTACK
                    self.attack()
                dx += options.get('move')
                self.dir = options.get('direction')

        pos_x = self.rect.center_x + dx
        pos_y = self.rect.center_y + dy
        if self.attack_delay:
            self.attack_delay -= 1
        self.rect.update(pos_x, pos_y)
        
    def get_self_state(self):
        return (self.rect.center_x, self.rect.center_y, self.health, self.action, self.dir)
    

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
    global connected_players_num
    players[id].socket.close()
    players[id] = None
    print('игрок закончился с id : ', id)
    connected_players_num -= 1

def send(data, client_socket):
    try:
        str_data = json.dumps(data)
        byte_data = str_data.encode()
        client_socket.send(byte_data)
    except Exception as err:
        print('connection error : ', err)

def recieve(client_socket,):
    try:
        raw_data = client_socket.recv(1024)
        str_data = raw_data.decode()
        data = json.loads(str_data)
    except Exception as err:
        print(err)
        data = ERROR
    finally:
        return data

def threaded_referee():
    global game_started, alive_players_num, max_players_num
    while True:
        if game_started:
            print('Referee: game started!')
            while threading.active_count() > 2:
                time.sleep(0.15)
            game_started = False
            alive_players_num = 0
            max_players_num = 0
            print('Referee: game over!')
        else:
            time.sleep(0.25)

def threaded_player(current_player):
    print('Игрок создан с id : ', current_player.id)
    start_state = {'current_player_id' : current_player.id}
    global connected_players_num, alive_players_num, max_players_num, game_started
  #  while connected_players_num < 2:
   #     print(connected_players_num, 'кол-во игроков')
    #    time.sleep(1)
    for id, player in players.items():
        if player:
            start_state[id] = (player.dir,
                               player.rect.center_x, 
                               player.rect.center_y, 
                               player.rect.width,
                               player.rect.height,
                               )
    send(start_state, current_player.socket)
    print('player', current_player.id, 'start state:', start_state)
                                                                            #TODO ожидание нажатия кнопки играть клиентом
    alive_players_num += 1
    max_players_num += 1
    print(f'alive_players_num:{alive_players_num}, max_players_num{max_players_num}')
    while True:                                                    #главный цикл игры
        options = recieve(current_player.socket)
        if options == ERROR:
            print('Потерянно соеденение с : ', current_player.id, 'игрок отключился')
            alive_players_num -= 1
            break
        game_started = True
        current_player.apply_options(options)
        players_state = {}
        for id, player in players.items():
            if player:
                players_state[id] = player.get_self_state()
 #       players_state
        send(players_state, current_player.socket)
        if alive_players_num < 2 and max_players_num > 1:
            print('GAME OVER', current_player.id)
            print(max_players_num, 'max_players_num')
            print(alive_players_num, 'alive_players_num')
            current_player.socket.recv(1024)
            for id, player in players.items():
                if player:
                    players_state[id] = 'finish'
            max_players_num = 0
            alive_players_num = 0
            send(players_state, current_player.socket)
            break
    remove_player(current_player.id)

threading.Thread(target=threaded_referee).start()

while True:
    player_socket, adress = start_socket.accept()
    print('Подключился игрок с адресом : ', adress)
    for id, player_in_slot in players.items():
        if not player_in_slot:
            player = Player(id, player_socket, GRAVITY)
            players[id] = player
            connected_players_num += 1
            threading.Thread(target=threaded_player, args=(player,)).start()
            break
    else:
        print('Максимальное кичество игроков')
        player_socket.close()
        