import random
import time

def is_valid_move(current_pos, next_pos, board):
    """Check if the move is valid for a knight."""
    try:
        row_diff = abs(current_pos[0] - next_pos[0])
        col_diff = abs(current_pos[1] - next_pos[1])
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            return 0 <= next_pos[0] < 8 and 0 <= next_pos[1] < 8
        return False
    except (IndexError, TypeError) as e:
        print(f"Error in is_valid_move: {e}")
        return False

def is_valid_tour(board, moves):
    """Check if the tour is valid."""
    try:
        if len(moves) != 64:
            return False
        visited = set()
        for i in range(8):
            for j in range(8):
                if board[i][j] != -1:
                    visited.add((i, j))
        if len(visited) != 64:
            return False
        for i in range(len(moves) - 1):
            if not is_valid_move(moves[i], moves[i + 1], board):
                return False
        return True
    except (IndexError, TypeError) as e:
        print(f"Error in is_valid_tour: {e}")
        return False

def get_valid_moves(pos, board):
    """Get all valid moves from the current position."""
    try:
        moves = [
            (pos[0] + 2, pos[1] + 1), (pos[0] + 2, pos[1] - 1),
            (pos[0] - 2, pos[1] + 1), (pos[0] - 2, pos[1] - 1),
            (pos[0] + 1, pos[1] + 2), (pos[0] + 1, pos[1] - 2),
            (pos[0] - 1, pos[1] + 2), (pos[0] - 1, pos[1] - 2)
        ]
        return [move for move in moves if 0 <= move[0] < 8 and 0 <= move[1] < 8 and board[move[0]][move[1]] == -1]
    except (IndexError, TypeError) as e:
        print(f"Error in get_valid_moves: {e}")
        return []

def get_degree(pos, board):
    """Get the number of unvisited neighbors for Warnsdorff’s algorithm."""
    try:
        return len(get_valid_moves(pos, board))
    except Exception as e:
        print(f"Error in get_degree: {e}")
        return 0

def solve_knights_tour_backtracking(start_pos):
    """Solve Knight's Tour using optimized backtracking with a timeout."""
    try:
        board = [[-1 for _ in range(8)] for _ in range(8)]
        board[start_pos[0]][start_pos[1]] = 0
        moves = [start_pos]
        start_time = time.time()
        timeout = 20  # seconds
        print(f"Starting Optimized Backtracking from {start_pos} at {time.ctime()}")

        def is_corner_or_edge(pos):
            try:
                r, c = pos
                return (r in [0, 7] and c in [0, 7]) or (r in [0, 7] or c in [0, 7])
            except (IndexError, TypeError):
                return False

        def backtrack(pos, move_count):
            try:
                if time.time() - start_time > timeout:
                    print(f"Optimized Backtracking timed out after {time.time() - start_time:.2f} seconds")
                    return False
                if move_count == 64:
                    return True
                valid_moves = get_valid_moves(pos, board)
                valid_moves.sort(key=lambda move: (get_degree(move, board), -is_corner_or_edge(move)))
                for next_pos in valid_moves:
                    board[next_pos[0]][next_pos[1]] = move_count
                    moves.append(next_pos)
                    if backtrack(next_pos, move_count + 1):
                        return True
                    board[next_pos[0]][next_pos[1]] = -1
                    moves.pop()
                return False
            except Exception as e:
                print(f"Error in backtrack: {e}")
                return False

        if backtrack(start_pos, 1):
            print(f"Optimized Backtracking solution found in {time.time() - start_time:.2f} seconds")
            return board
        print(f"Optimized Backtracking failed in {time.time() - start_time:.2f} seconds")
        return None
    except Exception as e:
        print(f"Error in solve_knights_tour_backtracking: {e}")
        return None

def solve_knights_tour_warnsdorff(start_pos):
    """Solve Knight's Tour using Warnsdorff’s algorithm."""
    try:
        board = [[-1 for _ in range(8)] for _ in range(8)]
        board[start_pos[0]][start_pos[1]] = 0
        current_pos = start_pos
        start_time = time.time()
        print(f"Starting Warnsdorff from {start_pos} at {time.ctime()}")

        for move_count in range(1, 64):
            valid_moves = get_valid_moves(current_pos, board)
            if not valid_moves:
                print(f"Warnsdorff failed after {time.time() - start_time:.2f} seconds")
                return None
            min_degree = float('inf')
            next_pos = None
            for move in valid_moves:
                degree = get_degree(move, board)
                if degree < min_degree:
                    min_degree = degree
                    next_pos = move
                elif degree == min_degree and random.random() < 0.5:
                    next_pos = move
            if not next_pos:
                print(f"Warnsdorff failed after {time.time() - start_time:.2f} seconds")
                return None
            board[next_pos[0]][next_pos[1]] = move_count
            current_pos = next_pos

        print(f"Warnsdorff solution found in {time.time() - start_time:.2f} seconds")
        return board
    except Exception as e:
        print(f"Error in solve_knights_tour_warnsdorff: {e}")
        return None

def solve_knights_tour_pure_backtracking(start_pos):
    """Solve Knight's Tour using pure backtracking with a 2-minute timeout."""
    try:
        board = [[-1 for _ in range(8)] for _ in range(8)]
        board[start_pos[0]][start_pos[1]] = 0
        start_time = time.time()
        timeout = 60  # 1 minute
        print(f"Starting Pure Backtracking from {start_pos} at {time.ctime()}")

        def backtrack(pos, move_count):
            try:
                if time.time() - start_time > timeout:
                    print(f"Pure Backtracking timed out after {time.time() - start_time:.2f} seconds")
                    return False
                if move_count == 64:
                    return True
                for next_pos in get_valid_moves(pos, board):
                    board[next_pos[0]][next_pos[1]] = move_count
                    if backtrack(next_pos, move_count + 1):
                        return True
                    board[next_pos[0]][next_pos[1]] = -1
                return False
            except Exception as e:
                print(f"Error in backtrack: {e}")
                return False

        if backtrack(start_pos, 1):
            print(f"Pure Backtracking solution found in {time.time() - start_time:.2f} seconds")
            return board
        print(f"Pure Backtracking failed in {time.time() - start_time:.2f} seconds")
        return None
    except Exception as e:
        print(f"Error in solve_knights_tour_pure_backtracking: {e}")
        return None