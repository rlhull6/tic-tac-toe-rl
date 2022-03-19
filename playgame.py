#################################################
#
#  Ryan Hull (hull0001)
#  CS 5033 Machine Learning 
#  Reinforced Machine Learning Midterm Project
#  Tic Tac Toe
#  March 18, 2022
#################################################


from tic_tac_toe_board import TicTacToeBoard
from player_agent import Player, RandomPlayer, HumanPlayer, QLearningPlayer,\
    WifeAgent, ProfessorSarsa
from game_state import GameResult, print_analysis,\
    update_iterative_history_csv, GameLog
from random import seed, uniform
from os.path import join
import os
import copy
import sys

seed(6)


def playGame(board, player_X, player_O, record_random_games=False, player_X_first=True):
    
    if 'PRINT_OUTPUT' not in os.environ:
        os.environ['PRINT_OUTPUT'] = 'FALSE'
    board_moves = []

    for counts in range(board.col * board.rows):
        board_moves.append(copy.deepcopy(board.board))
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
        if not player_O:
            print("how")
        player_O.makeMove(board)
        if board.find_winner("O") == "O":
            player_X.record_end_of_game(board, GameResult.LOSS, record_random_games)
            player_O.record_end_of_game(board, GameResult.WIN, record_random_games)
            break
        elif board.find_winner("O") == GameResult.DRAW:
            player_X.record_end_of_game(board, GameResult.DRAW, record_random_games)
            player_O.record_end_of_game(board, GameResult.DRAW, record_random_games)
            break

def get_random_agent(q_opponent_environment, marker):
    val = uniform(1, 15)
    if val < 2:
        return False, RandomPlayer(marker)
    elif val < 4:
        player_O = Player(marker)
        player_O.load_q_state(q_opponent_environment)
        return True, player_O
    elif val < 6:
        player_O = QLearningPlayer(marker)
        player_O.load_q_state(q_opponent_environment)
        return True, player_O
    elif val < 8:
        return False, Player(marker, random_action_percent=-1) # always greedy
    elif val < 10:
        return False, QLearningPlayer(marker, random_action_percent=-1)
    elif val < 16:
        return True, WifeAgent(marker)
    else:
        print("val is " + str(val))


