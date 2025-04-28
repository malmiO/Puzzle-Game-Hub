import streamlit as st
import time
import random
import pandas as pd

# Import from local modules
from database import init_db, save_result, get_leaderboard
from algorithms import solve_hanoi_recursive, solve_hanoi_iterative, solve_frame_stewart
from game_logic import init_game_state, is_valid_move, apply_move, is_solved
from ui_components import render_game_board

# Helper function to check if game is solved and handle winning state
def check_game_solved():
    if is_solved(st.session_state.game_state, st.session_state.disk_count):
        st.balloons()
        st.success(f"Congratulations! You solved the puzzle in {st.session_state.move_count} moves!")
        
        # Get player name from session state - ensure it's not empty
        player_name = st.session_state.player_name if st.session_state.player_name else "Anonymous"
        
        # Compare with algorithms
        compare_algorithms(player_name, st.session_state.disk_count, 
                         st.session_state.move_count, ",".join(st.session_state.moves_made))
        
        # Reset game
        st.session_state.game_active = False
        return True
    return False

# Helper function to compare algorithms and save results
def compare_algorithms(player_name, disk_count, moves_count, move_sequence):
    # Compare with algorithms
    recursive_moves, recursive_time = solve_hanoi_recursive(disk_count, 'A', 'B', 'C')
    iterative_moves, iterative_time = solve_hanoi_iterative(disk_count, 'A', 'B', 'C')
    
    st.write(f"Recursive algorithm solved it in {len(recursive_moves)} moves in {recursive_time:.6f} seconds")
    st.write(f"Iterative algorithm solved it in {len(iterative_moves)} moves in {iterative_time:.6f} seconds")
    
    # Save results for 3 pegs - use the passed player_name parameter
    save_result(player_name, disk_count, moves_count, move_sequence, 
               "Player Solution (3 pegs)", 0)
    save_result("Algorithm", disk_count, len(recursive_moves), 
               ",".join(recursive_moves), "Recursive", recursive_time)
    save_result("Algorithm", disk_count, len(iterative_moves), 
               ",".join(iterative_moves), "Iterative", iterative_time)
    
    # If 4 pegs were used, also compare with Frame-Stewart
    if st.session_state.peg_count == 4:
        fs_moves, fs_time = solve_frame_stewart(disk_count, 'A', 'B', 'C', 'D')
        st.write(f"Frame-Stewart algorithm (4 pegs) solved it in {len(fs_moves)} moves in {fs_time:.6f} seconds")
        
        # Save results for 4 pegs - use the passed player_name parameter
        save_result(player_name, disk_count, moves_count, move_sequence, 
                   "Player Solution (4 pegs)", 0)
        save_result("Algorithm", disk_count, len(fs_moves), 
                   ",".join(fs_moves), "Frame-Stewart (4 pegs)", fs_time)

# Function to handle individual move using callbacks
def make_move_callback():
    source = st.session_state.source_peg
    destination = st.session_state.destination_peg
    
    # Check if the player has already used all committed moves
    if st.session_state.move_count >= st.session_state.committed_moves:
        st.session_state.move_error = "You've used all your committed moves! Game over."
        st.session_state.game_lost = True
        return
    
    if source == destination:
        st.session_state.move_error = "Source and destination pegs cannot be the same!"
        return
    
    if apply_move(st.session_state.game_state, source, destination):
        st.session_state.move_count += 1
        st.session_state.moves_made.append(f"{source}->{destination}")
        st.session_state.move_sequence = ",".join(st.session_state.moves_made)
        st.session_state.move_error = None
        
        # Check if the game is solved
        if is_solved(st.session_state.game_state, st.session_state.disk_count):
            st.session_state.game_solved = True
        # Check if player has used all moves without solving
        elif st.session_state.move_count >= st.session_state.committed_moves:
            st.session_state.move_error = "You've used all your committed moves but didn't solve the puzzle. Game over!"
            st.session_state.game_lost = True
    else:
        st.session_state.move_error = "Invalid move! Remember, you cannot place a larger disk on a smaller one."

