import numpy as np
import heapq
from typing import Tuple, Optional

class GreedyAl:
    def __init__(self, board: np.ndarray, player: str):
        try:
            self.board = board
            self.player = player
            self.opponent = 'X' if player == 'O' else 'O'
        except Exception as e:
            raise ValueError(f"Error initializing GreedyAl: {e}")

    def evaluate_move(self, x: int, y: int) -> int:
        try:
            if self.board[x][y] != ' ':
                return -1000
            score = 0
            temp_board = self.board.copy()
            temp_board[x][y] = self.player
            if self.check_winner(temp_board, self.player):
                score += 100
            temp_board[x][y] = self.opponent
            if self.check_winner(temp_board, self.opponent):
                score += 50
            if x in [1, 2, 3] and y in [1, 2, 3]:
                score += 10
            return score
        except IndexError as e:
            return -1000  # Invalid coordinates
        except Exception as e:
            raise ValueError(f"Error evaluating move: {e}")

    def check_winner(self, board: np.ndarray, player: str) -> bool:
        try:
            for i in range(5):
                if all(board[i][j] == player for j in range(5)):
                    return True
            for j in range(5):
                if all(board[i][j] == player for i in range(5)):
                    return True
            if all(board[i][i] == player for i in range(5)):
                return True
            if all(board[i][4-i] == player for i in range(5)):
                return True
            return False
        except IndexError as e:
            raise ValueError(f"Error checking winner: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error checking winner: {e}")

    def get_move_with_score(self) -> Tuple[Optional[Tuple[int, int]], int]:
        try:
            heap = []
            for i in range(5):
                for j in range(5):
                    if self.board[i][j] == ' ':
                        score = self.evaluate_move(i, j)
                        heapq.heappush(heap, (-score, i, j))
            if heap:
                neg_score, x, y = heapq.heappop(heap)
                return (x, y), -neg_score
            return None, 0
        except Exception as e:
            raise ValueError(f"Error getting move with score: {e}")

class MinimaxAl:
    def __init__(self, board: np.ndarray, player: str):
        try:
            self.board = board
            self.player = player
            self.opponent = 'X' if player == 'O' else 'O'
            self.max_depth = 3
        except Exception as e:
            raise ValueError(f"Error initializing MinimaxAl: {e}")

    def evaluate(self, board: np.ndarray) -> int:
        try:
            if self.check_winner(board, self.player):
                return 10
            if self.check_winner(board, self.opponent):
                return -10
            return 0
        except Exception as e:
            raise ValueError(f"Error evaluating board: {e}")

    def check_winner(self, board: np.ndarray, player: str) -> bool:
        try:
            for i in range(5):
                if all(board[i][j] == player for j in range(5)):
                    return True
            for j in range(5):
                if all(board[i][j] == player for i in range(5)):
                    return True
            if all(board[i][i] == player for i in range(5)):
                return True
            if all(board[i][4-i] == player for i in range(5)):
                return True
            return False
        except IndexError as e:
            raise ValueError(f"Error checking winner: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error checking winner: {e}")

    def minimax(self, board: np.ndarray, depth: int, alpha: float, beta: float, is_max: bool) -> int:
        try:
            score = self.evaluate(board)
            if score != 0:
                return score - depth
            if depth >= self.max_depth:
                return 0
            if all(board[i][j] != ' ' for i in range(5) for j in range(5)):
                return 0

            if is_max:
                best = -float('inf')
                for i in range(5):
                    for j in range(5):
                        if board[i][j] == ' ':
                            board[i][j] = self.player
                            best = max(best, self.minimax(board, depth + 1, alpha, beta, False))
                            board[i][j] = ' '
                            alpha = max(alpha, best)
                            if beta <= alpha:
                                break
                return best
            else:
                best = float('inf')
                for i in range(5):
                    for j in range(5):
                        if board[i][j] == ' ':
                            board[i][j] = self.opponent
                            best = min(best, self.minimax(board, depth + 1, alpha, beta, True))
                            board[i][j] = ' '
                            beta = min(beta, best)
                            if beta <= alpha:
                                break
                return best
        except Exception as e:
            raise ValueError(f"Error in minimax algorithm: {e}")

    def get_move_with_score(self) -> Tuple[Optional[Tuple[int, int]], int]:
        try:
            best_val = -float('inf')
            best_move = None
            for i in range(5):
                for j in range(5):
                    if self.board[i][j] == ' ':
                        self.board[i][j] = self.player
                        move_val = self.minimax(self.board, 0, -float('inf'), float('inf'), False)
                        self.board[i][j] = ' '
                        if move_val > best_val:
                            best_move = (i, j)
                            best_val = move_val
            return best_move, best_val
        except Exception as e:
            raise ValueError(f"Error getting move with score: {e}")