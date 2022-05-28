import socket
from _thread import *
import sys
from snake.player import Player
import pickle
from game import Game

server = "127.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("waiting for connection, server started")

connected = set()
games = {}
idCount = 0

def threaded_client(conn, p, gameId):

    global idCount
    conn.send(str.encode(str(p)))
# Threaded client is always trying to recieve data. If the game has already
# been made and there is another player waiting, then the second player joins that game
# If no data is recieved, you break out of the loop. If the data is not 'get', then a move is being made
# and the game.play function is run.
    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()

            if gameId in games:
                game = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetWent()
                    elif data != "get":
                        game.play(p, data)
                    reply = game
                    print(reply)
                    conn.sendall(pickle.dumps(reply))
            else:
                break
        except:
            break
    print("lost connection")
    try:
        del games[gameId]
        print("closing game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()

# Accepts the connection.
# calculates if there is an even number of players. If so, then you are 
# the second player to join the game, you are player 2 (1), and the game.ready is turned to true.
# else you are the first player and a new game instance has to be created.
while True:
    conn, addr = s.accept()
    print("connected to: ", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1) // 2
    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        print("creating a new game")
    else:
        games[gameId].ready = True
        p = 1

    start_new_thread(threaded_client, (conn, p, gameId))
