import pygame, random
from Gem import CELL_SIZE, Gem, MARGIN

ROWS = 8
COLUMNS = 8
GEMS_NUM = 7 
FALLING_DISTANCE = 0 # the distance that the gem falling from
FALL_SPEED = 5
COLOR_GRID = "black"

# the set of valid matches
MATCHES = [
    ([-2, 0], [-1, 0]),
    ([-1, 0], [1, 0]),
    ([1, 0], [2, 0]),
    ([0, 1], [0, 2]),
    ([0, -1], [0, 1]),
    ([0, -1], [0, -2])
]

class Board(object):
    def __init__(self, rows = ROWS, cols = COLUMNS):
        self.rows = rows
        self.cols = cols
        self.board_rects = []
        self.board = []

        # init board with empty cells
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append(None)
            self.board.append(row)
        
        # init board_rects - the 2D array of rects to reset the board
        for r in range(self.rows):
            self.board_rects.append([])

        # set up board
        self.set_up_board()
    
    # return the clicked gem positions
    def select_gem(self, mousepos):
        for r in self.board:
            for gem in r:
                if gem.rect.collidepoint(mousepos):
                    gem.is_selected = True
                    return (self.board.index(r), r.index(gem))
        return None

    def draw(self, screen):
        # draw board's grids
        for x in range(MARGIN, CELL_SIZE * (COLUMNS + 1), CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, MARGIN), (x, CELL_SIZE * ROWS + MARGIN))
        for y in range(MARGIN, CELL_SIZE * (ROWS + 1), CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (MARGIN, y), (CELL_SIZE * COLUMNS + MARGIN, y))
        
        # draw gems
        for r in self.board:
            for gem in r:
                gem.draw(screen)

    # set up the board at the beginning of the game
    def set_up_board(self):
        # set up board rects
        x, y = MARGIN, MARGIN
        for r in self.board_rects:
            for c in range(self.cols):
                r.append(pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
                x += CELL_SIZE
            x = MARGIN
            y += CELL_SIZE

        # generate gems
        self.generate_gems()

    # generate gems (random approach)
    def generate_gems(self):
        for r in range(self.rows):
            for c in range(self.cols):
                gem_types = list(range(GEMS_NUM))
                # check that if it can make a match
                # get all the possible gem types that can make a match
                gem_types_matched = self.get_gem_type_to_match(r, c)
                # remove those gem typess
                for gem_type in gem_types_matched:
                    gem_types.remove(gem_type)
                # generate a new gem
                self.board[r][c] = Gem(random.choice(gem_types), (
                    self.board_rects[r][c].left,
                    self.board_rects[r][c].top - FALLING_DISTANCE
                ))

    # get the possible gem types to create a match
    def get_gem_type_to_match(self, r, c):
        gem_types = []
        if self.is_valid_pos(r, c):
            # check with MATCHES
            for (match1, match2) in MATCHES:
                if (
                    # check if the position in the possible matches set is valid
                    self.is_valid_pos(r + match1[0], c + match1[1]) and 
                    self.is_valid_pos(r + match2[0], c + match2[1]) and
                    # check if the gem in these positions is not None
                    self.board[r + match1[0]][c + match1[1]] and 
                    self.board[r + match2[0]][c + match2[1]] and
                    # check if the gem types in these positions are the same
                    self.board[r + match1[0]][c + match1[1]].gem_type == 
                    self.board[r + match2[0]][c + match2[1]].gem_type
                    ):
                    gem_type = self.board[r + match1[0]][c + match1[1]].gem_type
                    if gem_type not in gem_types:
                        gem_types.append(gem_type)
        return gem_types

    # check if the gem makes a match
    def is_match_made(self, r, c):
        if self.is_valid_pos(r, c):
            # check with MATCHES
            for (match1, match2) in MATCHES:
                if (
                    # check if the position in the possible matches set is valid
                    self.is_valid_pos(r + match1[0], c + match1[1]) and 
                    self.is_valid_pos(r + match2[0], c + match2[1]) and
                    # check if the gem in these positions is not None
                    self.board[r + match1[0]][c + match1[1]] and 
                    self.board[r + match2[0]][c + match2[1]] and
                    # check if the gem types in these positions are the same
                    self.board[r + match1[0]][c + match1[1]].gem_type == 
                    self.board[r + match2[0]][c + match2[1]].gem_type ==
                    self.board[r][c].gem_type
                    ):
                    return True
        return False
    
    # get the matches
    def get_matches(self, r, c):
        matches = []
        if self.is_valid_pos(r, c):
            matches.append([0, 0])
            # check with MATCHES
            for (match1, match2) in MATCHES:
                if (
                    # check if the position in the possible matches set is valid
                    self.is_valid_pos(r + match1[0], c + match1[1]) and 
                    self.is_valid_pos(r + match2[0], c + match2[1]) and
                    # check if the gem in these positions is not None
                    self.board[r + match1[0]][c + match1[1]] and 
                    self.board[r + match2[0]][c + match2[1]] and
                    # check if the gem types in these positions are the same
                    self.board[r + match1[0]][c + match1[1]].gem_type == 
                    self.board[r + match2[0]][c + match2[1]].gem_type ==
                    self.board[r][c].gem_type
                    ):
                    if match1 not in matches:
                        matches.append(match1)
                    if match2 not in matches:
                        matches.append(match2)
        return matches
    
    # check if the position is valid
    def is_valid_pos(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLUMNS

    # reset board
    def reset(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c].rect.topleft = self.board_rects[r][c].topleft

