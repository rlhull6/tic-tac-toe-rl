import pickle
from os.path import join
import os


def load_q_state(pickle_file):
    with open(pickle_file, "rb") as f:
        pickle_list = pickle.load(f)
        return pickle_list[0]


new_q_opponent_env = join(os.getcwd(), "q_sarsa_trained_making_2nd_move.pickle")
q = load_q_state(new_q_opponent_env)

new_q = {}

for action, v in q.items():
    new_q[action] = {}
    for state, value in v.items():
        state = state.replace("O", "M") # arbitrary value
        state = state.replace("X", "O")
        state = state.replace("M", "X")

        new_q[action][state] = value

new_swapped_q = join(os.getcwd(), "swapped_q.pickle")

with open(new_swapped_q, "wb") as fw:
    with open(new_q_opponent_env, "rb") as f:
        pickle_list = pickle.load(f)
        pickle_list[0] = new_q
        
        pickle.dump(pickle_list, fw)