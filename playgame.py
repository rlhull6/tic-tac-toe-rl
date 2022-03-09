from tic_tac_toe_board import TicTacToeBoard
from player_agent import Player, RandomPlayer, HumanPlayer, QLearningPlayer,\
    TeacherSarsa
from game_state import GameResult, print_analysis,\
    update_iterative_history_csv
from random import seed
from os.path import join
import os

seed(6)


def playGame(board, player_X, player_O, record_random_games=False, player_X_first=True):
    
    if 'PRINT_OUTPUT' not in os.environ:
        os.environ['PRINT_OUTPUT'] = 'FALSE'

    for counts in range(board.col * board.rows):
        if counts ==3:
            print("here")
        if player_X_first:
            player_X.makeMove(board)
        
            if board.find_winner("X") == "X":
                player_X.record_end_of_game(board, GameResult.WIN, record_random_games)
                player_O.record_end_of_game(board, GameResult.LOSS, record_random_games)
                break
            elif board.find_winner("X") == GameResult.DRAW:
                player_X.record_end_of_game(board, GameResult.DRAW, record_random_games)
                player_O.record_end_of_game(board, GameResult.DRAW, record_random_games)
                break
        else:
            player_X_first = True

        player_O.makeMove(board)
        if board.find_winner("O") == "O":
            player_X.record_end_of_game(board, GameResult.LOSS, record_random_games)
            player_O.record_end_of_game(board, GameResult.WIN, record_random_games)
            break
        elif board.find_winner("O") == GameResult.DRAW:
            player_X.record_end_of_game(board, GameResult.DRAW, record_random_games)
            player_O.record_end_of_game(board, GameResult.DRAW, record_random_games)
            break


def run_game(use_preloaded_Q_values=True, random_agent=False):
    q_environment = join(join(os.getcwd(), "environments"), "q.pickle")
    q_opponent_environment = join(join(os.getcwd(), "environments"), "q_opponent.pickle")
    
    csv_file = None
    #player_X = Player("X")
    player_X = QLearningPlayer("X")

    if random_agent:
        player_O = RandomPlayer("O")
    else:
        #player_O = Player("O")
        #player_O = HumanPlayer("O")
        player_O = TeacherSarsa("O")
        
    if use_preloaded_Q_values:
        player_X.load_q_state(q_environment)
        player_O.load_q_state(q_opponent_environment)
    
    for _ in range(200000):
        for counts in range(500):
            board = TicTacToeBoard()
            playGame(board, player_X, player_O)

        # These are for logging purposes only
        print_analysis(player_X.win_log, player_X.loss_log, player_X.draw_log)
        csv_file = update_iterative_history_csv(player_X.win_log, player_X.loss_log, player_X.draw_log, 
                                                player_X.agent_type, player_O.agent_type, player_X.random_action, csv_file)
        player_X.update_all_counters()
        print("The current random value is " + str(player_X.random_action))
        player_X.save_q_state(q_environment)
        #player_O.save_q_state(q_opponent_environment)
        
        if player_O.agent_type == 'TeacherSarsa':
            player_O.re_load_agent(q_environment)
        
    print("Done")

run_game()