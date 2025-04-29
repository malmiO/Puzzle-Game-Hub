import unittest
from unittest.mock import patch
from solver import sequential_solver, threaded_solver

class TestNQueensSolvers(unittest.TestCase):

    @patch('solver.save_to_db')
    def test_sequential_solver(self, mock_save_to_db):
        time_taken, solutions = sequential_solver()

        # Check time_taken is a float and positive
        self.assertIsInstance(time_taken, float)
        self.assertGreater(time_taken, 0)

        # Check solutions is a non-empty list
        self.assertIsInstance(solutions, list)
        self.assertTrue(len(solutions) > 0)

        # For 8-Queens, there should be exactly 92 solutions
        self.assertEqual(len(solutions), 92)

    @patch('solver.save_to_db')
    def test_threaded_solver(self, mock_save_to_db):
        time_taken, solutions = threaded_solver()

        # Check time_taken is a float and positive
        self.assertIsInstance(time_taken, float)
        self.assertGreater(time_taken, 0)

        # Check solutions is a non-empty list
        self.assertIsInstance(solutions, list)
        self.assertTrue(len(solutions) > 0)

        # For 8-Queens, there should be exactly 92 solutions
        self.assertEqual(len(solutions), 92)

if __name__ == '__main__':
    unittest.main()
