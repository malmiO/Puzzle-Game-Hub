import unittest
import numpy as np
from algorithms import GreedyAl, MinimaxAl

class TestTicTacToeAlgorithms(unittest.TestCase):
    def setUp(self):
        # Initialize a 5x5 empty board
        self.board = np.array([[' ' for _ in range(5)] for _ in range(5)])
        self.player = 'X'
        self.opponent = 'O'

    def test_greedy_al_initialization(self):
        # Test GreedyAl initialization
        greedy = GreedyAl(self.board, self.player)
        self.assertEqual(greedy.player, 'X')
        self.assertEqual(greedy.opponent, 'O')
        self.assertTrue(np.array_equal(greedy.board, self.board))

    def test_greedy_evaluate_move_invalid(self):
        # Test GreedyAl evaluate_move with an occupied cell
        greedy = GreedyAl(self.board, self.player)
        self.board[0][0] = 'X'
        score = greedy.evaluate_move(0, 0)
        self.assertEqual(score, -1000)

    def test_greedy_evaluate_move_winning(self):
        # Test GreedyAl evaluate_move for a winning move
        greedy = GreedyAl(self.board, self.player)
        # Set up a board where X can win in the first row
        self.board[0] = ['X', 'X', 'X', 'X', ' ']
        score = greedy.evaluate_move(0, 4)
        self.assertEqual(score, 100)  # Should score high for winning move

    def test_greedy_get_move_empty_board(self):
        # Test GreedyAl get_move_with_score on an empty board
        greedy = GreedyAl(self.board, self.player)
        move, score = greedy.get_move_with_score()
        self.assertIsNotNone(move)
        self.assertIn(move[0], [1, 2, 3])  # Should prefer center cells
        self.assertIn(move[1], [1, 2, 3])
        self.assertEqual(score, 10)  # Center cell score

    def test_minimax_al_initialization(self):
        # Test MinimaxAl initialization
        minimax = MinimaxAl(self.board, self.player)
        self.assertEqual(minimax.player, 'X')
        self.assertEqual(minimax.opponent, 'O')
        self.assertTrue(np.array_equal(minimax.board, self.board))
        self.assertEqual(minimax.max_depth, 3)

    def test_minimax_evaluate_winning(self):
        # Test MinimaxAl evaluate for a winning board
        minimax = MinimaxAl(self.board, self.player)
        self.board[0] = ['X', 'X', 'X', 'X', 'X']  # X wins in first row
        score = minimax.evaluate(self.board)
        self.assertEqual(score, 10)  # Positive score for player's win

    def test_minimax_evaluate_losing(self):
        # Test MinimaxAl evaluate for a losing board
        minimax = MinimaxAl(self.board, self.player)
        self.board[0] = ['O', 'O', 'O', 'O', 'O']  # O wins in first row
        score = minimax.evaluate(self.board)
        self.assertEqual(score, -10)  # Negative score for opponent's win

    def test_minimax_get_move_empty_board(self):
        # Test MinimaxAl get_move_with_score on an empty board
        minimax = MinimaxAl(self.board, self.player)
        move, score = minimax.get_move_with_score()
        self.assertIsNotNone(move)
        self.assertIn(move[0], range(5))
        self.assertIn(move[1], range(5))
        self.assertIsInstance(score, int)

    def test_check_winner_diagonal(self):
        # Test check_winner for a diagonal win
        greedy = GreedyAl(self.board, self.player)
        self.board[0][0] = 'X'
        self.board[1][1] = 'X'
        self.board[2][2] = 'X'
        self.board[3][3] = 'X'
        self.board[4][4] = 'X'
        self.assertTrue(greedy.check_winner(self.board, 'X'))

    def test_check_winner_no_winner(self):
        # Test check_winner with no winner
        greedy = GreedyAl(self.board, self.player)
        self.assertFalse(greedy.check_winner(self.board, 'X'))
        self.assertFalse(greedy.check_winner(self.board, 'O'))

if __name__ == '__main__':
    unittest.main()