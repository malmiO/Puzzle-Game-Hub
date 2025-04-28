import json
import streamlit as st
import time
import mysql.connector
from datetime import datetime
import pandas as pd

from db import (
    init_db, save_player_answer, solution_exists, get_recognized_solutions,
    player_solution_exists, is_solution_recognized,
    count_unique_player_solutions, reset_player_solutions, save_to_db
)
from solver import sequential_solver, threaded_solver
from game import (
    init_game_state, count_queens, get_attacked_queens,
    get_elapsed_time, is_solved, place_queen
)

init_db()

def handle_player_answer(player_name, current_solution):
    try:
        if count_queens() < 8:
            st.error("Not enough queens placed! You need to place all 8 queens.")
            return

        if not is_solved():
            st.error("Incorrect solution! Some queens are attacking each other.")
            return

        if player_solution_exists(player_name, current_solution):
            st.warning("You already submitted this solution.")
            return

        if is_solution_recognized(current_solution):
            st.warning("This solution has already been recognized by another player. Try a new one.")
            return

        save_player_answer(player_name, current_solution)
        st.success(f"🎉 Congratulations {player_name}! You've added a new unique solution.")

        if count_unique_player_solutions() >= 92:
            reset_player_solutions()
            st.info("🎯 All 92 unique solutions have been found! The board has been reset for a new round of discovery.")
    except Exception as e:
        st.error(f"An unexpected error occurred while handling your solution: {e}")
        print(f"Error: {e}")

def main():
    st.set_page_config(page_title="Eight Queens Puzzle", layout="centered")
    st.title("♛ Eight Queens Puzzle")

    menu = ["Home", "Generate Solutions", "Play Game", "Leadership Board"]
    choice = st.sidebar.selectbox("Menu", menu)

    try:
        if choice == "Home":
            st.header("Welcome to the Eight Queens Puzzle!")
            st.markdown("""
            ### 🌟 Your Mission
            Place **8 queens** on an **8×8 chessboard** in such a way that **no two queens can attack each other**.
            - ❌ No two queens in the same **row**
            - ❌ No two queens in the same **column**
            - ❌ No two queens on the same **diagonal**
            There are **92 unique solutions** – can you discover them?

            ### 🕹️ How to Play
            1. Head over to the **Play Game** tab.
            2. Click on any square to place or remove a queen (♛).
            3. You can place up to **8 queens only**.
            4. Once all 8 are placed, enter your **name** and click **Check Solution**.
            5. If your solution is **correct and unique**, you'll be added to the **Leadership Board**! 🎉   
            """)

        elif choice == "Generate Solutions":
            action = st.selectbox("Select Action", ["Show Saved Results", "Solve Sequentially", "Solve Using Threads"])

            if action == "Solve Sequentially":
                if solution_exists("Sequential"):
                    st.warning("Sequential results already exist.")
                else:
                    with st.spinner("Solving..."):
                        time_taken, solutions = sequential_solver()
                        if time_taken is None:
                            st.warning("The sequential solution already exists.")
                        else:
                            save_to_db("Sequential", time_taken, solutions)
                            st.success(f"Solved in {time_taken:.4f} sec with {len(solutions)} solutions.")

            elif action == "Solve Using Threads":
                if solution_exists("Threaded"):
                    st.warning("Threaded results already exist.")
                else:
                    with st.spinner("Solving with threads..."):
                        time_taken, solutions = threaded_solver()
                        if time_taken is None:
                            st.warning("The threaded solution already exists.")
                        else:
                            save_to_db("Threaded", time_taken, solutions)
                            st.success(f"Solved in {time_taken:.4f} sec with {len(solutions)} solutions.")

            elif action == "Show Saved Results":
                try:
                    conn = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="eight_queens"
                    )
                    c = conn.cursor()
                    c.execute("SELECT method, time_taken, solutions, created_at FROM solutions ORDER BY id DESC LIMIT 10")
                    rows = c.fetchall()
                    conn.close()

                    if not rows:
                        st.info("ℹ️ No solutions have been generated yet!")
                    else:
                        formatted_rows = []
                        for method, time_taken, solutions_json, created_at in rows:
                            try:
                                total_solutions = len(json.loads(solutions_json))
                            except Exception as e:
                                total_solutions = "?"
                                print(f"Error parsing solutions: {e}")

                            try:
                                if isinstance(created_at, str):
                                    created_at = datetime.fromisoformat(created_at).strftime("%B %d, %Y %I:%M %p")
                                else:
                                    created_at = created_at.strftime("%B %d, %Y %I:%M %p")
                            except Exception as e:
                                print(f"Error formatting date: {e}")

                            formatted_rows.append((method, f"{time_taken:.4f}", total_solutions, created_at))

                        df = pd.DataFrame(formatted_rows, columns=["Method", "Time Taken (sec)", "Total Solutions", "Generated At"])
                        st.table(df)
                except Exception as e:
                    st.error(f"An error occurred while retrieving saved results: {e}")
                    print(f"Error retrieving results: {e}")

        elif choice == "Play Game":
            if "play_game_loaded" not in st.session_state or not st.session_state.play_game_loaded:
                init_game_state(force=True)
                st.session_state.play_game_loaded = True

            col1, col2, col3 = st.columns(3)
            col1.metric("Queens on board", f"{count_queens()}/8")
            col2.metric("Queens attacked", len(get_attacked_queens()))
            col3.metric("Time elapsed", f"{get_elapsed_time()} sec")

            if st.session_state.warning_shown:
                st.warning("You can only place up to 8 queens on the board!")

            cols = st.columns(8)
            for row in range(8):
                for col in range(8):
                    with cols[col]:
                        if st.button("♛" if st.session_state.board[row][col] else " ", key=f"btn_{row}_{col}"):
                            place_queen(row, col)

            player_name = st.text_input("Enter your name")
            if st.button("Check Solution"):
                if not player_name.strip():
                    st.warning("Please enter your name before checking the solution.")
                else:
                    current_solution = [row.index(1) for row in st.session_state.board]
                    handle_player_answer(player_name, current_solution)

            if st.button("Restart"):
                init_game_state(force=True)
                st.session_state.play_game_loaded = True
                st.rerun()

        elif choice == "Leadership Board":
            try:
                st.subheader("Leadership Board")
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="eight_queens"
                )
                c = conn.cursor()
                c.execute("SELECT player_name, correct_solution, created_at FROM player_answers WHERE correct_solution IS NOT NULL")
                rows = c.fetchall()
                conn.close()

                if not rows:
                    st.info("No one has won the game yet!")
                else:
                    col1, col2, col3 = st.columns(3)
                    col1.write("**Player**")
                    col2.write("**Solution**")
                    col3.write("**Date & Time**")
                    for row in rows:
                        c1, c2, c3 = st.columns(3)
                        c1.write(row[0])
                        c2.write(str(json.loads(row[1])))
                        try:
                            if isinstance(row[2], str):
                                formatted_time = datetime.fromisoformat(row[2]).strftime("%B %d, %Y %I:%M %p")
                            else:
                                formatted_time = row[2].strftime("%B %d, %Y %I:%M %p")
                        except Exception as e:
                            formatted_time = str(row[2])
                            print(f"Error formatting time: {e}")
                        c3.write(formatted_time)
            except Exception as e:
                st.error(f"An error occurred while retrieving the leaderboard: {e}")
                print(f"Error retrieving leaderboard: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
