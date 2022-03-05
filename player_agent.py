from random import random, seed, choice, randint
import pickle
import os
import sys
from game_state import GameResult, GameLog

seed(6)

class Move():
    def __init__(self):
        self.action = None
        self.state = None
        self.reward = None


class Player():
    def __init__(self, marker, rows=3, columns=3):
        self.marker = marker
        # Set at .2 for testing however can set to -1 to remove random pathing
        self.random_action = -1
        self.epsilon_decay = .999
        self.alpha = .01
        self.gamma = .99
        self.previous_move = Move()
        # Q is composed of available actions 
        self.Q = {}
        for r in range(rows):
            for c in range(columns):
                self.Q[(r,c)] = {}

        # The attributes are just for plotting and analysis
        self.win_log = GameLog(result_type=GameResult.WIN)
        self.loss_log = GameLog(result_type=GameResult.LOSS)
        self.draw_log = GameLog(result_type=GameResult.DRAW)
        self.agent_type = "QLearning"

    def _get_best_move(self, moves, moves_hash):
        best_moves = []
        best_move_score = -1 * sys.maxsize
        for m in range(len(moves)):
            # Lazy init of Q
            if moves_hash[m] not in self.Q[moves[m]]:
                self.Q[moves[m]][moves_hash[m]] = 0

            # Check if current move beats all others
            if self.Q[moves[m]][moves_hash[m]] > best_move_score:
                best_moves = [m]
                best_move_score = self.Q[moves[m]][moves_hash[m]]
            elif self.Q[moves[m]][moves_hash[m]] == best_move_score:
                best_moves.append(m)
        choice([moves[m] for m in best_moves])

        return choice([moves[m] for m in best_moves])

    def _get_random_move(self, moves, moves_hash):
        index = randint(0, len(moves)-1)
        if moves_hash[index] not in self.Q[moves[index]]:
            self.Q[moves[index]][moves_hash[index]] = 0
        return moves[index]

    # Updates the previous state
    def update_state(self, next_best_q, board, state = None, action = None):
        
        test_gamma = self.gamma
        test_gamma = (1-(board.get_board_state().count("-")/len(board.get_board_state())))
        
        # If this is our first move then do nothing
        if self.previous_move.action:
            self.Q[self.previous_move.action][self.previous_move.state] += self.alpha * \
                    (self.previous_move.reward + test_gamma * next_best_q - self.Q[self.previous_move.action][self.previous_move.state])
        if action:
            self.previous_move.state = state
            self.previous_move.action = action
        
        # TODO See if this is needed?
        self.previous_move.reward = board.get_reward(self.marker)


    def makeMove(self, board):
        board_state_init = board.get_board_state()

        moves, moves_hash = board.get_available_moves(self.marker)
        
        # More random as k becomes larger?  Idea 1/k
        if random() < self.random_action:
            action = self._get_random_move(moves, moves_hash)
            self.random_action = self.random_action * self.epsilon_decay
            board.random_action = True
        else:
            action = self._get_best_move(moves, moves_hash)
        
        board.set_tile(action[0], action[1], self.marker)
        board_state = board.get_board_state()

        #  Since other player alters state we can't do a look ahead.
        self.update_state(self.Q[action][board.get_board_state()], board, board.get_board_state(), action)

    def save_q_state(self, pickle_file):
        try:
            os.mkdir("environments")
        except FileExistsError:
            pass
        with open(pickle_file, "wb") as f:
            # Pickle everything we need as a list for easy loading and saving
            pickle.dump([self.Q, self.win_log, self.draw_log, self.loss_log], f)

    def update_all_counters(self):
        self.loss_log.update_game_counters()
        self.draw_log.update_game_counters()
        self.win_log.update_game_counters()

    def load_q_state(self, pickle_file):
        try:
            with open(pickle_file, "rb") as f:
                pickle_list = pickle.load(f)
                self.Q = pickle_list[0]
                self.win_log = pickle_list[1]
                self.draw_log = pickle_list[2]
                self.loss_log = pickle_list[3]
                self.update_all_counters()
                
        except FileNotFoundError:
            print("Q environment file does not exist.  One will be created upon calling save.")

    def record_end_of_game(self, board, result, record_random_games):
        if os.environ['PRINT_OUTPUT'] == "TRUE":
            print(board.pretty_print_board())
        if result == GameResult.WIN:
            self.update_state(board.win_value, board)
            if record_random_games or not board.random_action:
                self.win_log.update_all_attributes(self.previous_move.action,
                                                   board.get_board_state())
            if os.environ['PRINT_OUTPUT'] == "TRUE":
                # Since this will likely only be used for human players for printing,
                #  the loss is for the RL.  For everything else, the perspective is for
                #  the RL.
                print("\n------------  Loss")
        if result == GameResult.LOSS:
            self.update_state(board.lose_value, board)
            if record_random_games or not board.random_action:
                self.loss_log.update_all_attributes(self.previous_move.action,
                                                   board.get_board_state())
            if os.environ['PRINT_OUTPUT'] == "TRUE":
                print("\n------------  Win -------------\n")  
        if result == GameResult.DRAW:
            self.update_state(board.draw_value, board)
            if record_random_games or not board.random_action:
                self.draw_log.update_all_attributes(self.previous_move.action,
                                                   board.get_board_state())
            if os.environ['PRINT_OUTPUT'] == "TRUE":
                print("\n------------  Draw Game -------------\n")


class RandomPlayer(Player):

    def __init__(self, marker, rows=3, columns=3):
        self.marker = marker
        self.win_log = GameLog(result_type=GameResult.WIN)
        self.loss_log = GameLog(result_type=GameResult.LOSS)
        self.draw_log = GameLog(result_type=GameResult.DRAW)
        self.agent_type = "Random"

    def makeMove(self, board):
        moves, _ = board.get_available_moves(self.marker)
        move = choice(moves)
        board.set_tile(move[0], move[1], self.marker)

    def update_state(self, next_best_q, board, state = None, action = None):
        pass

    def load_q_state(self, pickle_file):
        pass

    def record_end_of_game(self, board, result, record_random):
        pass

class HumanPlayer(Player):

    def __init__(self, marker, rows=3, columns=3):
        self.marker = marker
        self.win_log = GameLog(result_type=GameResult.WIN)
        self.loss_log = GameLog(result_type=GameResult.LOSS)
        self.draw_log = GameLog(result_type=GameResult.DRAW)
        self.agent_type = "Human"

    def makeMove(self, board):
        board.pretty_print_board()
        sel = input("Enter selection, either row, column in tic tac toe or ABCDEFGHI: ")
        sel = sel.strip()
        
        if len(sel) == 1:
            row, col = board.abc_to_row_col(sel)
            while not board.is_valid_move(row, col):
                sel = input("Invalid selection, please try again: ")
                sel = sel.strip()
                row, col = board.abc_to_row_col(sel)

        board.set_tile(row, col, self.marker)

    def update_state(self, next_best_q, board, state = None, action = None):
        pass

    def load_q_state(self, pickle_file):
        pass

    def record_end_of_game(self, board, result, record_random):
        pass