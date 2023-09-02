THREE_MATCHES_SCORE = 100
FOUR_MATCHES_SCORE = 200
FIVE_MATCHES_SCORE = 300
from copy import deepcopy
import pygame
from pygame.locals import *

# Applying minimax algorithm
class MMAgent(object):
    def __init__(self):
        self.active = True
        
    # play game
    def play_game(self, board):
        # simplify the board object
        if self.active:
            board_state = []
            for r in board.board:
                row = []
                for gem in r:
                    row.append(gem.gem_type)
                board_state.append(row)
            (r1, c1), (r2, c2) = self.get_best_move(board_state, board.rows, board.cols)
            pos1, pos2 = (self.get_gem_coordinates(board, r1, c1), self.get_gem_coordinates(board, r2, c2))
            mouse_event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=pos1)
            pygame.event.post(mouse_event)
            mouse_event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=pos2)
            pygame.event.post(mouse_event)
            self.active = False

    # get best move
    def get_best_move(self, board, rows, cols, depth=1):
        max_score = float('-inf')
        best_move = None
        moves = self.generate_moves(rows, cols)

        for move in moves:
            new_board = self.make_move(board, move)
            score = self.minimax(new_board, depth - 1, False, rows, cols)
            if score > max_score:
                max_score = score
                best_move = move
        return best_move
    
    # minimax algorithm 
    def minimax(self, board, depth, maximizing_player, rows, cols):
        if depth == 0:
            return self.calculate_score(board, rows, cols)

        if maximizing_player:
            max_score = float('-inf')
            moves = self.generate_moves(rows, cols)

            for move in moves:
                new_board = self.make_move(board, move)
                score = self.minimax(new_board, depth - 1, False, rows, cols)
                max_score = max(max_score, score)

            return max_score
        else:
            min_score = float('inf')
            moves = self.generate_moves(rows, cols)

            for move in moves:
                new_board = self.make_move(board, move)
                score = self.minimax(new_board, depth - 1, True, rows, cols)
                min_score = min(min_score, score)

            return min_score
        
    # make a move
    def make_move(self, board, move):
        ((r1, c1), (r2, c2)) = move
        new_board = deepcopy(board)
        new_board[r1][c1], new_board[r2][c2] = new_board[r2][c2], new_board[r1][c1]
        return new_board
        
    # generate possible moves
    def generate_moves(self, rows, cols):
        moves = []
        for row in range(rows):
            for col in range(cols):
                # swap with the gem above if valid
                if row > 0:
                    moves.append(((row, col), (row - 1, col)))

                # swap with the gem below if valid
                if row < rows - 1:
                    moves.append(((row, col), (row + 1, col)))

                # swap with the gem to the left if valid
                if col > 0:
                    moves.append(((row, col), (row, col - 1)))

                # swap with the gem to the right if valid
                if col < cols - 1:
                    moves.append(((row, col), (row, col + 1)))
        return moves
    
    # calculate the score of a board state
    def calculate_score(self, board, rows, cols):
        score = 0
        visited = [] # list of gems that we visited
        matches = []
        # ---- find all current matches -----
        # scan through the cols
        for row in board:
            for col in range(cols - 2):
                if (row[col] == row[col + 1] == row[col + 2]) and (row[col] != -1):
                    r = board.index(row)
                    if (r, col) not in visited:
                        match = [(r, col), (r, col + 1), (r, col + 2)]
                        if col + 3 < cols and row[col + 3] == row[col]:
                            match.append((r, col + 3))
                            if col + 4 < cols and row[col + 4] == row[col]:
                                match.append((r, col + 4))
                        matches.append(match)
                        visited.extend(match)

        # scan through the rows       
        visited = []
        for col in range(cols):
            for row in range(rows - 2):
                if (board[row][col] == board[row + 1][col] == board[row + 2][col]) and board[row][col] != -1:
                    if (row, col) in visited:
                        continue
                    else:
                        match = [(row, col), (row + 1, col), (row + 2, col)]
                        if row + 3 < rows and board[row + 3][col] == board[row][col]:
                            match.append((row + 3, col))
                            if row + 4 < rows and board[row + 4][col] == board[row][col]:
                                match.append((row + 4, col))
                        matches.append(match)
                        visited.extend(matches)
        # ---- sort the matches' types ----   
        three_matches = 0
        four_matches = 0
        five_matches = 0
        for match in matches:
            if len(match) == 3:
                three_matches += 1
            elif len(match) == 4:
                four_matches += 1
            elif len(match) == 5:
                five_matches += 1      
        
        # ---- calculating score ------
        score += three_matches * THREE_MATCHES_SCORE + \
                four_matches * FOUR_MATCHES_SCORE + \
                five_matches * FIVE_MATCHES_SCORE
        
        return score
    
    # return the x,y positions based on the row and column of gem
    def get_gem_coordinates(self, board, r, c):
        rect = board.board_rects[r][c]
        return (rect.centerx, rect.centery)