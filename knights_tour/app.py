import streamlit as st
import random
import re
import plotly.graph_objects as go
from knight_tour import solve_knights_tour_backtracking, solve_knights_tour_warnsdorff, solve_knights_tour_pure_backtracking, is_valid_move, is_valid_tour, get_valid_moves
from database import save_algorithm_times, save_winner_details, fetch_algorithm_performance
import mysql.connector
from mysql.connector import DataError
import time
import uuid
import traceback

# Streamlit app configuration
try:
    st.set_page_config(page_title="Knight's Tour Game", layout="wide")
except Exception as e:
    print(f"Error setting Streamlit page configuration: {e}")

def initialize_board():
    """Initialize an 8x8 chessboard."""
    try:
        return [[-1 for _ in range(8)] for _ in range(8)]
    except Exception as e:
        print(f"Error initializing board: {e}")
        return [[-1 for _ in range(8)] for _ in range(8)]

def create_chessboard_plot(board, valid_moves=None, current_pos=None):
    """Create a Plotly chessboard visualization."""
    try:
        z = [[0 if (i + j) % 2 == 0 else 1 for j in range(8)] for i in range(8)]
        colors = [[('#f0d9b5' if (i + j) % 2 == 0 else '#b58863') for j in range(8)] for i in range(8)]
        text = [[f"{board[i][j]}" if board[i][j] != -1 else '' for j in range(8)] for i in range(8)]
        hovertext = [[f"({i},{j})" for j in range(8)] for i in range(8)]
        
        if current_pos:
            text[current_pos[0]][current_pos[1]] = '♞'
        
        if valid_moves:
            for move in valid_moves:
                i, j = move
                colors[i][j] = '#aaffaa' if (i + j) % 2 == 0 else '#88cc88'
                hovertext[i][j] += " - Valid move!"

        fig = go.Figure()
        
        fig.add_trace(go.Heatmap(
            z=z,
            colorscale=[[0, '#f0d9b5'], [1, '#b58863']],
            showscale=False,
            customdata=[[f"({i},{j})" for j in range(8)] for i in range(8)],
            hoverinfo="text",
            hovertext=hovertext,
            textfont=dict(size=20),
            text=text,
            texttemplate="%{text}"
        ))

        if valid_moves:
            for move in valid_moves:
                i, j = move
                fig.add_trace(go.Scatter(
                    x=[j],
                    y=[i],
                    mode='markers',
                    marker=dict(size=40, color=colors[i][j], opacity=0.5),
                    hoverinfo="skip",
                    showlegend=False
                ))

        fig.update_layout(
            width=600,
            height=600,
            xaxis=dict(
                tickvals=list(range(8)),
                ticktext=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                side="top",
                range=[-0.5, 7.5],
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                tickvals=list(range(8)),
                ticktext=[str(8-i) for i in range(8)],
                autorange="reversed",
                range=[-0.5, 7.5],
                showgrid=False,
                zeroline=False,
                scaleanchor="x",
                scaleratio=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=50, b=50),
            clickmode='event'
        )

        fig.add_trace(go.Scatter(
            x=[j for j in range(8) for _ in range(8)],
            y=[i for _ in range(8) for i in range(8)],
            customdata=[(i, j) for i in range(8) for j in range(8)],
            mode='markers',
            marker=dict(opacity=0, size=30),
            hoverinfo="skip",
            showlegend=False
        ))

        return fig
    except Exception as e:
        print(f"Error creating chessboard plot: {e}")
        return go.Figure()

def create_performance_chart(performance_data):
    """Create a Plotly grouped bar chart for algorithm performance across rounds."""
    try:
        if not performance_data:
            return go.Figure()

        round_ids = [data[0][-8:] for data in performance_data]  # Use last 8 chars of round_id for brevity
        warnsdorff_times = [data[1] for data in performance_data]
        backtracking_times = [data[2] for data in performance_data]
        pure_backtracking_times = [data[3] for data in performance_data]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=round_ids,
            y=warnsdorff_times,
            name="Warnsdorff",
            marker_color='blue',
            text=[f"{t:.4f}" for t in warnsdorff_times],  # Display exact times on bars
            textposition='auto'
        ))

        fig.add_trace(go.Bar(
            x=round_ids,
            y=backtracking_times,
            name="Optimized Backtracking",
            marker_color='green',
            text=[f"{t:.4f}" for t in backtracking_times],
            textposition='auto'
        ))

        fig.add_trace(go.Bar(
            x=round_ids,
            y=pure_backtracking_times,
            name="Pure Backtracking",
            marker_color='red',
            text=[f"{t:.2f}" for t in pure_backtracking_times],
            textposition='auto'
        ))

        fig.update_layout(
            title="Algorithm Performance (Execution Time) for Latest 10 Rounds",
            xaxis_title="Round ID (Last 8 Characters)",
            yaxis_title="Execution Time (seconds)",
            xaxis=dict(tickangle=45),
            yaxis=dict(range=[0, max(max(pure_backtracking_times, default=1), 1) * 1.1]),
            barmode='group',  # Group bars for each round
            bargap=0.2,  # Gap between bars in each group
            bargroupgap=0.1,  # Gap between groups
            legend=dict(x=0, y=1, bgcolor='rgba(255,255,255,0.5)'),
            width=900,  # Increased width to accommodate 10 rounds
            height=500,
            margin=dict(l=50, r=50, t=100, b=100)
        )

        return fig
    except Exception as e:
        print(f"Error creating performance chart: {e}")
        st.error(f"Error creating performance chart: {e}")
        return go.Figure()

