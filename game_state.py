from enum import Enum
from datetime import datetime
from os.path import exists, join
import os

class GameResult(Enum):
    LOSS = "Loss"
    WIN = "Win"
    DRAW = "Draw"


class GameLog():

    def __init__(self, actions={}, states={}, result_type=GameResult.DRAW):
        self.actions = actions
        self.states = states
        self.result_type = result_type
        
        # Sum of the number of runs in the current run
        self.game_log_count = 0
        self.previous_count_game_log = 0
        self.total_previous_counts = 0

    def _increment_game_log_count(self):
        self.game_log_count += 1

    def _add_action(self, action):
        if action not in self.actions:
            self.actions[action] = 0
        self.actions[action] += 1
        
    def _add_state(self, state):
        if state not in self.states:
            self.states[state] = 0
        self.states[state] += 1

    def update_all_attributes(self, action, state):
        # self.previous_count = 0 if not action else len(action)
        self._add_action(action)
        self._add_state(state)
        self._increment_game_log_count()

    '''
    This should only be called when loading Q object from pickle file to run more runs for comparison.
    '''
    def update_game_counters(self):
        self.previous_count_game_log = self.game_log_count
        self.total_previous_counts += self.game_log_count
        self.game_log_count = 0

    def print_analysis(self, num_to_display=5):
        sorted_actions = {k: v for k, v in sorted(self.actions.items(), key=lambda item: item[1], reverse=True)}
        sorted_states = {k: v for k, v in sorted(self.states.items(), key=lambda item: item[1], reverse=True)}

        print("Top action counts: ")
        i = 1
        for k, v in sorted_actions.items():
            print(f"{k}: {str(v)}")
            if i > num_to_display:
                break
            i+=1
        i = 1
        print("Top states counts: ")
        for k, v in sorted_states.items():
            print(f"{k}: {str(v)}")
            if i > num_to_display:
                break
            i+=1

def print_analysis(win_log, loss_log, draw_log):

    total_previous_count = win_log.total_previous_counts + loss_log.total_previous_counts + draw_log.total_previous_counts
    total_current_count = win_log.game_log_count + loss_log.game_log_count + draw_log.game_log_count
    new_wins = win_log.game_log_count - win_log.previous_count_game_log
    new_losses = loss_log.game_log_count - loss_log.previous_count_game_log
    new_draws = draw_log.game_log_count - draw_log.previous_count_game_log
    

    print(f"Analyzed {str(total_previous_count)} total games for learning and added {str(total_current_count)} games.")
    print(f"Total wins: {str(win_log.game_log_count)}  losses: {str(loss_log.game_log_count)} draws: {str(draw_log.game_log_count)}")
    print(f"Previous wins: {str(win_log.previous_count_game_log)}  losses: {str(loss_log.previous_count_game_log)} draws: {str(draw_log.previous_count_game_log)}")

    if win_log.previous_count_game_log != 0:
        print(f"Rate of change for wins: {str(round(new_wins/win_log.previous_count_game_log * 100, 2))}%")
    if loss_log.previous_count_game_log != 0:
        print(f"Rate of change for loss: {str(round(new_losses/loss_log.previous_count_game_log * 100, 2))}%")
    if draw_log.previous_count_game_log != 0:
        print(f"Rate of change for draw: {str(round(new_draws/draw_log.previous_count_game_log * 100, 2))}%")

    win_log.print_analysis()


def update_iterative_history_csv(win_log, loss_log, draw_log, csv_file=join(os.getcwd(), join("output", datetime.now().strftime("%d_%m_%Y_%H-%M-%S_history.csv")))):
    if not csv_file:
        csv_file = join(os.getcwd(), join("output", datetime.now().strftime("%d_%m_%Y_%H-%M-%S_history.csv")))
    total_previous_count = win_log.total_previous_counts + loss_log.total_previous_counts + draw_log.total_previous_counts
    total_current_count = win_log.game_log_count + loss_log.game_log_count + draw_log.game_log_count
    
    if win_log.previous_count_game_log != 0:
        win_roc = round((win_log.game_log_count -  win_log.previous_count_game_log)/win_log.previous_count_game_log * 100, 2)
    else:
        win_roc = 0
    if loss_log.previous_count_game_log != 0:
        loss_roc = round((loss_log.game_log_count -  loss_log.previous_count_game_log)/loss_log.previous_count_game_log * 100, 2)
    else:
        loss_roc = 0
    if draw_log.previous_count_game_log != 0:
        draw_roc = round((draw_log.game_log_count -  draw_log.previous_count_game_log)/draw_log.previous_count_game_log * 100, 2)
    else:
        draw_roc = 0

    if not exists(csv_file):
        with open(csv_file, "w") as f:
            f.write("TotalGames,GameCount,wins,losses,draw,win_roc,loss_roc,daw_roc\n")
    
    with open(csv_file, "a") as f:
        f.write(str(total_previous_count) + "," + str(total_current_count) + "," + str(win_log.game_log_count) + "," +
                str(loss_log.game_log_count) + "," + str(draw_log.game_log_count) + "," + str(win_roc) + "," + str(loss_roc) + "," + str(draw_roc) + "\n")
    return csv_file
    
    