def run_game(use_preloaded_Q_values=True, training=False, multi_agent_training=False):
    print("Welcome to Ryan Hull's tic-tac-toe game for Reinforced Learning\n\n" + \
          "A list of available options are as follows:\n" + \
          "   1)  Play first move against a Sarsa RL agent.\n" + \
          "   2)  Play first move against a Q-Learning RL agent.\n" + \
          "   3)  Play second move against a Sarsa RL agent.\n" + \
          "   4)  Play second move against a Q-Learning RL agent.\n" + \
          "   5)  Train Sarsa making the first move.\n" + \
          "   6)  Train Q-Learning making the first move.\n" + \
          "   7)  Train Sarsa making the second move.\n" + \
          "   8)  Train Q-Learning making the second move.\n\n" + \
          "   ***Note more options and configurations are done as part\n" + \
          "   of the code however due to this input prompt being post-development\n" + \
          "   not all possibilities have been added.\n\n" + \
          "   **Second note, training is saved after each iteration so you \n" + \
          "   kill the process whenever and resume as long as you give same filename\n" + \
          "\n")

    sel = input("Enter selection (1-8): ")
    sel = sel.strip()
    
    if sel not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        sys.exit("Invalid command selected please re-run with correct input.")
    
    if sel == "1":
        q_opponent_environment = join(join(os.getcwd(), "environments"), "q_X_first_player_Sarsa.pickle")
        player_X = Player("X")
        player_X_first = True
    elif sel == "2":
        q_opponent_environment = join(join(os.getcwd(), "environments"), "q_X_first_player_Q-Learning.pickle")
        player_X = QLearningPlayer("X")
        player_X_first = True
    elif sel == "3":
        q_opponent_environment = join(join(os.getcwd(), "environments"), "q-sarsa-2nd-move.pickle")
        player_X = Player("X")
        player_X_first = False
    elif sel == "4":
        q_opponent_environment = join(join(os.getcwd(), "environments"), "q-learning-2nd-move.pickle")
        player_X = QLearningPlayer("X")
        player_X_first = False
    #  Training options
    elif sel == "5":
        player_X = Player("X")
        player_X_first = True
    elif sel == "6":
        player_X = QLearningPlayer("X")
        player_X_first = True
    elif sel == "7":
        player_X = Player("X")
        player_X_first = False
    elif sel == "8":
        player_X = QLearningPlayer("X")
        player_X_first = False

    if sel in ["1", "2", "3", "4"]:
        player_X.random_action = [-1 for _ in range(len(player_X.random_action))]
        player_O = HumanPlayer("O")
        training = False
    else:
        sel = input("Enter a filename for the training file: ")
        sel = sel.strip()
        q_opponent_environment = join(join(os.getcwd(), "environments"), sel)
        print("Results will be saved to the pickle file " + str(sel))
        training = True
        player_O = Player("O")
    #     player_O = RandomPlayer("O")
    #     player_O = Player("O")
    #     #player_O = QLearningPlayer("O")
    #     #player_O = WifeAgent("O")
    #     #player_O = HumanPlayer("O")
    #     #player_O = ProfessorSarsa("O")

    agent_environment = join(join(os.getcwd(), "environments"), "agent.pickle")

    trail_win_log = GameLog(result_type=GameResult.WIN)
    trail_loss_log = GameLog(result_type=GameResult.LOSS)
    trail_draw_log = GameLog(result_type=GameResult.DRAW)
    csv_file_trial = None

    loaded_agent= False  # This is only  used when using multi-agents for deciding when to load agents
    csv_file = None      # The csv file for writing results.  Generated based on dates


    if use_preloaded_Q_values:
        player_X.load_q_state(q_opponent_environment)
        player_O.load_q_state(agent_environment)
    
    for _ in range(30000):
        if multi_agent_training:
            loaded_agent, player_O = get_random_agent(q_opponent_environment + player_O.agent_type + ".pickle", marker="O")
        print("\n\nPlaying with Agent: " + player_O.agent_type)
        for _ in range(10000):
            board = TicTacToeBoard()
            playGame(board, player_X, player_O, player_X_first=player_X_first)

        # These are for logging purposes only
        print_analysis(player_X.win_log, player_X.loss_log, player_X.draw_log)
        csv_file = update_iterative_history_csv(player_X.win_log, player_X.loss_log, player_X.draw_log, 
                                                player_X.agent_type, player_O.agent_type, player_X.random_action, csv_file)
        player_X.update_all_counters()
        print("The current random value is " + str(player_X.random_action))
        if training:
            player_X.save_q_state(q_opponent_environment)
        

        if loaded_agent:
            player_O.save_q_state(q_opponent_environment + player_O.agent_type + ".pickle")
        # if training:
        #     player_O.save_q_state(q_opponent_environment + player_O.agent_type + ".pickle")
        
        if player_O.agent_type == 'TeacherSarsa':
            player_O.re_load_agent(agent_environment)
        if player_O.agent_type == "WifeSarsa":
            player_O.clear_memory()
        
        ################################
        # Test out the changes without saving the results to the agent
        ################################
        if training:
            print("\n\n\nRunning Trial....")
            temp_agent = join(join(os.getcwd(), "environments"), "temp.pickle")
            
            # Save Player O Configuration
            player_O.save_q_state(q_opponent_environment)
            old_O_random_actions = player_O.random_action
            
            # Save Player X Configuration
            old_random_actions = player_X.random_action
            player_X.loss_log = trail_loss_log
            player_X.win_log = trail_win_log
            player_X.draw_log = trail_draw_log
            player_X.save_q_state(temp_agent)
            
            #Load Testing Configuration
            player_X.random_action = [-1 for _ in range(len(player_X.random_action))]
            player_O.random_action = [-1 for _ in range(len(player_O.random_action))]
            
            for counts in range(2000):
                board = TicTacToeBoard()
                playGame(board, player_X, player_O)
            csv_file_trial = update_iterative_history_csv(player_X.win_log, player_X.loss_log, player_X.draw_log, 
                                                          player_X.agent_type, player_O.agent_type, player_X.random_action, csv_file_trial)
            print_analysis(player_X.win_log, player_X.loss_log, player_X.draw_log)
            player_X.update_all_counters()
            trail_loss_log = player_X.loss_log
            trail_win_log = player_X.win_log
            trail_draw_log = player_X.draw_log
            # Restore Q values to original before trial
            player_X.load_q_state(temp_agent)
            player_X.random_action = old_random_actions
            player_O.random_action= old_O_random_actions
            player_O.load_q_state(q_opponent_environment)
            print("\n\n")

    print("Done")

run_game()