# Function to replay moves from a sequence
def replay_move_sequence():
    if not st.session_state.is_replaying:
        return
    
    # Get current index and total moves
    current_idx = st.session_state.current_replay_index
    total_moves = len(st.session_state.replay_moves)
    
    # If we've reached the end, stop replaying
    if current_idx >= total_moves:
        st.session_state.is_replaying = False
        
        # Check if puzzle is solved
        if is_solved(st.session_state.game_state, st.session_state.disk_count):
            # Keep success state but stop replaying
            st.session_state.replay_complete = True
        else:
            # The solution didn't work
            st.session_state.replay_error = "Your solution didn't solve the puzzle within your committed moves!"
        return
    
    # Apply the current move
    move = st.session_state.replay_moves[current_idx]
    try:
        source, destination = move.split('->')
        
        if apply_move(st.session_state.game_state, source, destination):
            # Update move count and moves made
            st.session_state.moves_made.append(move)
            st.session_state.move_count += 1
            
            # Move to next index
            st.session_state.current_replay_index += 1
            
            # Enforce a rerun to process the next move
            st.rerun()
        else:
            # If move is invalid, stop replaying
            st.session_state.is_replaying = False
            st.session_state.replay_error = f"Invalid move: {move}"
    except Exception as e:
        st.session_state.is_replaying = False
        st.session_state.replay_error = f"Error processing move: {move} - {str(e)}"

# Function to process sequence submission
def submit_solution():
    moves = st.session_state.solution_sequence.split(',')
    if len(moves) > st.session_state.committed_moves:
        st.session_state.solution_error = f"You provided {len(moves)} moves but you committed to only {st.session_state.committed_moves} moves!"
        return
    
    # Reset game state and apply moves to test validity
    test_state = init_game_state(st.session_state.disk_count)
    valid_solution = True
    
    for move in moves:
        if '->' not in move:
            st.session_state.solution_error = f"Invalid move format: {move}. Use 'Source->Destination' format."
            valid_solution = False
            break
        
        source, destination = move.split('->')
        if not apply_move(test_state, source, destination):
            st.session_state.solution_error = f"Invalid move: {move}. Check your solution."
            valid_solution = False
            break
    
    if valid_solution:
        if is_solved(test_state, st.session_state.disk_count):
            # Setup for replaying the moves
            st.session_state.game_state = init_game_state(st.session_state.disk_count)
            st.session_state.move_count = 0
            st.session_state.moves_made = []
            st.session_state.move_sequence = st.session_state.solution_sequence
            
            # Store moves for replay
            st.session_state.replay_moves = moves
            st.session_state.current_replay_index = 0
            st.session_state.is_replaying = True
            st.session_state.replay_complete = False
            st.session_state.replay_error = None
            
            # Trigger the first move in the sequence
            st.rerun()
        else:
            st.session_state.solution_error = "Your solution does not solve the puzzle within your committed moves!"

# Generate the initial disk count before committing to moves
def generate_game_parameters():
    # Generate random disk count between 5 and 10
    disk_count = random.randint(5, 10)
    st.session_state.disk_count = disk_count
    st.session_state.peg_count = st.session_state.peg_selection
    st.session_state.disk_count_generated = True
    
    # Calculate optimal moves, but don't show to user
    if st.session_state.peg_count == 3:
        st.session_state.optimal_moves, _ = solve_hanoi_recursive(disk_count, 'A', 'B', 'C')
    else:
        st.session_state.optimal_moves, _ = solve_frame_stewart(disk_count, 'A', 'B', 'C', 'D')
    
    st.success(f"Game parameters generated: {disk_count} disks with {st.session_state.peg_count} pegs.")

