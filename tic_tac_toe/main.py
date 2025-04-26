import streamlit as st
import numpy as np
import time
import plotly.express as px
import re
from algorithms import GreedyAl, MinimaxAl
from database import save_algorithm_performance, get_performance_data, save_game_moves, initialize_database

# Set Streamlit to wide mode
try:
    st.set_page_config(layout="wide")
except Exception as e:
    st.error(f"Error setting page configuration: {e}")

def validate_username(username: str) -> bool:
    """Validate username: alphanumeric, spaces, 1-20 characters."""
    if not username:
        st.error("Username cannot be empty.")
        return False
    if len(username) > 20:
        st.error("Username must be 20 characters or less.")
        return False
    if not re.match(r'^[a-zA-Z0-9 ]+$', username):
        st.error("Username can only contain letters, numbers, and spaces.")
        return False
    return True

class TicTacToe:
    def __init__(self):
        try:
            self.board = np.array([[' ' for _ in range(5)] for _ in range(5)])
            self.current_player = 'X'
            self.game_id = None
        except Exception as e:
            st.error(f"Error initializing game board: {e}")
            raise

    def make_move(self, x: int, y: int) -> bool:
        try:
            if 0 <= x < 5 and 0 <= y < 5 and self.board[x][y] == ' ':
                self.board[x][y] = self.current_player
                return True
            return False
        except Exception as e:
            st.error(f"Error making move: {e}")
            return False

    def check_winner(self) -> tuple[str, list]:
        try:
            for player in ['X', 'O']:
                # Check rows
                for i in range(5):
                    if all(self.board[i][j] == player for j in range(5)):
                        return player, [(i, j) for j in range(5)]
                # Check columns
                for j in range(5):
                    if all(self.board[i][j] == player for i in range(5)):
                        return player, [(i, j) for i in range(5)]
                # Check main diagonal
                if all(self.board[i][i] == player for i in range(5)):
                    return player, [(i, i) for i in range(5)]
                # Check anti-diagonal
                if all(self.board[i][4-i] == player for i in range(5)):
                    return player, [(i, 4-i) for i in range(5)]
            # Check for draw
            if all(self.board[i][j] != ' ' for i in range(5) for j in range(5)):
                return 'Draw', []
            return None, []
        except Exception as e:
            st.error(f"Error checking winner: {e}")
            return None, []

def render_html_board(board):
    try:
        html = """
        <style>
            .game-board { border-collapse: collapse; margin: 30px auto; }
            .game-cell { width: 100px; height: 100px; text-align: center; vertical-align: middle; font-size: 40px; }
            .header-cell { width: 100px; height: 100px; text-align: center; vertical-align: middle; font-size: 32px; border: none; padding: 0; margin: 0; font-weight: bold; }
            .diagonal-cell { position: relative; }
            .diagonal-cell::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top right, transparent calc(50% - 1px), black, transparent calc(50% + 1px)); }
            .x-label { position: absolute; top: 15px; left: 15px; font-size: 32px; }
            .y-label { position: absolute; bottom: 15px; right: 15px; font-size: 32px; }
            .x-mark { color: #3b82f6; }
            .o-mark { color: #ef4444; }
        </style>
        <table class="game-board">
            <tr>
                <th class="header-cell diagonal-cell">
                    <span class="x-label">x</span>
                    <span class="y-label">y</span>
                </th>"""
        
        for col_num in range(5):
            html += f'<th class="header-cell">{col_num}</th>'
        html += "</tr>"

        for i in range(5):
            html += f'<tr><th class="header-cell">{i}</th>'
            for j in range(5):
                css_class = "x-mark" if board[i][j] == 'X' else "o-mark" if board[i][j] == 'O' else ""
                html += f'<td class="game-cell {css_class}">{board[i][j]}</td>'
            html += "</tr>"
        
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error rendering board: {e}")