def compute_algorithm_solutions():
    """Compute solutions for all algorithms and save execution times."""
    try:
        print("Computing algorithm solutions...")
        with st.spinner("Computing algorithm solutions, please wait..."):
            # Warnsdorff's Algorithm
            start_time = time.time()
            try:
                st.session_state.warnsdorff_solution = solve_knights_tour_warnsdorff(st.session_state.start_pos)
                st.session_state.warnsdorff_time = time.time() - start_time
                print(f"Warnsdorff computation completed in {st.session_state.warnsdorff_time:.2f} seconds")
            except Exception as e:
                print(f"Error in Warnsdorff computation: {e}")
                st.session_state.warnsdorff_solution = None
                st.session_state.warnsdorff_time = 0

            # Optimized Backtracking Algorithm
            start_time = time.time()
            try:
                st.session_state.backtracking_solution = solve_knights_tour_backtracking(st.session_state.start_pos)
                st.session_state.backtracking_time = time.time() - start_time
                print(f"Optimized Backtracking computation completed in {st.session_state.backtracking_time:.2f} seconds")
            except Exception as e:
                print(f"Error in Optimized Backtracking computation: {e}")
                st.session_state.backtracking_solution = None
                st.session_state.backtracking_time = 0

            # Pure Backtracking Algorithm
            start_time = time.time()
            try:
                st.session_state.pure_backtracking_solution = solve_knights_tour_pure_backtracking(st.session_state.start_pos)
                st.session_state.pure_backtracking_time = time.time() - start_time
                print(f"Pure Backtracking computation completed in {st.session_state.pure_backtracking_time:.2f} seconds")
            except Exception as e:
                print(f"Error in Pure Backtracking computation: {e}")
                st.session_state.pure_backtracking_solution = None
                st.session_state.pure_backtracking_time = 0

            # Save to database
            try:
                save_algorithm_times(
                    st.session_state.round_id,
                    st.session_state.warnsdorff_time,
                    st.session_state.backtracking_time,
                    st.session_state.pure_backtracking_time
                )
                st.session_state.algorithms_computed = True
                print("Algorithm times saved to database")
            except mysql.connector.Error as e:
                st.error(f"Database error saving algorithm times: {e}")
                print(f"Database error: {e}")

    except Exception as e:
        st.error(f"Error computing algorithm solutions: {e}")
        print(f"Error in compute_algorithm_solutions: {e}")

def validate_player_name(name):
    """Validate the player's name."""
    try:
        name = name.strip()  # Trim whitespace
        if not name:
            return False, "Please enter a valid name."
        if len(name) > 255:
            return False, "Name must not exceed 255 characters."
        if not re.match("^[a-zA-Z0-9 ]+$", name):
            return False, "Name can only contain letters, numbers, and spaces."
        return True, ""
    except Exception as e:
        print(f"Error validating player name: {e}")
        return False, f"Error validating name: {e}"

