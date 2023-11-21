import socket
import threading
import time
import json


SCREEN_HEIGHT = 970
SCREEN_WIDTH = 1280
GROUND_LEVEL = SCREEN_HEIGHT - 254
START_POSITIONS = (int(SCREEN_WIDTH / 5), 
                   int(SCREEN_WIDTH - SCREEN_WIDTH / 5),
                   int(SCREEN_WIDTH / 5 * 2),
                   int(SCREEN_WIDTH / 5 * 3)
                   )

SERVER = 'localhost'
PORT = 5555

start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start_socket.bind((SERVER, PORT))
start_socket.listen(2)
print('Сервер запущен')

players = {0 : None,
		   1 : None,
		   2 : None,
		   3 : None,
		   }

def remove_player(id):
	players[id].close()
	players[id] = None
	print('игрок закончился с id : ', id)


def fighter(id):
    fighter_socket = players[id]
    print('Игрок создан с id : ', id)
    x_pos = START_POSITIONS[id]
    y_pos = GROUND_LEVEL
    start_pos = json.dumps((x_pos, y_pos))
    fighter_socket.send(start_pos.encode())
    while True:
        try:
            raw_options = fighter_socket.recv(1024)
            str_options = raw_options.decode()
            options = json.loads(str_options)
            print('options:', options)
        except Exception as err:
            print('Потерянно соеденение с : ', id, 'игрок отключился')
            break
    remove_player(id)


while True:
	player_socket, adress = start_socket.accept()
	print('Подключился игрок с адресом : ', adress)
	for id, player in players.items():
		if not player:
			players[id] = player_socket
			threading.Thread(target=fighter, args=(id,)).start()
			break
	else:
		print('Максимальное кичество игроков')
		player_socket.close()