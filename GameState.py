import pygame, random
from Gem import CELL_SIZE
from Board import GEMS_NUM

class GameState(object):
    @staticmethod
    def run(controller):
        raise NotImplementedError()
    
class BeginningState(GameState):
    def run(controller):
        b = controller.board
        # make the gems fall down to the bottom of the board
        if b.board[0][0].rect.top < b.board_rects[0][0].top:
            # move the gem down with the specified speed
            for r in b.board:
                for gem in r:
                    gem.rect.move_ip(0, controller.FALL_SPEED)
        else:
            # reset cell rects
            b.reset()
            controller.change_state(StationaryState)

class StationaryState(GameState):
    def run(controller):
        # if two valid cells are selected
        if controller.cell_selected_1 and controller.cell_selected_2:
            controller.swap_times = 2
            controller.change_state(SwappingState)

class SwappingState(GameState):
    def run(controller):
        # swapping animation
        SwappingState.move_gems(controller)
        if controller.swap_times == 0:
            if controller.swap_success:
                controller.change_state(ClearingMatchesState)
                controller.swap_success = False
            else:    
                controller.change_state(StationaryState)

    def move_gems(controller):
        b = controller.board
        swap_speed = controller.MOVE_SPEED
        r1, c1 = controller.cell_selected_1
        r2, c2 = controller.cell_selected_2
        gem1 = b.board[r1][c1]
        gem2 = b.board[r2][c2]
        if gem1.vel == [] and gem2.vel == []:
            # set up vels for two gems
            if gem1.rect.y == gem2.rect.y and gem1.rect.x < gem2.rect.x:
                gem1.vel, gem2.vel = [swap_speed, 0], [-swap_speed, 0]
            elif gem1.rect.y == gem2.rect.y and gem1.rect.x > gem2.rect.x:
                gem1.vel, gem2.vel = [-swap_speed, 0], [swap_speed, 0]
            elif gem1.rect.x == gem2.rect.x and gem1.rect.y < gem2.rect.y:
                gem1.vel, gem2.vel = [0, swap_speed], [0, -swap_speed]   
            elif gem1.rect.x == gem2.rect.x and gem1.rect.y > gem2.rect.y:
                gem1.vel, gem2.vel = [0, -swap_speed], [0, swap_speed]
            
        if controller.gem_move_distance < CELL_SIZE + 1:
            gem1.rect.move_ip(gem1.vel)
            gem2.rect.move_ip(gem2.vel)
            controller.gem_move_distance += swap_speed
        else: 
            # reset swap distance
            controller.gem_move_distance = 0
            # reduce swap times
            controller.swap_times -= 1
            # reset gem velocity
            gem1.vel = []
            gem2.vel = []
            # reset all cell rects
            b.reset()
            # swap gems
            SwappingState.swap_gems(gem1, gem2)
            # if the swap creates a match
            if b.is_match_made(r1, c1) or b.is_match_made(r2, c2):
                controller.swap_times = 0 # set swap_times to end
                controller.swap_success = True
            # reset variables when swap times = 0
            if controller.swap_times == 0:
                gem1.is_selected = False
                gem2.is_selected = False
                controller.cell_selected_1 = None
                controller.cell_selected_2 = None

    # swap gems
    def swap_gems(gem1, gem2):
        # swap gem type
        gem1.gem_type, gem2.gem_type = gem2.gem_type, gem1.gem_type       
        # swap images
        gem1.images, gem2.images = gem2.images, gem1.images
        
class ClearingMatchesState(GameState):
    def run(controller):
        removed = ClearingMatchesState.remove_matches(controller.board)
        if removed == 0:
            controller.change_state(StationaryState)
        else:
            (s1, s2, s3) = removed
            # update score
            controller.score += s1 * controller.THREE_MATCHES_SCORE + \
                s2 * controller.FOUR_MATCHES_SCORE + \
                s3 * controller.FIVE_MATCHES_SCORE
            controller.score_text.update_msg("Score " + str(controller.score))
            # set up the bottom empty cells
            controller.set_bottom_empty_cells()
            controller.change_state(GemFallState)

    def remove_matches(board):
        matches = ClearingMatchesState.get_matches(board)
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
            for pos in match:
                row, col = pos
                board.board[row][col].gem_type = -1
                board.board[row][col].images = None
        if len(matches) > 0:
            return three_matches, four_matches, five_matches
        return 0 # no matches

    def get_matches(board):
        visited = [] # list of gems that we visited
        matches = []
        # scan through the cols
        for row in board.board:
            for col in range(board.cols - 2):
                if (row[col].gem_type == 
                    row[col + 1].gem_type == 
                    row[col + 2].gem_type) and \
                    (row[col].gem_type != -1):
                    r = board.board.index(row)
                    if (r, col) not in visited:
                        match = [(r, col), (r, col + 1), (r, col + 2)]
                        if col + 3 < board.cols and row[col + 3].gem_type == row[col].gem_type:
                            match.append((r, col + 3))
                            if col + 4 < board.cols and row[col + 4].gem_type == row[col].gem_type:
                                match.append((r, col + 4))
                        matches.append(match)
                        visited.extend(match)

        # scan through the rows       
        visited = []
        for col in range(board.cols):
            for row in range(board.rows - 2):
                if (board.board[row][col].gem_type == 
                    board.board[row + 1][col].gem_type == 
                    board.board[row + 2][col].gem_type) and \
                    board.board[row][col].gem_type != -1:
                    if (row, col) in visited:
                        continue
                    else:
                        match = [(row, col),(row + 1, col), (row + 2, col)]
                        if row + 3 < board.rows and board.board[row + 3][col].gem_type == board.board[row][col].gem_type:
                            match.append((row + 3, col))
                            if row + 4 < board.rows and board.board[row + 4][col].gem_type == board.board[row][col].gem_type:
                                match.append((row + 4, col))

                        matches.append(match)
                        visited.extend(matches)
        return matches        

class GemFallState(GameState):
    def run(controller):
        if GemFallState.make_gems_fall(controller) == 1:
            controller.set_bottom_empty_cells()
            if (controller.bottom_empty_cells == []):
                controller.change_state(ClearingMatchesState)

    def make_gems_fall(controller):
        # move the gems to the empty space in the board
        falling_gems = []
        b = controller.board
        for (row, col) in controller.bottom_empty_cells:
            for r in range(row, -1, -1):
                if b.board[r][col].gem_type > -1:
                    if b.board[r][col].rect.bottom != b.board[row][col].rect.bottom:
                        falling_gems.append(b.board[r][col])
        # update gem move distance
        if controller.gem_move_distance < CELL_SIZE:
            for cell in falling_gems:
                cell.rect.move_ip(0, controller.FALL_SPEED)
            controller.gem_move_distance += controller.FALL_SPEED
        else:
            b.reset()
            # randomise gem and pull it down
            for (row, col) in controller.bottom_empty_cells:
                for r in range(row, -1, -1):
                    if r == 0:
                        b.board[r][col].reset(random.randint(0, GEMS_NUM - 1))
                    else:
                        b.board[r][col].reset(b.board[r - 1][col].gem_type)
            controller.gem_move_distance = 0 # reset gem move distance
            return 1
        return 0



