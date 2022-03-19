from random import seed
from game_state import GameResult

seed(6)

class TicTacToeBoard():

    def __init__(self, rows=3, column=3):
        self.rows = rows
        self.col = column
        self.board = []
        self.win_value = 1
        self.lose_value = -1
        self.draw_value = .5
        self.transition_value = 0
        self.random_action = False
        self.abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

        for _ in range(rows):
            row = []
            for _ in range(column):
                row.append("-")
            self.board.append(row)

    def print_board(self):
        print(self.board)

    def get_board_state(self):
        return "".join([ "".join(r) for r in self.board])

    def get_available_moves(self, marker):
        moves_hash = []
        moves = []
        for r in range(self.rows):
            for c in range(self.col):
                if self.board[r][c] == '-':
                    self.board[r][c] = marker                    
                    moves_hash.append("".join(["".join(r) for r in self.board]))
                    self.board[r][c] = '-'
                    moves.append((r,c))
        return moves, moves_hash

    def set_tile(self, row, col, marker):
        # Defensive coding to make sure none of our updates do anything funny
        if self.board[row][col] != '-':
            raise Exception("Issue sending invalid row col for row: " + str(row) + \
                            "column: " + str(col) + " for marker " + marker)
        self.board[row][col] = marker

    def find_winner(self, marker):
        # win by rows
        marks = [marker] * self.rows
        for r in self.board:
            if r == marks:
                return marker

        # Win by column
        for ind in range(self.col):
            col = [row[ind] for row in self.board]
            if col == marks:
                return marker
        
        cross = [self.board[i][i] for i in range(self.col)]
        if cross == marks:
            return marker

        cross = [self.board[self.col-1-i][i] for i in range(self.col)]
        if cross == marks:
            return marker

        if "-" not in [xrow for row in self.board for xrow in row]:
            return GameResult.DRAW
        else:
            return None

    def get_reward(self, marker):
        winner = self.find_winner(marker)
        if not winner:
            return self.transition_value
        if winner == GameResult.DRAW:
            return self.draw_value
        if winner == marker:
            return self.win_value
        else:
            return self.lose_value # we lost

    def is_valid_move(self, row, col):
        if self.board[row][col] == '-':
            return True
        return False
        
    def abc_to_row_col(self, abc):
        ind = self.abc.index(abc)
        col = ind % self.col
        row = int(ind / self.col)
        return row, col

    def pretty_print_board(self, alpha=True):
        counter = 0
        print("_____________")
        for row in self.board:
            row_vals = []
            for col in row:
                if col == "-":
                    row_vals.append(self.abc[counter])
                else:
                    row_vals.append(col)
                counter += 1
            print("| " + " | ".join(row_vals) + " |")
        print("_____________")

    def moves_left(self):
        return self.get_board_state().count("-")

    def check_win_condition(self, mark):
        board = self.board
        for i in range(len(board)):
            row = board[i]
            if row[0] == mark and row[1] == mark and row[2] == '-':
                return (i, 2)
            if row[1] == mark and row[2] == mark and row[0] == '-':
                return (i, 0)
            if row[0] == mark and row[2] == mark and row[1] == '-':
                return (i, 1)

        # Check for column win
        for i in range(len(board)):
            if board[0][i] == mark and board[1][i] == mark and board[2][i] == '-':
                return (2, i)
            if board[1][i] == mark and board[2][i] == mark and board[0][i] == '-':
                return (0, i)
            if board[2][i] == mark and board[0][i] == mark and board[1][i] == '-':
                return (1, i)
            
        # Check for cross win
        if board[0][0] == mark and board[1][1] == mark and board[2][2] == '-':
            return (2, 2)
        if board[1][1] == mark and board[2][2] == mark and board[0][0] == '-':
            return (0, 0)
        if board[0][0] == mark and board[2][2] == mark and board[1][1] == '-':
            return (1, 1)
    
        if board[0][2] == mark and board[1][1] == mark and board[2][0] == '-':
            return (2, 0)
        if board[2][0] == mark and board[1][1] == mark and board[0][2] == '-':
            return (0, 2)
        if board[0][2] == mark and board[2][0] == mark and board[1][1] == '-':
            return (1, 1)

        return None