def main():
    try:
        st.markdown("<h1 style='font-size: 48px; margin-bottom: 50px;'>5x5 Tic-Tac-Toe ⭕❌ : Human vs. Computer</h1>", unsafe_allow_html=True)
        initialize_database()

        if 'game' not in st.session_state:
            st.session_state.game = TicTacToe()
            st.session_state.player_name = ""
            st.session_state.move_number = 0
            st.session_state.game_over = False
            st.session_state.result = None
            st.session_state.computer_has_moved = False
            st.session_state.computer_turn = False
            st.session_state.moves = []

        game = st.session_state.game

        if not st.session_state.player_name:
            st.markdown("<p style='font-size: 24px; margin-bottom: -5px;'>Enter your name:</p>", unsafe_allow_html=True)
            player_name = st.text_input(
                label="Player name input",
                value="",
                key="player_name_input",
                max_chars=20,
                help="Enter your name (letters, numbers, spaces only)",
                placeholder="Enter your name",
                label_visibility="collapsed"
            )
            if player_name:
                if validate_username(player_name):
                    st.session_state.player_name = player_name.strip()
                    st.rerun()
                else:
                    return

        col_board, col_right = st.columns([3, 1])

        with col_board:
            render_html_board(game.board)

        with col_right:
            st.markdown("<h3 style='font-size: 28px;'>Player Move</h3>", unsafe_allow_html=True)
            if not st.session_state.game_over and game.current_player == 'X':
                st.markdown("<p style='font-size: 24px; margin-bottom: 5px;'> -> X (Row, 0–4)</p>", unsafe_allow_html=True)
                x = st.number_input(
                    label="X input",
                    min_value=0,
                    max_value=4,
                    step=1,
                    key="x_input",
                    help="This is the X-axis (row)",
                    format="%d",
                    label_visibility="collapsed"
                )
                st.markdown("<p style='font-size: 24px; margin-bottom: 5px;'> -> Y (Column, 0–4)</p>", unsafe_allow_html=True)
                y = st.number_input(
                    label="Y input",
                    min_value=0,
                    max_value=4,
                    step=1,
                    key="y_input",
                    help="This is the Y-axis (column)",
                    format="%d",
                    label_visibility="collapsed"
                )
                if st.button("Make Move", key="make_move_btn", help="Submit your move"):
                    if game.make_move(x, y):
                        st.session_state.moves.append((x, y, st.session_state.move_number))
                        winner, winning_path = game.check_winner()
                        if winner:
                            st.session_state.game_over = True
                            st.session_state.result = winner
                            player_name_to_save = "Computer" if winner == 'O' else st.session_state.player_name
                            if winner in ['X', 'O']:
                                winning_moves = []
                                for pos in winning_path:
                                    for move in st.session_state.moves:
                                        if move[0] == pos[0] and move[1] == pos[1]:
                                            winning_moves.append(move)
                                            break
                                winning_moves.sort(key=lambda move: move[2])
                                moves_to_save = winning_moves
                            else:
                                moves_to_save = []
                            game.game_id = save_game_moves(
                                game.game_id,
                                player_name_to_save,
                                winner,
                                moves_to_save
                            )
                            save_algorithm_performance(game.game_id, st.session_state.move_number, None, None, update_game_id=True)
                        else:
                            game.current_player = 'O'
                            st.session_state.move_number += 1
                            st.session_state.computer_has_moved = False
                            st.session_state.computer_turn = True
                        st.rerun()
                    else:
                        st.error("Invalid move. Try another cell.")

        action_buttons_col = st.columns([1, 1])

        with action_buttons_col[0]:
            if st.button("Restart", key="restart_btn", help="Start a new game"):
                st.session_state.game = TicTacToe()
                st.session_state.game_over = False
                st.session_state.result = None
                st.session_state.move_number = 0
                st.session_state.computer_has_moved = False
                st.session_state.computer_turn = False
                st.session_state.moves = []
                st.rerun()

        with action_buttons_col[1]:
            if st.button("Quit", key="quit_btn", help="End the game"):
                st.session_state.game_over = True
                st.session_state.result = "Quit"
                player_name_to_save = st.session_state.player_name
                game.game_id = save_game_moves(
                    game.game_id,
                    player_name_to_save,
                    "Quit",
                    []
                )
                save_algorithm_performance(game.game_id, st.session_state.move_number, None, None, update_game_id=True)
                st.rerun()

        if (game.current_player == 'O' and 
            not st.session_state.game_over and 
            not st.session_state.computer_has_moved and 
            st.session_state.computer_turn):

            st.info("Computer is thinking...")

            try:
                greedy_al = GreedyAl(game.board, 'O')
                minimax_al = MinimaxAl(game.board, 'O')

                start_time_greedy = time.time()
                greedy_move, greedy_score = greedy_al.get_move_with_score()
                end_time_greedy = time.time()
                greedy_time = end_time_greedy - start_time_greedy

                start_time_minimax = time.time()
                minimax_move, minimax_score = minimax_al.get_move_with_score()
                end_time_minimax = time.time()
                minimax_time = end_time_minimax - start_time_minimax

                save_algorithm_performance(None, st.session_state.move_number, greedy_time, minimax_time)

                if greedy_score > minimax_score:
                    chosen_move = greedy_move
                    st.session_state.chosen_algorithm = "Greedy"
                else:
                    chosen_move = minimax_move
                    st.session_state.chosen_algorithm = "Minimax"

                if chosen_move:
                    x, y = chosen_move
                    game.make_move(x, y)
                    st.session_state.moves.append((x, y, st.session_state.move_number))
                    winner, winning_path = game.check_winner()
                    if winner:
                        st.session_state.game_over = True
                        st.session_state.result = winner
                        player_name_to_save = "Computer" if winner == 'O' else st.session_state.player_name
                        if winner in ['X', 'O']:
                            winning_moves = []
                            for pos in winning_path:
                                for move in st.session_state.moves:
                                    if move[0] == pos[0] and move[1] == pos[1]:
                                        winning_moves.append(move)
                                        break
                            winning_moves.sort(key=lambda move: move[2])
                            moves_to_save = winning_moves
                        else:
                            moves_to_save = []
                        game.game_id = save_game_moves(
                            game.game_id,
                            player_name_to_save,
                            winner,
                            moves_to_save
                        )
                        save_algorithm_performance(game.game_id, st.session_state.move_number, None, None, update_game_id=True)
                    else:
                        game.current_player = 'X'
                        st.session_state.move_number += 1
                        st.session_state.computer_has_moved = True
                        st.session_state.computer_turn = False
                    st.rerun()
            except Exception as e:
                st.error(f"Error during computer move: {e}")

        if st.session_state.game_over:
            if st.session_state.result == 'X':
                st.success(f"Congratulations, {st.session_state.player_name}! You won!")
            elif st.session_state.result == 'O':
                st.error("Computer wins!")
            elif st.session_state.result == 'Quit':
                st.warning("Game was quit. Game ended.")
            else:
                st.warning("It's a draw!")
            
            if st.button("New Game", help="Start a new game"):
                st.session_state.game = TicTacToe()
                st.session_state.game_over = False
                st.session_state.result = None
                st.session_state.move_number = 0
                st.session_state.computer_has_moved = False
                st.session_state.computer_turn = False
                st.session_state.moves = []
                st.rerun()

        # Performance chart section for latest 10 game rounds
        df = get_performance_data(limit=10)
        if not df.empty:
            st.markdown("<h3 style='font-size: 28px;'>Performance of Computer Strategies (Latest 10 Games)</h3>", unsafe_allow_html=True)
            try:
                fig = px.line(
                    df,
                    x='game_number',
                    y='time_taken',
                    color='algorithm',
                    title='Total Time Taken by Computer Strategies (Latest 10 Games)',
                    labels={
                        'game_number': 'Game Number',
                        'time_taken': 'Total Time Taken (seconds)',
                        'algorithm': 'Strategy'
                    },
                    color_discrete_map={'Greedy': '#00CC96', 'Minimax': '#EF553B'},
                    markers=True
                )

                fig.update_layout(
                    font=dict(size=16),
                    title_font_size=20,
                    xaxis_title="Game Number",
                    yaxis_title="Total Time Taken (seconds)",
                    xaxis=dict(
                        gridcolor='#30363d',
                        tickmode='linear',
                        tick0=1,
                        dtick=1
                    ),
                    yaxis=dict(
                        gridcolor='#30363d',
                        tickformat=".3f"
                    ),
                    legend_title_text='Strategy',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode="x unified"
                )

                for algo in df['algorithm'].unique():
                    avg_time = df[df['algorithm'] == algo]['time_taken'].mean()
                    fig.add_hline(
                        y=avg_time,
                        line_dash="dash",
                        line_color='#00CC96' if algo == 'Greedy' else '#EF553B',
                        annotation_text=f"Avg {algo}: {avg_time:.3f}s",
                        annotation_position="top left",
                        annotation_font_size=12
                    )

                st.plotly_chart(fig, use_container_width=True)

                st.markdown("""
                **What does this chart show?**  
                This chart displays the total time taken by the Greedy and Minimax strategies for each of the 10 most recent game rounds. Each game round represents one complete game, which may include multiple moves by the computer.  

                - **Why total time per game?** We use the total time to show the overall computational effort required by each strategy to play an entire game. This gives a clear comparison of how fast or slow each strategy is, regardless of the number of moves in a game.  
                - **Greedy (green)**: This strategy is usually faster because it makes quick decisions based on immediate benefits.  
                - **Minimax (red)**: This strategy is slower as it evaluates future moves to make smarter decisions, which takes more time.  
                - **Dashed lines**: These show the average time each strategy takes across the 10 games, helping you see which strategy is generally faster.  

                Use this chart to understand how the computer's strategies perform over full games and which one might be more efficient for your play style!
                """)
            except Exception as e:
                st.error(f"Error rendering performance chart: {e}")
        else:
            st.warning("No performance data available for the latest 10 games.")

    except Exception as e:
        st.error(f"Unexpected error in main application: {e}")

if __name__ == "__main__":
    main()