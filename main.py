import pygame
from pygame.locals import *
from GameController import GameController
from GameState import StationaryState
import enum
from mmagent import MMAgent

WIDTH = 550
HEIGHT = 720
COLOR_BG = "purple"

class Players(enum.Enum):
    Human = 0
    MMAgent = 1
    
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # set caption for the game
    pygame.display.set_caption("Bejeweled")
    clock = pygame.time.Clock()
    running = True
    # init game
    game_controller = GameController()

    #------------------- SELECT PLAYERS HERE -------------------
    player = Players.Human
    # player = Players.MMAgent
    # player= Players.RLAgent # not implemented yet
    # -----------------------------------------------------------

    # init AI
    agent = None
    if player == Players.MMAgent:
        agent = MMAgent()
    mouse_event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(0, 0))
    while running:
        # allow agents to play when board is stationary
        if game_controller.state == StationaryState:
            if player == Players.MMAgent:
                agent.play_game(game_controller.board)
            
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                game_controller.on_click(event)
                
        # game update
        game_controller.run()

        # game draw
        screen.fill(COLOR_BG)
        game_controller.draw(screen)

        pygame.display.update()

        clock.tick(60) # FPS


pygame.quit()