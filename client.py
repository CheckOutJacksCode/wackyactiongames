import pygame
pygame.init()
from network import Network
import pickle
pygame.font.init()

# setting up the pygame window
width = 700
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

#  Creates a button instace, will use three times for 'rock', 'paper', and 'scissors'
class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

# Renders the button to the screen
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, 1, (255, 255, 255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

# Checks to see if the click happened inside of the button on the screen, 
# returns true, false if not.
    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False

# If the socket connection is not made, the screen renders 'waiting for player...'
# as you need two people for a rock paper scissors game. 
def redrawWindow(win, game, p):
    win.fill((128, 128, 128))

    if not (game.connected()):
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("waiting for player...", 1, (255,0,0), True)
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))

# If both players are connected, it is ready for a move to be made, and displays 'your move'.
# It retrieves both players' moves and renders them to the screen if both players have gone   
    else:
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Your Move", 1, (0,255,255))
        win.blit(text, (80, 200))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 200))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        if game.bothWent():
            text1 = font.render(move1, 1, (0,0,0))
            text2 = font.render(move2, 1, (0,0,0))
        else:
# If you are player 1, and you went but your opponent has not, it will display 'Locked In'
# on your side of the screen, and 'waiting' on your opponents. Opposite if you are player 2.
            if game.p1Went and p == 0:
                text1 = font.render(move1, 1, (0,0,0))
            elif game.p1Went:
                text1 = font.render("Locked In", 1, (0,0,0))
            else:
                text1 = font.render("Waiting...", 1, (0,0,0))

            if game.p2Went and p == 1:
                text2 = font.render(move2, 1, (0,0,0))
            elif game.p2Went:
                text2 = font.render("Locked In", 1, (0,0,0))
            else:
                text2 = font.render("Waiting...", 1, (0,0,0))

        if p == 1:
            win.blit(text2, (100, 350))
            win.blit(text1, (400, 350))
        else:
            win.blit(text1, (100, 350))
            win.blit(text2, (400, 350))

        for btn in btns:
            btn.draw(win)

    pygame.display.update()


btns = [Button("Rock", 50, 500, (0,0,0)), Button("Scissors", 250, 500, (255,0,0)), Button("Paper", 450, 500, (0,255,0))]

# Creates a new instance of a local network
# sends 'get' to the server to create a new game on the network.
def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()
    player = int(n.getP())
    print("you are player", player)

    while run:
        clock.tick(60)
        try:
            game = n.send("get")
        except:
            run = False
            print("couldn't get game")
            break
# If both players have gone, redraw the window, delay for 5 seconds,
# and then try and reset the window, calling the network again.
        if game.bothWent():
            redrawWindow(win, game, player)
            pygame.time.delay(500)
            try:
                game = n.send("reset")
            except:
                run = False
                print("couldn't get game")
                break
# Logic to find out who won.
            font = pygame.font.SysFont("cominsans", 90)
            if (game.winner() == 1 and player == 1) or (game.winner == 0 and player == 0):
                text = font.render("YOU WON!", 1, (255,0,0))
            elif game.winner() == -1:
                text = font.render("TIE GAME!", 1, (255,0,0))
            else:
                text = font.render("YOU LOST...", 1, (255,0,0))
            win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(2000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

# Heres where the event loop happens, if player one clicks on a button,
# and a button hasn't already been clicked for player one, the network sends the 
# button text. Else, you are player two and if you haven't gone already, it makes
# a move and redraws the window.
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in btns:
                    if btn.click(pos) and game.connected():
                        if player == 0:
                            if not game.p1Went:
                                n.send(btn.text)
                        else:
                            if not game.p2Went:
                                n.send(btn.text)
        redrawWindow(win, game, player)

def menu_screen():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("click to play!", 1, (255,0,0))
        win.blit(text, (100,200))
        pygame.display.update()

# if you click on the menu screen, the run loop ends and the main function is called.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False
    main()

while True:
    menu_screen()

main()