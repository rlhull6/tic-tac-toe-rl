from unittest.mock import patch
import unittest
from unittest import mock
from rh183tictactoe.player_agent import Player
from rh183tictactoe.tic_tac_toe_board import TicTacToeBoard
from random import random, seed, choice

seed(6)

class BoardTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_best_move(self, *args):
        player = Player("X")
        moves_hash = ['X--------', '-X-------', '--X------', '---X-----', '----X----', '-----X---', '------X--', '-------X-', '--------X']
        moves = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        res = player._get_best_move(moves, moves_hash)
        self.assertEqual(res, (0, 0)) # random seed of 6 guarantees this
    
        # Win for arbitrary action
        ind = 2
        player.Q[moves[ind]][moves_hash[ind]] = 1
        res = player._get_best_move(moves, moves_hash)
        self.assertEqual(res, moves[ind])


    def test_get_available_moves(self, *args):
        player = Player("X")
        board = TicTacToeBoard()
        player.makeMove(board)
        self.assertEqual(board.get_board_state(), "-X-------")
        #
        # # Simulate random player
        # board.set_tile(0, 0, "O")
        # player.makeMove(board)
        # self.assertEqual(board.get_board_state(), "OX---X---")

        # Setup board for a win for player X
        board.board = [['X','O','X'], ['O','X','O'], ['X','O','-']]
        player.makeMove(board)
        self.assertEqual(board.get_board_state(), "XOXOXOXOX")
        
        
        
        
