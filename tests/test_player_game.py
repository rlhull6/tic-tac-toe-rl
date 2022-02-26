from unittest.mock import patch
import unittest
from unittest import mock
from player_agent import Player, RandomPlayer
from tic_tac_toe_board import TicTacToeBoard
from playgame import playGame

class BoardTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_best_move(self, *args):
        board = TicTacToeBoard()
        player_X = Player("X")
        player_O_Random = RandomPlayer("O")
        playGame(board, player_X, player_O_Random, 0)
        print(board)
        
        board = TicTacToeBoard()
        playGame(board, player_X, player_O_Random, 1)

        board = TicTacToeBoard()
        playGame(board, player_X, player_O_Random, 2)

        board = TicTacToeBoard()
        playGame(board, player_X, player_O_Random, 3)