from tic_tac_toe_board import TicTacToeBoard
from player_agent import Player, RandomPlayer
from game_state import GameResult, print_analysis,\
    update_iterative_history_csv
from random import seed
from os.path import join
import os

seed(6)


def playGame(board, player_X, player_O, round):
    
    if 'PRINT_OUTPUT' not in os.environ:
        os.environ['PRINT_OUTPUT'] = 'FALSE'

    for i in range(board.col * board.rows):
        if os.environ['PRINT_OUTPUT'] == 'TRUE':
            print(board.get_board_state())
            if board.get_board_state() == "OO-X---X-":
                print(board.get_board_state())
        player_X.makeMove(board)

        if board.find_winner("X") == "X":
            player_X.record_end_of_game(board, GameResult.WIN)
            player_O.record_end_of_game(board, GameResult.LOSS)
            break
        elif board.find_winner("X") == GameResult.DRAW:
            player_X.record_end_of_game(board, GameResult.DRAW)
            player_O.record_end_of_game(board, GameResult.DRAW)
            break

        player_O.makeMove(board)
        if board.find_winner("O") == "O":
            player_X.record_end_of_game(board, GameResult.LOSS)
            player_O.record_end_of_game(board, GameResult.WIN)
            break
        elif board.find_winner("O") == GameResult.DRAW:
            player_X.record_end_of_game(board, GameResult.DRAW)
            player_O.record_end_of_game(board, GameResult.DRAW)
            break


def run_game(use_preloaded_Q_values=False, random_agent=False):
    q_environment = join(join(os.getcwd(), "environments"), "q.pickle")
    q_opponent_environment = join(join(os.getcwd(), "environments"), "q_opponent.pickle")
    
    csv_file = None
    player_X = Player("X")

    if random_agent:
        player_O = RandomPlayer("O")
    else:
        player_O = Player("O")
    if use_preloaded_Q_values:
        player_X.load_q_state(q_environment)
        player_O.load_q_state(q_opponent_environment)
    
    for _ in range(10):        
        for i in range(2000):
            board = TicTacToeBoard()
            playGame(board, player_X, player_O, i)

        # These are for logging purposes only
        print_analysis(player_X.win_log, player_X.loss_log, player_X.draw_log)
        csv_file = update_iterative_history_csv(player_X.win_log, player_X.loss_log, player_X.draw_log, csv_file)
        player_X.update_all_counters()

    player_X.save_q_state(q_environment)
    print("Done")

run_game()