def main():
    try:
        st.title("Knight's Tour Problem")
        st.markdown("Select one of the Available Moves to move the knight on the Chess Board. Valid moves are highlighted in green.")

        # Initialize session state
        if 'board' not in st.session_state:
            print("Initializing new game session...")
            try:
                st.session_state.board = initialize_board()
                #st.session_state.start_pos = (random.randint(0, 7), random.randint(0, 7))
                st.session_state.start_pos = (3, 6)
                st.session_state.moves = [st.session_state.start_pos]
                st.session_state.board[st.session_state.start_pos[0]][st.session_state.start_pos[1]] = 0
                st.session_state.move_count = 1
                st.session_state.game_over = False
                st.session_state.player_name = ""
                st.session_state.round_id = str(uuid.uuid4())
                st.session_state.warnsdorff_time = 0
                st.session_state.backtracking_time = 0
                st.session_state.pure_backtracking_time = 0
                st.session_state.algorithms_computed = False
                st.session_state.last_clicked_pos = None
                st.session_state.name_valid = False
            except Exception as e:
                st.error(f"Error initializing session state: {e}")
                print(f"Error initializing session state: {e}")
                return

        # Input for player name with validation
        try:
            player_name_input = st.text_input(
                "Enter your name:",
                value=st.session_state.player_name,
                max_chars=255,
                help="Name can only contain letters, numbers, and spaces."
            )
            is_valid, error_message = validate_player_name(player_name_input)
            if not is_valid:
                st.error(error_message)
                st.session_state.name_valid = False
                st.session_state.player_name = player_name_input.strip()
                return  # Prevent game progression until name is valid
            else:
                st.session_state.player_name = player_name_input.strip()
                st.session_state.name_valid = True
        except Exception as e:
            st.error(f"Error processing player name: {e}")
            print(f"Error processing player name: {e}")
            return

        # Calculate valid moves for current position
        try:
            current_pos = st.session_state.moves[-1]
            valid_moves = get_valid_moves(current_pos, st.session_state.board) if not st.session_state.game_over else []
        except Exception as e:
            print(f"Error calculating valid moves: {e}")
            valid_moves = []
            st.error(f"Error calculating valid moves: {e}")

        # Display the chessboard
        st.subheader("Current Board")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            try:
                fig = create_chessboard_plot(st.session_state.board, valid_moves, current_pos)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying chessboard: {e}")
                print(f"Error displaying chessboard: {e}")

        with col2:
            try:
                st.markdown("### Game Info")
                st.write(f"Starting Position: {st.session_state.start_pos}")
                st.write(f"Current Position: {current_pos}")
                st.write(f"Moves Made: {st.session_state.move_count - 1}/64")
                
                st.markdown("---")
                
                st.markdown("### Available Moves")
                
                if valid_moves:
                    move_cols = st.columns(2)
                    for i, move in enumerate(valid_moves):
                        col_idx = i % 2
                        with move_cols[col_idx]:
                            row, col = move
                            chess_notation = f"{chr(97+col)}{8-row}"
                            if st.button(f"Move to {chess_notation}", key=f"move_{row}_{col}", use_container_width=True):
                                try:
                                    print(f"User made move to {move}")
                                    next_move = move
                                    st.session_state.board[next_move[0]][next_move[1]] = st.session_state.move_count
                                    st.session_state.moves.append(next_move)
                                    st.session_state.move_count += 1
                                    
                                    if st.session_state.move_count == 64:
                                        if is_valid_tour(st.session_state.board, st.session_state.moves):
                                            st.session_state.game_over = True
                                            try:
                                                compute_algorithm_solutions()
                                                player_name = st.session_state.player_name
                                                move_sequence = ",".join([f"({r},{c})" for r, c in st.session_state.moves])
                                                try:
                                                    save_winner_details(
                                                        st.session_state.round_id,
                                                        player_name,
                                                        move_sequence
                                                    )
                                                except DataError as e:
                                                    st.error("The name is too long. Please use a name with 255 or fewer characters.")
                                                    print(f"Database DataError: {e}")
                                                except mysql.connector.Error as e:
                                                    st.error(f"Database error: {e}")
                                                    print(f"Database error: {e}")
                                            except Exception as e:
                                                st.error(f"Error saving game results: {e}")
                                                print(f"Error saving game results: {e}")
                                    
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error processing move: {e}")
                                    print(f"Error processing move: {e}")
                elif not st.session_state.game_over and st.session_state.move_count < 64:
                    st.error("No valid moves available! Game over.")
                    st.session_state.game_over = True
            except Exception as e:
                st.error(f"Error displaying game info: {e}")
                print(f"Error displaying game info: {e}")

        # Game over options
        if st.session_state.game_over:
            try:
                st.subheader("Game Over")
                if st.session_state.move_count == 64 and is_valid_tour(st.session_state.board, st.session_state.moves):
                    st.balloons()
                    st.success("Congratulations! You've completed a valid Knight's Tour!")
                    st.write("You won! The tour is valid.")
                else:
                    st.write("You lost! The tour is incomplete or invalid.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Play Again"):
                        try:
                            print("User clicked Play Again")
                            st.session_state.board = initialize_board()
                            st.session_state.start_pos = (random.randint(0, 7), random.randint(0, 7))
                            st.session_state.moves = [st.session_state.start_pos]
                            st.session_state.board[st.session_state.start_pos[0]][st.session_state.start_pos[1]] = 0
                            st.session_state.move_count = 1
                            st.session_state.game_over = False
                            st.session_state.round_id = str(uuid.uuid4())
                            st.session_state.warnsdorff_time = 0
                            st.session_state.backtracking_time = 0
                            st.session_state.pure_backtracking_time = 0
                            st.session_state.algorithms_computed = False
                            if 'warnsdorff_solution' in st.session_state:
                                print("Clearing warnsdorff_solution")
                                del st.session_state.warnsdorff_solution
                            if 'backtracking_solution' in st.session_state:
                                print("Clearing backtracking_solution")
                                del st.session_state.backtracking_solution
                            if 'pure_backtracking_solution' in st.session_state:
                                print("Clearing pure_backtracking_solution")
                                del st.session_state.pure_backtracking_solution
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error resetting game: {e}")
                            print(f"Error resetting game: {e}")
                with col2:
                    if not st.session_state.algorithms_computed:
                        if st.button(
                            "Generate Algorithm Solutions",
                            key="generate_solutions_game_over",
                            use_container_width=True,
                            help="Click to compute solutions using different algorithms.",
                            type="primary"
                        ):
                            try:
                                compute_algorithm_solutions()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating algorithm solutions: {e}")
                                print(f"Error generating algorithm solutions: {e}")
            except Exception as e:
                st.error(f"Error handling game over: {e}")
                print(f"Error handling game over: {e}")

        # Educational expander: Learn about Knight's Tour
        with st.expander("Learn About Knight's Tour"):
            st.subheader("Learn About Knight's Tour")
            
            st.markdown("### What is the Knight's Tour Problem?")
            st.markdown("""
            The Knight's Tour is a classic problem in chess and computer science. The goal is to move a knight on an 8x8 chessboard so that it visits each square **exactly once**, following the knight's unique L-shaped movement pattern. Here’s what you need to know:

            - **Knight's Movement**: The knight moves in an L-shape: two squares in one direction and one square perpendicular, or one square in one direction and two squares perpendicular. For example, from position (3,4), the knight can move to (5,5), (5,3), (1,5), (1,3), (4,6), (4,2), (2,6), or (2,2).
            - **Open vs. Closed Tours**: An *open tour* means the knight can end anywhere after visiting all 64 squares. A *closed tour* means the knight must return to its starting square, forming a loop.
            - **History**: The problem dates back to the 9th century, with early solutions found in Arabic manuscripts. It became a popular mathematical puzzle in the 18th century, studied by mathematicians like Euler and Legendre.
            - **Significance**: The Knight's Tour is used to study graph theory (the board can be modeled as a graph where squares are nodes and knight moves are edges) and algorithm efficiency.
            """)

            st.markdown("### How the Knight Moves")
            st.markdown("""
            Here’s a simple diagram showing the knight's possible moves from a central position (marked as 'K'):
            """)
            st.code("""
. x . x .
x . . . x
. . K . .
x . . . x
. x . x .
            """)
            st.markdown("""
            - **K**: The knight's current position.
            - **x**: Possible squares the knight can move to.
            - **.**: Empty spaces.
            """)

            st.markdown("### Algorithms Used in This Game")
            st.markdown("""
            This game uses three different algorithms to solve the Knight's Tour. You can see their solutions and performance after completing a game:

            - **Warnsdorff's Algorithm**:
              - A heuristic method that chooses the next move with the fewest onward moves (i.e., the square that leads to the fewest unvisited squares).
              - Fast and often finds a solution quickly, but it’s not guaranteed to succeed in all cases.
              - Execution time: Usually less than 0.5 seconds, as seen in the performance chart.

            - **Optimized Backtracking**:
              - A smarter version of backtracking that uses heuristics (like Warnsdorff’s rule and preferring edge/corner moves) to reduce the search space.
              - More reliable than Warnsdorff’s but still fast, often completing in under 1 second.
              - Has a timeout of 20 seconds to prevent excessive computation.

            - **Pure Backtracking**:
              - A brute-force approach that tries all possible moves, backtracking when it reaches a dead end.
              - Guaranteed to find a solution if one exists, but very slow—often taking up to 60 seconds, as seen in the performance chart.
              - Has a timeout of 60 seconds, so it may not always complete.

            These algorithms demonstrate different trade-offs between speed and reliability. Warnsdorff’s and Optimized Backtracking are much faster, which is why their execution times are near 0 compared to Pure Backtracking.
            """)

            st.markdown("### Tips and Strategies for Solving the Knight's Tour")
            st.markdown("""
            Solving the Knight's Tour manually can be challenging, but here are some tips to improve your chances:

            - **Start Smart**: Starting in the center (e.g., (3,4)) often gives you more flexibility than starting in a corner (e.g., (0,0)), where the knight has fewer initial moves.
            - **Prioritize Low-Degree Squares**: Like Warnsdorff’s algorithm, try to move to squares that have the fewest unvisited onward moves. This reduces the chance of getting trapped.
              - For example, from (3,4), if (5,5) has 3 onward moves and (4,6) has 5, move to (5,5) first.
            - **Avoid Corners Early**: Corners and edges have fewer moves, so save them for later in your tour to avoid getting stuck.
            - **Plan Ahead**: Look a few moves ahead to ensure you don’t box yourself in. If you see a move that might lead to a dead end, try a different path.
            - **Practice**: The more you play, the better you’ll get at recognizing patterns that lead to a successful tour.

            Experiment with different starting positions and strategies to see what works best for you!
            """)

            st.markdown("### Fun Fact")
            st.markdown("""
            Did you know there are over **26 trillion** possible open Knight's Tours on an 8x8 board? However, finding a closed tour is much harder—there are only about 132,000 closed tours starting from a given square. This game challenges you to find just one of those many possibilities!
            """)

        # Display algorithm solutions when expander is opened
        with st.expander("View Algorithm Solutions"):
            try:
                if st.session_state.algorithms_computed:
                    st.subheader("Algorithm Solutions")
                    
                    row1_col1, row1_col2 = st.columns(2)
                    
                    with row1_col1:
                        st.markdown("### Warnsdorff's Algorithm Solution")
                        if st.session_state.warnsdorff_solution:
                            try:
                                fig = create_chessboard_plot(st.session_state.warnsdorff_solution)
                                st.plotly_chart(fig, use_container_width=True)
                                st.write(f"Execution Time: {st.session_state.warnsdorff_time:.4f} seconds")
                            except Exception as e:
                                st.error(f"Error displaying Warnsdorff solution: {e}")
                                print(f"Error displaying Warnsdorff solution: {e}")
                        else:
                            st.write("No solution found with Warnsdorff's algorithm.")

                    with row1_col2:
                        st.markdown("### Optimized Backtracking Solution")
                        if st.session_state.backtracking_solution:
                            try:
                                fig = create_chessboard_plot(st.session_state.backtracking_solution)
                                st.plotly_chart(fig, use_container_width=True)
                                st.write(f"Execution Time: {st.session_state.backtracking_time:.4f} seconds")
                            except Exception as e:
                                st.error(f"Error displaying Optimized Backtracking solution: {e}")
                                print(f"Error displaying Optimized Backtracking solution: {e}")
                        else:
                            st.write("No solution found with Optimized Backtracking algorithm within time limit.")

                    st.markdown("### Pure Backtracking Solution")
                    if st.session_state.pure_backtracking_solution:
                        try:
                            fig = create_chessboard_plot(st.session_state.pure_backtracking_solution)
                            st.plotly_chart(fig, use_container_width=True)
                            st.write(f"Execution Time: {st.session_state.pure_backtracking_time:.4f} seconds")
                        except Exception as e:
                            st.error(f"Error displaying Pure Backtracking solution: {e}")
                            print(f"Error displaying Pure Backtracking solution: {e}")
                    else:
                        st.write("No solution found with Pure Backtracking algorithm within time limit.")
                else:
                    if st.session_state.game_over:
                        st.info("Solutions have not been computed yet. Complete the tour or run out of moves, then click 'Generate Algorithm Solutions' in the 'Game Over' section to compute and view solutions.")
                    else:
                        st.info("Solutions can be computed after the game ends. Complete the tour or run out of moves to proceed.")
            except Exception as e:
                st.error(f"Error displaying algorithm solutions: {e}")
                print(f"Error displaying algorithm solutions: {e}")

        # Display algorithm performance chart for latest 10 rounds
        with st.expander("View Algorithm Performance Analysis"):
            try:
                st.subheader("Algorithm Performance Analysis")
                performance_data = fetch_algorithm_performance()
                if performance_data:
                    fig = create_performance_chart(performance_data)
                    st.plotly_chart(fig, use_container_width=True)
                    st.write("This chart shows the execution times of the three algorithms for the latest 10 game rounds, ordered by timestamp (most recent first).")
                else:
                    st.info("No performance data available. Play some games to generate data.")
            except Exception as e:
                st.error(f"Error displaying performance analysis: {e}")
                print(f"Error displaying performance analysis: {e}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        print(f"Unexpected error in main: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application failed to start: {e}")
        print(f"Application error: {e}\n{traceback.format_exc()}")