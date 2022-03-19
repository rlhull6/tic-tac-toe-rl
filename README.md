# Tic Tac Toe with Reinforced Machine Learning

Developed by Ryan Hull at University of Oklahoma CS 5033

Run playgame.py to run training and should be the only file needed for tweaking basic functionality.

There are basically 4 different agents supported
 * Sarsa Agent
 * Q-Learning Agent
 * Random Agent
 * Human Agent
 * Recall Agent (Wife agent - Remembers all the mistakes made and tests that the RL agent remembers them and once it does pops them off the state)


Currently support for different agents are driven off code changes but could be added in the future

environment directory contains trained models.

These are agents trained to make the first move
 * q_X_first_player_Q-Learning.pickle
 * q_X_first_player_Sarsa.pickle
Agents trained to make second move
 * q-learning-2nd-move.pickle
 * q-sarsa-2nd-move.pickle
