from GameState import StationaryState, BeginningState, SwappingState
from Board import Board
from utils import Text
import pygame
from pygame.locals import *

pygame.init()

class Environment(object):
    FALL_SPEED = 10
    MOVE_SPEED = 10
    THREE_MATCHES_SCORE = 100
    FOUR_MATCHES_SCORE = 200
    FIVE_MATCHES_SCORE = 300
    MAX_CONSECUTIVE_INVALID_MOVE = 10
    WIDTH = 550
    HEIGHT = 720
    COLOR_BG = "purple"

    def __init__(self):
        # init display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        # set caption for the game
        pygame.display.set_caption("Bejeweled")
        self.clock = pygame.time.Clock()
        self.cell_selected_1 = None
        self.cell_selected_2 = None
        self.reset()
        
    def reset(self):
        self.last_game_state = None
        self.game_state = BeginningState
        self.board = Board()
        if self.cell_selected_1:
            r1, c1 = self.cell_selected_1
            self.board.board[r1][c1].is_selected = False
        if self.cell_selected_2:
            r1, c1 = self.cell_selected_2
            self.board.board[r1][c1].is_selected = False
        self.cell_selected_1 = None # position of the first gem selected
        self.cell_selected_2 = None # position of the second gem selected
        self.gem_move_distance = 0 # the total distance that the gem moves
        self.swap_times = 0 # the times that swap actions are performed
        self.swap_success = False
        self.score = 0
        self.bottom_empty_cells = []  
        self.consecutive_invalid_moves = 0
        self.score_text = Text(30, "Score " + str(self.score), (20, 550))

    def on_click(self, event):
        if self.game_state == StationaryState and not self.cell_selected_2:
            cell_selected = self.board.select_gem(event.pos)
            if cell_selected:
                # no cell selected
                if not self.cell_selected_1:
                    self.cell_selected_1 = cell_selected
                else:
                    # position of the first selected one
                    r1, c1 = self.cell_selected_1
                    # click on the same cell
                    if self.cell_selected_1 == cell_selected:
                        self.board.board[r1][c1].is_selected = False
                        self.cell_selected_1 = None
                    else:
                        # click on the adjacent cell
                        if self.is_adjacent(cell_selected, self.cell_selected_1):                       
                            self.cell_selected_2 = cell_selected
                        else:
                            # deselect the first cell
                            self.board.board[r1][c1].is_selected = False
                            # change the selection cell
                            self.cell_selected_1 = cell_selected

    def run(self):
        # 1. listen to agent's action
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                self.on_click(event)
        
        current_score = self.score

        # 2. game state run
        self.game_state.run(self)

        # 3. set up reward and check gameover
        reward = 0
        game_over = False
        # if swapping failed 
        if self.last_game_state == SwappingState and self.game_state == StationaryState:
            # raise the invalid moves values
            self.consecutive_invalid_moves += 1
            reward = -2
        # too many invalid moves ---> gameover
        if self.consecutive_invalid_moves > self.MAX_CONSECUTIVE_INVALID_MOVE:
            game_over = True
            reward = -10
            return reward, game_over, self.score
        # if score changed
        if self.score - current_score == self.THREE_MATCHES_SCORE:
            reward = +5
            self.consecutive_invalid_moves = 0
        elif self.score - current_score > self.THREE_MATCHES_SCORE:
            reward = +10
            self.consecutive_invalid_moves = 0

        # 4. update UI
        self.screen.fill(self.COLOR_BG)
        self.draw(self.screen)
        self.clock.tick(60)
        if reward != 0:
            print("Reward: ", reward)
        return reward, game_over, self.score

    def change_state(self, state):
        self.last_game_state = self.game_state
        self.game_state = state

    def draw(self, screen):
        # draw the board
        self.board.draw(screen)
        # display the score
        self.score_text.draw(screen)
        pygame.display.flip()

    # check if two cells are adjacent
    def is_adjacent(self, pos1, pos2):
        if pos1[0] == pos2[0]:
            if pos1[1] + 1 == pos2[1] or pos1[1] - 1 == pos2[1]:
                return True
        if pos1[1] == pos2[1]:
            if pos1[0] + 1 == pos2[0] or pos1[0] - 1 == pos2[0]:
                return True
        return False
    
    # set the bottom cells that are empty
    def set_bottom_empty_cells(self):
        board = self.board
        self.bottom_empty_cells = [] # list of the empty cells in every column
        
        for row in range(board.rows):
            for col in range(board.cols):
                if board.board[row][col].gem_type == -1:
                    if row + 1 < board.rows:
                        # find the bottom-most empty cells in the column
                        while board.board[row + 1][col].gem_type == -1: 
                            if row + 1 < board.rows - 1:
                                row += 1
                            else:
                                break
                    if not (row, col) in self.bottom_empty_cells:
                        self.bottom_empty_cells.append((row, col))
                        
    # return the x,y positions based on the row and column of gem
    def get_gem_coordinates(self, r, c):
        rect = self.board.board_rects[r][c]
        return (rect.centerx, rect.centery)
