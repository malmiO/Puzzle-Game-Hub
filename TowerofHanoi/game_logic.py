# Initialize game state
def init_game_state(n):
    return {
        'A': list(range(n, 0, -1)),
        'B': [],
        'C': [],
        'D': []
    }

# Validate a move
def is_valid_move(state, source, destination):
    if not state[source]:
        return False
    if not state[destination]:
        return True
    return state[source][-1] < state[destination][-1]

# Apply a move
def apply_move(state, source, destination):
    if is_valid_move(state, source, destination):
        disk = state[source].pop()
        state[destination].append(disk)
        return True
    return False

# Check if the game is solved
def is_solved(state, n, destination='C'):
    return len(state[destination]) == n and sorted(state[destination], reverse=True) == state[destination]