# Function to set up game with committed move count
def setup_game():
    # Store player's committed move count
    st.session_state.committed_moves = st.session_state.move_commitment
    
    # Use the previously generated disk count
    disk_count = st.session_state.disk_count
    
    # Initialize the game state
    st.session_state.game_state = init_game_state(disk_count)
    st.session_state.game_active = True
    st.session_state.move_count = 0
    st.session_state.moves_made = []
    st.session_state.move_sequence = ""
    st.session_state.move_error = None
    st.session_state.game_solved = False
    st.session_state.game_lost = False
    st.session_state.is_replaying = False
    st.session_state.replay_complete = False
    st.session_state.solution_success = False
    st.session_state.setup_complete = True
    
    st.success(f"Game started with {disk_count} disks and {st.session_state.peg_count} pegs! You committed to solving it in {st.session_state.committed_moves} moves.")

# Main application
def main():
    st.set_page_config(page_title="Tower of Hanoi Challenge", layout="wide")
    
    # Initialize database
    init_db()
    
    # App title
    st.title("Tower of Hanoi Challenge")
    
    # Initialize session state variables
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    if 'disk_count_generated' not in st.session_state:
        st.session_state.disk_count_generated = False
    if 'disk_count' not in st.session_state:
        st.session_state.disk_count = 0
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {}
    if 'move_count' not in st.session_state:
        st.session_state.move_count = 0
    if 'moves_made' not in st.session_state:
        st.session_state.moves_made = []
    if 'optimal_moves' not in st.session_state:
        st.session_state.optimal_moves = []
    if 'peg_count' not in st.session_state:
        st.session_state.peg_count = 3
    if 'move_sequence' not in st.session_state:
        st.session_state.move_sequence = ""
    if 'source_peg' not in st.session_state:
        st.session_state.source_peg = 'A'
    if 'destination_peg' not in st.session_state:
        st.session_state.destination_peg = 'B'
    if 'move_error' not in st.session_state:
        st.session_state.move_error = None
    if 'game_solved' not in st.session_state:
        st.session_state.game_solved = False
    if 'game_lost' not in st.session_state:
        st.session_state.game_lost = False
    if 'committed_moves' not in st.session_state:
        st.session_state.committed_moves = 0
    if 'player_name' not in st.session_state:
        st.session_state.player_name = "Player"
    
    # Replay-specific state variables
    if 'replay_moves' not in st.session_state:
        st.session_state.replay_moves = []
    if 'current_replay_index' not in st.session_state:
        st.session_state.current_replay_index = 0
    if 'is_replaying' not in st.session_state:
        st.session_state.is_replaying = False
    if 'replay_complete' not in st.session_state:
        st.session_state.replay_complete = False
    if 'replay_error' not in st.session_state:
        st.session_state.replay_error = None
    
    # Continue replay if in progress
    if st.session_state.is_replaying:
        replay_move_sequence()
    
    # Sidebar for game options
    st.sidebar.header("Game Options")
    
    # Menu options
    menu = st.sidebar.selectbox("Menu", ["Play Tower of Hanoi", "Leaderboard", "Algorithm Comparison"])
    
    # Process drag and drop moves if not replaying
    if not st.session_state.is_replaying and 'source' in st.query_params and 'destination' in st.query_params:
        source = st.query_params['source'][0]
        destination = st.query_params['destination'][0]
        
        if source and destination and st.session_state.game_active and not st.session_state.game_lost:
            st.session_state.source_peg = source
            st.session_state.destination_peg = destination
            make_move_callback()

    # Handle game solved state that happened through drag and drop
    if st.session_state.game_solved and st.session_state.game_active and not st.session_state.is_replaying:
        st.balloons()
        st.success(f"Congratulations! You solved the puzzle in {st.session_state.move_count} moves out of your committed {st.session_state.committed_moves}!")
        
        # Get player name from session state - ensure it's not empty
        player_name = st.session_state.player_name if st.session_state.player_name else "Anonymous"
        
        # Compare with algorithms - pass the player name
        compare_algorithms(player_name, st.session_state.disk_count, 
                         st.session_state.move_count, st.session_state.move_sequence)
        
        # Reset game
        st.session_state.game_active = False
        st.session_state.game_solved = False

    if menu == "Play Tower of Hanoi":
        st.header("Play Tower of Hanoi")
        
        # Two-step game setup process
        if not st.session_state.game_active:
            # Step 1: Set up player name and pegs, generate disk count
            if not st.session_state.disk_count_generated:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Store the player name in session state when entered
                    player_name = st.text_input("Your Name", value=st.session_state.player_name, key="name_input")
                    st.session_state.player_name = player_name  # Update session state with latest input
                    
                    # Number of pegs selection
                    peg_count = st.radio("Number of Pegs", [3, 4], key="peg_selection_input")
                    st.session_state.peg_selection = peg_count
                
                with col2:
                    st.write("**First, we'll generate the disk count for your game.**")
                    
                    # Generate disk count button
                    if st.button("Generate Disk Count", key="generate_disk_count"):
                        generate_game_parameters()
            
            # Step 2: Show disk count and ask for move commitment
            elif st.session_state.disk_count_generated and not st.session_state.setup_complete:
                st.info(f"Game with {st.session_state.disk_count} disks and {st.session_state.peg_count} pegs")
                
                # Player commits to a number of moves
                st.write("**Now commit to solving the puzzle with a specific number of moves:**")
                st.write("(You won't be able to change this after starting!)")
                
                # Let player choose any number of moves
                move_commitment = st.number_input("Number of Moves", 
                                                min_value=1, 
                                                value=20, 
                                                key="move_commitment_input")
                st.session_state.move_commitment = move_commitment
                
                # Start button
                if st.button("Start Game With Commitment", key="start_game_commitment"):
                    setup_game()
        
        # Display game if active
        if st.session_state.game_active:
            # Display replay status if replaying
            if st.session_state.is_replaying:
                progress = st.session_state.current_replay_index / len(st.session_state.replay_moves)
                st.progress(progress)
                st.write(f"Replaying moves: {st.session_state.current_replay_index} of {len(st.session_state.replay_moves)}")
            
            # Display replay errors if any
            if st.session_state.replay_error:
                st.error(st.session_state.replay_error)
            
            # Display game info
            st.write(f"Current game: {st.session_state.disk_count} disks with {st.session_state.peg_count} pegs")
            st.write(f"**You committed to solving this in {st.session_state.committed_moves} moves**")
            st.write(f"Moves made so far: {st.session_state.move_count} / {st.session_state.committed_moves}")
            
            # Progress bar for moves
            move_progress = st.session_state.move_count / st.session_state.committed_moves
            st.progress(move_progress)
            
            # Display the move sequence
            if st.session_state.moves_made:
                st.write("Move sequence: " + ", ".join(st.session_state.moves_made))
            
            # Display the game board with drag and drop enabled
            render_game_board(st.session_state.game_state, st.session_state.disk_count, st.session_state.peg_count)
            
            # Display any move errors or game lost state
            if st.session_state.move_error:
                st.error(st.session_state.move_error)
            
            if st.session_state.game_lost:
                st.error(f"Game Over! You failed to solve the puzzle in your committed {st.session_state.committed_moves} moves.")
                
                # Add option to start a new game after losing
                if st.button("Start New Game", key="start_game_after_loss"):
                    st.session_state.game_active = False
                    st.session_state.setup_complete = False
                    st.session_state.disk_count_generated = False
                    st.session_state.game_lost = False
                    st.rerun()
            
            # If not replaying and not lost, show the move controls
            if not st.session_state.is_replaying and not st.session_state.game_lost:
                # Move input (as alternative to drag and drop)
                st.subheader("Make a Move")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    source_options = ['A', 'B', 'C', 'D'][:st.session_state.peg_count]
                    st.selectbox("From Peg", source_options, key="source_peg")
                
                with col2:
                    dest_options = ['A', 'B', 'C', 'D'][:st.session_state.peg_count]
                    st.selectbox("To Peg", dest_options, key="destination_peg")
                
                with col3:
                    st.button("Make Move", on_click=make_move_callback, key="make_move_button")
                
                # Option to enter full move sequence
                st.subheader("Enter Full Solution")
                
                # Use the generated sequence as a default if available
                default_sequence = st.session_state.move_sequence if st.session_state.move_sequence else ""
                move_sequence = st.text_input(f"Move Sequence (e.g., A->B,B->C,A->C) - Max {st.session_state.committed_moves} moves", 
                                            value=default_sequence, key="move_sequence_input")
                
                # Add state variables for sequence submission
                st.session_state.solution_sequence = move_sequence
                    
                if 'solution_error' not in st.session_state:
                    st.session_state.solution_error = None
                    
                if 'solution_success' not in st.session_state:
                    st.session_state.solution_success = False
                
                # Submit button with callback
                st.button("Submit Solution", on_click=submit_solution, key="submit_solution_button")
                
                # Handle solution errors
                if st.session_state.solution_error:
                    st.error(st.session_state.solution_error)
                    st.session_state.solution_error = None
            
            # If replay is complete, show success message
            if st.session_state.replay_complete:
                st.balloons()
                st.success(f"Your solution is correct! Completed in {st.session_state.move_count} moves out of your committed {st.session_state.committed_moves}.")
                
                # Get player name from session state - ensure it's not empty
                player_name = st.session_state.player_name if st.session_state.player_name else "Anonymous"
                
                # Compare with algorithms - pass the player name
                compare_algorithms(player_name, st.session_state.disk_count, 
                                 st.session_state.move_count, st.session_state.move_sequence)
                
                # Add a button to start a new game
                if st.button("Start New Game", key="start_game_after_win"):
                    st.session_state.game_active = False
                    st.session_state.setup_complete = False
                    st.session_state.disk_count_generated = False
                    st.session_state.replay_complete = False
                    st.rerun()
    
    elif menu == "Leaderboard":
        st.header("Leaderboard")
        leaderboard = get_leaderboard()
        st.dataframe(leaderboard)
    
    elif menu == "Algorithm Comparison":
        st.header("Algorithm Comparison")
        
        # Compare algorithms for different disk counts
        st.subheader("Comparison by Disk Count")
        
        disk_count = st.slider("Number of Disks", min_value=3, max_value=20, value=10, key="disk_count_slider")
        
        if st.button("Run Comparison", key="run_comparison_button"):
            st.write("Running comparison...")
            
            # 3 pegs
            recursive_moves, recursive_time = solve_hanoi_recursive(disk_count, 'A', 'B', 'C')
            iterative_moves, iterative_time = solve_hanoi_iterative(disk_count, 'A', 'B', 'C')
            
            # 4 pegs
            fs_moves, fs_time = solve_frame_stewart(disk_count, 'A', 'B', 'C', 'D')
            
            # Results
            data = {
                'Algorithm': ['Recursive (3 pegs)', 'Iterative (3 pegs)', 'Frame-Stewart (4 pegs)'],
                'Move Count': [len(recursive_moves), len(iterative_moves), len(fs_moves)],
                'Execution Time (s)': [recursive_time, iterative_time, fs_time]
            }
            
            df = pd.DataFrame(data)
            st.dataframe(df)
            
            # Visualization
            st.subheader("Move Count Comparison")
            st.bar_chart(df.set_index('Algorithm')['Move Count'])
            
            st.subheader("Execution Time Comparison")
            st.bar_chart(df.set_index('Algorithm')['Execution Time (s)'])

if __name__ == "__main__":
    main()
#final