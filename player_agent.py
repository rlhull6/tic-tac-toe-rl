#################################################
#
#  Ryan Hull (hull0001)
#  CS 5033 Machine Learning 
#  Reinforced Machine Learning Midterm Project
#  Tic Tac Toe
#  March 18, 2022
#################################################

from game_state import GameResult, GameLog
from random import random, seed, choice, randint
import pickle
import os
import sys
import copy

seed(6)

class Move():
    def __init__(self):
        self.action = None
        self.state = None
        self.reward = None


class Player():
    def __init__(self, marker, rows=3, columns=3, random_action_percent=.8):
        self.marker = marker
        # Set at .2 for testing however can set to -1 to remove random pathing
        self.random_action = []
        for i in range(rows * columns + 1):
            self.random_action.append(random_action_percent)
        self.epsilon_decay = .99  # As this gets closer to 1, decay gets slower
        self.random_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.alpha = .1
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
        self.agent_type = "Sarsa"
        #self.random_action_stages = [100, 100, 100, 100, 100, 100, 500, 500, 1000, 1000]
        #self.random_action_stages = [1000, 1000, 1000, 1000, 2000, 2000, 3000, 3000, 8000, 8000]
        self.random_action_stages = [100, 100, 100, 100, 200, 200, 300, 300, 500, 500]
        self.random_action_stages.reverse()

    def _get_best_move(self, moves, moves_hash):
        best_moves = []
        best_move_score = -1 * sys.maxsize
        for m in range(len(moves)):
            # Lazy init of Q
            if moves_hash[m] not in self.Q[moves[m]]:
                self.Q[moves[m]][moves_hash[m]] = 0
            moveh = moves_hash[m]

            # Check if current move beats all others
            if self.Q[moves[m]][moves_hash[m]] > best_move_score:
                best_moves = [m]
                best_move_score = self.Q[moves[m]][moves_hash[m]]
            elif self.Q[moves[m]][moves_hash[m]] == best_move_score:
                best_moves.append(m)
        #choice([moves[m] for m in best_moves])

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
            q_previous = self.Q[self.previous_move.action][self.previous_move.state]
            new_q_value = self.alpha * (self.previous_move.reward + test_gamma * next_best_q - q_previous)
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

        moves_left = board.moves_left()
        if random() < self.random_action[moves_left]:
            action = self._get_random_move(moves, moves_hash)
            if self.marker == "X":
                board.random_action = True
            self.random_count[moves_left] += 1
            
            if self.random_count[moves_left] > self.random_action_stages[moves_left]:
                self.random_count[moves_left] = 0
                self.random_action[moves_left] = self.random_action[moves_left] * self.epsilon_decay
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
                self.previous_move.action = None
                self.previous_move.reward = None
                self.previous_move.state = None
                
        except FileNotFoundError:
            print(pickle_file)
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
                print("\n------------  You Lose  ------------ \n\n\n")
        if result == GameResult.LOSS:
            self.update_state(board.lose_value, board)
            if record_random_games or not board.random_action:
                self.loss_log.update_all_attributes(self.previous_move.action,
                                                   board.get_board_state())
            if os.environ['PRINT_OUTPUT'] == "TRUE":
                print("\n------------  Win -------------\n\n\n")  
        if result == GameResult.DRAW:
            self.update_state(board.draw_value, board)
            if record_random_games or not board.random_action:
                self.draw_log.update_all_attributes(self.previous_move.action,
                                                   board.get_board_state())
            if os.environ['PRINT_OUTPUT'] == "TRUE":
                print("\n------------  Draw Game -------------\n\n\n")


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

    def save_q_state(self, pickle_file):
        pass

class HumanPlayer(Player):

    def __init__(self, marker, rows=3, columns=3):
        self.marker = marker
        self.win_log = GameLog(result_type=GameResult.WIN)
        self.loss_log = GameLog(result_type=GameResult.LOSS)
        self.draw_log = GameLog(result_type=GameResult.DRAW)
        self.agent_type = "Human"
        os.environ['PRINT_OUTPUT'] = 'TRUE'

    def makeMove(self, board):
        board.pretty_print_board()
        sel = input("Enter selection, either row, column in tic tac toe or ABCDEFGHI: ")
        sel = sel.strip()
        
        if len(sel) == 1:
            row, col = board.abc_to_row_col(sel)
            while sel.strip() not in board.abc and not board.is_valid_move(row, col):
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

