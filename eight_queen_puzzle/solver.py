import time
import threading
from db import save_to_db

class SolverError(Exception):
    """Custom exception class for solver-specific errors."""
    pass

def is_safe(board, row, col):
    """
    Check if placing a queen at position (row, col) is safe.
    """
    if not isinstance(board, list) or not isinstance(row, int) or not isinstance(col, int):
        raise ValueError("Invalid input types to is_safe().")

    if row < 0 or row >= 8 or col < 0 or col >= 8:
        raise ValueError(f"Row and column must be between 0 and 7. Got row={row}, col={col}.")

    for i in range(row):
        if board[i] == col or \
           board[i] - i == col - row or \
           board[i] + i == col + row:
            return False
    return True

def solve_n_queens(board, row, solutions):
    """
    Recursive backtracking function to solve the N-Queens problem.
    """
    if not isinstance(board, list) or not isinstance(row, int) or not isinstance(solutions, list):
        raise ValueError("Invalid arguments passed to solve_n_queens.")

    if row == 8:
        solutions.append(board[:])
        return

    for col in range(8):
        if is_safe(board, row, col):
            board[row] = col
            solve_n_queens(board, row + 1, solutions)

def sequential_solver():
    """
    Solves the N-Queens problem sequentially and saves the result to the database.
    """
    try:
        solutions = []
        board = [-1] * 8
        start_time = time.time()
        solve_n_queens(board, 0, solutions)
        end_time = time.time()

        time_taken = end_time - start_time

        if not solutions:
            raise SolverError("Sequential solver found no solutions.")

        save_to_db("Sequential", time_taken, solutions)
        return time_taken, solutions

    except Exception as e:
        print(f"Error in sequential_solver: {e}")
        return None, None

def threaded_solver():
    """
    Solves the N-Queens problem using multiple threads and saves the result to the database.
    """
    try:
        solutions = []
        lock = threading.Lock()
        threads = []

        def thread_solve(start_col):
            local_board = [-1] * 8
            local_solutions = []

            if is_safe(local_board, 0, start_col):
                local_board[0] = start_col
                solve_n_queens(local_board, 1, local_solutions)

                with lock:
                    solutions.extend(local_solutions)

        start_time = time.time()

        for col in range(8):
            thread = threading.Thread(target=thread_solve, args=(col,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        time_taken = end_time - start_time

        if not solutions:
            raise SolverError("Threaded solver found no solutions.")

        save_to_db("Threaded", time_taken, solutions)
        return time_taken, solutions

    except Exception as e:
        print(f"Error in threaded_solver: {e}")
        return None, None
