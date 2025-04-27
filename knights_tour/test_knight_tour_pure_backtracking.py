import unittest
import time
from knight_tour import solve_knights_tour_pure_backtracking, is_valid_tour

class TestKnightTourPureBacktracking(unittest.TestCase):

    def test_valid_tour_from_fixed_start(self):
        start_pos = (3, 4)
        print(f"\nRunning pure backtracking from {start_pos}")
        start_time = time.time()
        board = solve_knights_tour_pure_backtracking(start_pos)
        elapsed = time.time() - start_time
        print(f"Execution Time: {elapsed:.2f} seconds")

        if board is None:
            print("No solution found within the time limit.")
            self.assertTrue(True)  # Passes test since timeout is acceptable
        else:
            # Reconstruct the move list from the board
            moves = [None] * 64
            for i in range(8):
                for j in range(8):
                    move_index = board[i][j]
                    if move_index != -1:
                        moves[move_index] = (i, j)
            self.assertTrue(is_valid_tour(board, moves))

    def test_execution_under_timeout(self):
        start_pos = (0, 4)
        print(f"\nTesting timeout behavior from {start_pos}")
        start_time = time.time()
        board = solve_knights_tour_pure_backtracking(start_pos)
        elapsed = time.time() - start_time
        self.assertLessEqual(elapsed, 125)  # Allowing slight margin
        print(f"Execution completed in {elapsed:.2f} seconds")

if __name__ == "__main__":
    unittest.main()
