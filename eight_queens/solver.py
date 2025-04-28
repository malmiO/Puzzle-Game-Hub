import time
import threading
from db import save_to_db, solution_exists  # Assuming save_to_db is modified to work with MySQL

# Helper function to check if placing a queen is safe
def is_safe(board, row, col):
    """
    Check if placing a queen at position (row, col) is safe.
    A position is safe if no other queen threatens it in the same column or diagonal.
    """
    for i in range(row):
        if board[i] == col or \
           board[i] - i == col - row or \
           board[i] + i == col + row:
            return False
    return True

# Recursive function to solve the n-queens puzzle
def solve_n_queens(board, row, solutions):
    """
    Recursive backtracking function to solve the N-Queens problem.
    Adds a solution to the list once a valid configuration is found.
    """
    if row == 8:  # All queens are placed, save the solution
        solutions.append(board[:])
        return
    for col in range(8):
        if is_safe(board, row, col):
            board[row] = col  # Place queen at (row, col)
            solve_n_queens(board, row + 1, solutions)  # Recurse for the next row

# Sequential solver
def sequential_solver():
    """
    Solves the N-Queens problem sequentially (without threads).
    This method performs the solution search one step at a time.
    """
    try:
        if solution_exists("Sequential"):  # Check if the sequential solution already exists in the database
            return None, None  # Return None, None to indicate that results already exist

        solutions = []  # List to store all valid solutions
        board = [-1] * 8  # Initialize the board with no queens placed
        start_time = time.time()  # Start the timer to calculate execution time
        solve_n_queens(board, 0, solutions)  # Start solving the N-Queens problem
        end_time = time.time()  # End the timer after solving

        time_taken = end_time - start_time  # Calculate the time taken to solve the problem
        save_to_db("Sequential", time_taken, solutions)  # Save results to the database
        return time_taken, solutions
    except Exception as e:
        print(f"Error in sequential solver: {e}")
        return None, None

# Threaded solver
def threaded_solver():
    """
    Solves the N-Queens problem using threading (parallel processing).
    Each thread solves a different portion of the problem.
    """
    try:
        if solution_exists("Threaded"):  # Check if the threaded solution already exists in the database
            return None, None  # Return None, None to indicate that results already exist

        solutions = []  # List to store all valid solutions
        board = [-1] * 8  # Initialize the board with no queens placed
        start_time = time.time()  # Start the timer to calculate execution time

        # Thread function to solve a portion of the problem from a given starting row
        def thread_solve(row_start):
            local_solutions = []  # Local list of solutions for this thread
            solve_n_queens(board, row_start, local_solutions)  # Solve for the given starting row
            solutions.extend(local_solutions)  # Add the local solutions to the global list

        threads = []  # List to keep track of the threads
        for i in range(8):  # We spawn 8 threads, each solving a different part of the problem
            thread = threading.Thread(target=thread_solve, args=(i,))  # Start solving from row i
            threads.append(thread)  # Add thread to the list
            thread.start()  # Start the thread

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        end_time = time.time()  # End the timer after all threads are done
        time_taken = end_time - start_time  # Calculate the time taken to solve the problem
        save_to_db("Threaded", time_taken, solutions)  # Save results to the database
        return time_taken, solutions
    except Exception as e:
        print(f"Error in threaded solver: {e}")
        return None, None
