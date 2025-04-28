import streamlit as st
import time

def init_game_state(force=False):
    if "board" not in st.session_state or force:
        st.session_state.board = [[0 for _ in range(8)] for _ in range(8)]
        st.session_state.queen_count = 0
        st.session_state.start_time = time.time()
        st.session_state.warning_shown = False

def count_queens():
    return st.session_state.queen_count

def get_attacked_queens():
    attacked = set()
    queens = [(r, c) for r in range(8) for c in range(8) if st.session_state.board[r][c] == 1]
    for i, (r1, c1) in enumerate(queens):
        for (r2, c2) in queens[i+1:]:
            if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                attacked.add((r1, c1))
                attacked.add((r2, c2))
    return attacked

def get_elapsed_time():
    return int(time.time() - st.session_state.start_time)

def is_solved():
    return count_queens() == 8 and len(get_attacked_queens()) == 0

def place_queen(row, col):
    if st.session_state.board[row][col] == 0 and st.session_state.queen_count < 8:
        st.session_state.board[row][col] = 1
        st.session_state.queen_count += 1
        st.session_state.warning_shown = False
    elif st.session_state.board[row][col] == 1:
        st.session_state.board[row][col] = 0
        st.session_state.queen_count -= 1
        st.session_state.warning_shown = False
    elif st.session_state.queen_count >= 8:
        st.session_state.warning_shown = True