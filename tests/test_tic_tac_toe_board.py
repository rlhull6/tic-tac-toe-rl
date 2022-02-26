from unittest.mock import patch
import unittest
from unittest import mock
from tic_tac_toe_board import TicTacToeBoard
from random import random, seed, choice

seed(6)

class BoardTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_available_moves(self, *args):
        board = TicTacToeBoard()
        self.assertEqual(board.col, 3)
        self.assertEqual(board.rows, 3)
        x = board.get_available_moves("X")
        self.assertEqual(len(board.get_available_moves("X")[0]), 9)
        self.assertEqual(x[1][0], 'X--------')
        self.assertEqual(x[1][1], '-X-------')
        self.assertEqual(x[1][8], '--------X')
        
    def test_find_winner(self, *args):
        board = TicTacToeBoard()
        board.board = [['O','O','X'], ['X','X','X'], ['X','O','O']]
        self.assertEqual(board.find_winner("X"), "X")
        
        board.board = [['X','O','X'], ['X','O','X'], ['X','O','O']]
        self.assertEqual(board.find_winner("X"), "X")
        
        board.board = [['X','O','X'], ['O','X','O'], ['O','O','X']]
        self.assertEqual(board.find_winner("X"), "X")
        
        board.board = [['X','O','X'], ['O','X','O'], ['O','O','-']]
        self.assertEqual(board.find_winner("X"), None)
        
        board.board = [['X','O','X'], ['O','X','O'], ['X','O','O']]
        self.assertEqual(board.find_winner("X"), "X")
        
        board.board = [['X','O','O'], ['O','X','X'], ['X','O','O']]
        self.assertEqual(board.find_winner("X").value, "Draw")

