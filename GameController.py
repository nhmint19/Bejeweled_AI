from GameState import StationaryState, BeginningState
from Board import Board
from utils import Text

class GameController(object):
    FALL_SPEED = 10
    MOVE_SPEED = 3
    THREE_MATCHES_SCORE = 100
    FOUR_MATCHES_SCORE = 200
    FIVE_MATCHES_SCORE = 300
    def __init__(self):
        self.state = BeginningState
        self.board = Board()
        self.cell_selected_1 = None # position of the first gem selected
        self.cell_selected_2 = None # position of the second gem selected
        self.gem_move_distance = 0 # the total distance that the gem moves
        self.swap_times = 0 # the times that swap actions are performed
        self.swap_success = False
        self.score = 0
        self.bottom_empty_cells = []
        self.score_text = Text(30, "Score " + str(self.score), (20, 550))
        
    def on_click(self, event):
        if self.state == StationaryState and not self.cell_selected_2:
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
        
        self.state.run(self)

    def change_state(self, state):
        self.state = state

    def draw(self, screen):
        # draw the board
        self.board.draw(screen)
        # display the score
        self.score_text.draw(screen)

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