class QLearningPlayer(Player):
    def __init__(self, marker, rows=3, columns=3, random_action_percent=.5):
        super().__init__(marker, rows, columns, random_action_percent)
        self.agent_type = "QLearning"

    def makeMove(self, board):
        board_state_init = board.get_board_state()

        moves, moves_hash = board.get_available_moves(self.marker)

        moves_left = board.moves_left()
        if random() < self.random_action[moves_left]:
            action = self._get_random_move(moves, moves_hash)
            self.random_count[moves_left] += 1
            
            if self.random_count[moves_left] > self.random_action_stages[moves_left]:
                self.random_count[moves_left] = 0
                self.random_action[moves_left] = self.random_action[moves_left] * self.epsilon_decay
            if self.marker == 'X':
                board.random_action = True
            q_move = self._get_best_move(moves, moves_hash)
            # Make pretend move for q
            board_temp = copy.deepcopy(board)
            board_temp.set_tile(q_move[0], q_move[1], self.marker)
            q_score = self.Q[q_move][board_temp.get_board_state()]
            board.set_tile(action[0], action[1], self.marker)
        else:
            action = self._get_best_move(moves, moves_hash)
            board.set_tile(action[0], action[1], self.marker)
            q_score = self.Q[action][board.get_board_state()]

        board_state = board.get_board_state()
        #  Since other player alters state we can't do a look ahead.
        self.update_state(q_score, board, board.get_board_state(), action)


class WifeAgent(Player):
    def __init__(self, marker, rows=3, columns=3, random_action_percent=.5):
        super().__init__(marker, rows, columns, random_action_percent)
        self.agent_type = "WifeSarsa"
        self.current_history = []
        self.action_hash = []
        self.winning_moves = {}

    def makeMove(self, board):
        board_state_init = board.get_board_state()
        if board_state_init in self.winning_moves:
            action = self.winning_moves[board_state_init][0]
        else:

            board_state_init = board.get_board_state()
            moves, moves_hash = board.get_available_moves(self.marker)
    
            moves_left = board.moves_left()
            if random() < self.random_action[moves_left]:
                action = self._get_random_move(moves, moves_hash)
                if self.marker == 'X':
                    board.random_action = True
                self.random_count[moves_left] += 1
                
                if self.random_count[moves_left] > self.random_action_stages[moves_left]:
                    self.random_count[moves_left] = 0
                    self.random_action[moves_left] = self.random_action[moves_left] * self.epsilon_decay
            else:
                action = self._get_best_move(moves, moves_hash)

        board.set_tile(action[0], action[1], self.marker)

        self.update_state(self.Q[action][board.get_board_state()], board, board.get_board_state(), action)
        self.current_history.append((board_state_init, []))
        for i in range(len(self.current_history)):
            self.current_history[i][1].append(action)

    def record_end_of_game(self, board, result, record_random_games):
        super().record_end_of_game(board, result, record_random_games)
        if result == GameResult.WIN:
            for event in self.current_history:
                self.winning_moves[event[0]] = event[1]
        elif result == GameResult.LOSS:
            for event in self.current_history:
                if event[0] in self.winning_moves:
                    del self.winning_moves[event[0]]
        self.current_history = []


    def clear_memory(self):
        self.winning_moves = {}

class ProfessorSarsa(Player):

    def __init__(self, marker, rows=3, columns=3):
        super().__init__(marker, rows, columns)
        self.random_action = [-100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100]
        self.agent_type = "ProfessorSarsa"
        self.history = []

    def re_load_agent(self, pickle_file):
        self.load_q_state(pickle_file)
        self.random_action = [-100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100]
        
 
    def makeMove(self, board_obj):
        move = self.get_move_teacher(board_obj)
        temp =board_obj.get_board_state()
        if board_obj.get_board_state().count("-") > 7:
            self.history = []
        self.history.append((move, copy.deepcopy(board_obj.board)))
        return board_obj.set_tile(move[0], move[1], self.marker)
    
    def get_move_teacher(self, board_obj):
        board = board_obj.board
        board_state_init = board_obj.get_board_state()
        # For now hard code
        mark = "X"
        
        # Check for row across wins
        state = board.check_win_condition(self.marker)
        if state:
            return (state[0], state[1])

        state = self.check_win_condition(board, mark)
        if state:
            return (state[0], state[1])
    
        # Diamond trick
        if board[0][0] == self.marker and board[2][2] == '-':
            return (2, 2)
        if board[0][2] == self.marker and board[2][0] == '-':
            return (2, 0)
        if board[2][2] == self.marker and board[0][0] == '-':
            return (0, 0)
        if board[2][0] == self.marker and board[0][2] == '-':
            return (0, 2)
        
        # Middle move is also a good move
        # if board[1][1] == '-':
        #     return (1, 1)
        
        # Corners are next best
        if board[0][0] == '-':
            return (0, 0)
        if board[0][2] == '-':
            return (0, 2)
        if board[2][2] == '-':
            return (2, 2)
        if board[2][0] == '-':
            return (2, 0)
        
        # No viable move pick random
        moves, moves_hash = board_obj.get_available_moves(self.marker)
        move = choice(moves)
        return (move[0], move[1]) 
    
        