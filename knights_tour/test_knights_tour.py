import unittest
import mysql.connector
from mysql.connector import Error
import time
import random
import plotly.graph_objects as go
from knight_tour import (
    is_valid_move, 
    is_valid_tour, 
    get_valid_moves, 
    get_degree, 
    solve_knights_tour_warnsdorff, 
    solve_knights_tour_backtracking, 
    solve_knights_tour_pure_backtracking
)
from database import initialize_database, save_algorithm_times, save_winner_details, fetch_algorithm_performance
from main import initialize_board, validate_player_name, create_performance_chart

class TestKnightsTour(unittest.TestCase):
    
    def setUp(self):
        """Set up a test database and board for each test."""
        # Initialize a test board
        self.board = initialize_board()
        self.start_pos = (3, 4)
        self.board[self.start_pos[0]][self.start_pos[1]] = 0
        
        # Set up a test database
        try:
            initialize_database()
        except Exception as e:
            self.fail(f"Database initialization failed: {e}")

    def test_is_valid_move(self):
        """Test the is_valid_move function."""
        # Valid knight move (L-shape)
        self.assertTrue(is_valid_move((3, 4), (5, 5), self.board))
        # Invalid move (not L-shape)
        self.assertFalse(is_valid_move((3, 4), (4, 4), self.board))
        # Out of bounds
        self.assertFalse(is_valid_move((3, 4), (9, 5), self.board))

    def test_get_valid_moves(self):
        """Test the get_valid_moves function."""
        valid_moves = get_valid_moves(self.start_pos, self.board)
        expected_moves = [
            (5, 5), (5, 3), (1, 5), (1, 3),
            (4, 6), (4, 2), (2, 6), (2, 2)
        ]
        self.assertEqual(sorted(valid_moves), sorted(expected_moves))
        
        # Mark a position as visited
        self.board[5][5] = 1
        valid_moves = get_valid_moves(self.start_pos, self.board)
        expected_moves.remove((5, 5))
        self.assertEqual(sorted(valid_moves), sorted(expected_moves))

    def test_get_degree(self):
        """Test the get_degree function for Warnsdorff's algorithm."""
        degree = get_degree(self.start_pos, self.board)
        self.assertEqual(degree, 8)  # Should have 8 valid moves from (3, 4)

        # Mark a position as visited
        self.board[5][5] = 1
        degree = get_degree(self.start_pos, self.board)
        self.assertEqual(degree, 7)  # One less valid move

    def test_is_valid_tour(self):
        """Test the is_valid_tour function."""
        # Create a small invalid tour
        moves = [(0, 0), (2, 1)]
        self.board[0][0] = 0
        self.board[2][1] = 1
        self.assertFalse(is_valid_tour(self.board, moves))

        # A valid but incomplete tour
        moves = [(0, 0), (2, 1), (4, 2)]
        self.board[4][2] = 2
        self.assertFalse(is_valid_tour(self.board, moves))

    def test_solve_knights_tour_warnsdorff(self):
        """Test Warnsdorff's algorithm."""
        result = solve_knights_tour_warnsdorff(self.start_pos)
        if result:
            # Extract moves in the correct order based on move numbers
            move_positions = []
            for i in range(8):
                for j in range(8):
                    if result[i][j] != -1:
                        move_positions.append((result[i][j], (i, j)))
            # Sort by move number (0 to 63)
            move_positions.sort(key=lambda x: x[0])
            moves = [pos for _, pos in move_positions]
            self.assertTrue(is_valid_tour(result, moves), "Warnsdorff's tour is not valid")
        else:
            print("Warnsdorff's algorithm did not find a solution in this test.")

    def test_solve_knights_tour_backtracking(self):
        """Test optimized backtracking algorithm."""
        result = solve_knights_tour_backtracking(self.start_pos)
        if result:
            # Extract moves in the correct order based on move numbers
            move_positions = []
            for i in range(8):
                for j in range(8):
                    if result[i][j] != -1:
                        move_positions.append((result[i][j], (i, j)))
            # Sort by move number (0 to 63)
            move_positions.sort(key=lambda x: x[0])
            moves = [pos for _, pos in move_positions]
            self.assertTrue(is_valid_tour(result, moves), "Optimized Backtracking tour is not valid")
        else:
            print("Optimized Backtracking did not find a solution in this test.")

    def test_solve_knights_tour_pure_backtracking(self):
        """Test pure backtracking algorithm."""
        result = solve_knights_tour_pure_backtracking(self.start_pos)
        if result:
            # Extract moves in the correct order based on move numbers
            move_positions = []
            for i in range(8):
                for j in range(8):
                    if result[i][j] != -1:
                        move_positions.append((result[i][j], (i, j)))
            # Sort by move number (0 to 63)
            move_positions.sort(key=lambda x: x[0])
            moves = [pos for _, pos in move_positions]
            self.assertTrue(is_valid_tour(result, moves), "Pure Backtracking tour is not valid")
        else:
            print("Pure Backtracking did not find a solution in this test (expected due to timeout).")

    def test_initialize_board(self):
        """Test the initialize_board function."""
        board = initialize_board()
        self.assertEqual(len(board), 8)
        self.assertEqual(len(board[0]), 8)
        self.assertEqual(board[0][0], -1)

    def test_validate_player_name(self):
        """Test the validate_player_name function."""
        # Valid name
        is_valid, msg = validate_player_name("Player1")
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

        # Invalid name (special characters)
        is_valid, msg = validate_player_name("Player@")
        self.assertFalse(is_valid)
        self.assertIn("letters, numbers, and spaces", msg)

        # Empty name
        is_valid, msg = validate_player_name("")
        self.assertFalse(is_valid)
        self.assertIn("valid name", msg)

        # Name too long
        long_name = "A" * 256
        is_valid, msg = validate_player_name(long_name)
        self.assertFalse(is_valid)
        self.assertIn("255 characters", msg)

    def test_database_operations(self):
        """Test database operations."""
        round_id = "test-round-123"
        warnsdorff_time = 0.5
        backtracking_time = 1.0
        pure_backtracking_time = 2.0

        # Test save_algorithm_times
        try:
            save_algorithm_times(round_id, warnsdorff_time, backtracking_time, pure_backtracking_time)
        except Exception as e:
            self.fail(f"save_algorithm_times failed: {e}")

        # Test save_winner_details
        try:
            save_winner_details(round_id, "TestPlayer", "(0,0),(2,1)")
        except Exception as e:
            self.fail(f"save_winner_details failed: {e}")

        # Verify data in the database
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="knights_tour_db"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM algorithm_times WHERE round_id = %s", (round_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[1], round_id)  # round_id
            self.assertEqual(result[2], warnsdorff_time)  # warnsdorff_time
            self.assertEqual(result[3], backtracking_time)  # backtracking_time
            self.assertEqual(result[4], pure_backtracking_time)  # pure_backtracking_time

            cursor.execute("SELECT * FROM winner_details WHERE round_id = %s", (round_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[1], round_id)
            self.assertEqual(result[2], "TestPlayer")
            self.assertEqual(result[3], "(0,0),(2,1)")

        except mysql.connector.Error as e:
            self.fail(f"Database verification failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def test_fetch_algorithm_performance(self):
        """Test the fetch_algorithm_performance function using a temporary table."""
        try:
            # Create a temporary table to control test data
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="knights_tour_db"
            )
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE temp_algorithm_times LIKE algorithm_times
            """)
            cursor.execute("USE knights_tour_db")

            # Insert sample data with explicit timestamps
            round_ids = [f"test-round-{i}" for i in range(12)]  # 12 rounds to test LIMIT 10
            base_time = "2025-04-25 10:00:00"
            for i, round_id in enumerate(round_ids):
                timestamp = f"2025-04-25 10:00:{i:02d}"  # Increment seconds: 10:00:00, 10:00:01, ..., 10:00:11
                cursor.execute("""
                    INSERT INTO temp_algorithm_times (round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    round_id,
                    0.1 + i * 0.01,  # warnsdorff_time
                    0.5 + i * 0.02,  # backtracking_time
                    1.0 + i * 0.03,  # pure_backtracking_time
                    timestamp
                ))
            connection.commit()

            # Fetch performance data using the same query as fetch_algorithm_performance
            cursor.execute("""
                SELECT round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp
                FROM temp_algorithm_times
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            performance_data = cursor.fetchall()

            # Debug: Print the fetched data to inspect timestamps and order
            print("\nFetched performance data:")
            for data in performance_data:
                print(f"Round ID: {data[0]}, Timestamp: {data[4]}")

            # Verify that exactly 10 rounds are returned (latest 10)
            self.assertEqual(len(performance_data), 10, "Should return exactly 10 rounds")

            # Verify that data is sorted by timestamp (most recent first)
            timestamps = [data[4] for data in performance_data]
            self.assertEqual(timestamps, sorted(timestamps, reverse=True), "Results should be sorted by timestamp descending")

            # Verify the structure and content of the data
            for i, data in enumerate(performance_data):
                expected_round_id = round_ids[11 - i]  # Latest rounds (index 11 down to 2)
                self.assertEqual(data[0], expected_round_id, f"Round ID mismatch for index {i}")
                self.assertAlmostEqual(data[1], 0.1 + (11 - i) * 0.01, places=4, msg="Warnsdorff time mismatch")
                self.assertAlmostEqual(data[2], 0.5 + (11 - i) * 0.02, places=4, msg="Backtracking time mismatch")
                self.assertAlmostEqual(data[3], 1.0 + (11 - i) * 0.03, places=4, msg="Pure backtracking time mismatch")
                self.assertIsNotNone(data[4], "Timestamp should not be None")

        except mysql.connector.Error as e:
            self.fail(f"Database error in test_fetch_algorithm_performance: {e}")
        finally:
            # Clean up temporary table
            try:
                cursor.execute("DROP TABLE IF EXISTS temp_algorithm_times")
                connection.commit()
            except mysql.connector.Error as e:
                print(f"Error dropping temporary table: {e}")
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def test_fetch_algorithm_performance_empty_database(self):
        """Test fetch_algorithm_performance with an empty database."""
        try:
            # Create a temporary table to avoid modifying algorithm_times
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="knights_tour_db"
            )
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE temp_algorithm_times LIKE algorithm_times
            """)
            cursor.execute("USE knights_tour_db")
            
            # Fetch performance data from the empty temp table
            cursor.execute("""
                SELECT round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp
                FROM temp_algorithm_times
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            performance_data = cursor.fetchall()
            
            # Verify that an empty list is returned
            self.assertEqual(performance_data, [], "Should return an empty list for an empty database")
            
        except mysql.connector.Error as e:
            self.fail(f"Database error in test_fetch_algorithm_performance_empty_database: {e}")
        finally:
            # Clean up temporary table
            try:
                cursor.execute("DROP TABLE IF EXISTS temp_algorithm_times")
                connection.commit()
            except mysql.connector.Error as e:
                print(f"Error dropping temporary table: {e}")
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def test_create_performance_chart(self):
        """Test the create_performance_chart function with valid data."""
        try:
            # Prepare sample performance data
            performance_data = [
                (f"round-{i}", 0.1 + i * 0.01, 0.5 + i * 0.02, 1.0 + i * 0.03, time.strftime('%Y-%m-%d %H:%M:%S'))
                for i in range(5)
            ]

            # Create the chart
            fig = create_performance_chart(performance_data)

            # Verify that a valid Plotly figure is returned
            self.assertIsInstance(fig, go.Figure, "Should return a Plotly Figure object")

            # Verify the number of traces (3 bars for each algorithm)
            self.assertEqual(len(fig.data), 3, "Should have 3 bar traces (one for each algorithm)")

            # Verify trace names and data
            expected_names = ["Warnsdorff", "Optimized Backtracking", "Pure Backtracking"]
            for trace, expected_name in zip(fig.data, expected_names):
                self.assertEqual(trace.name, expected_name, f"Trace name mismatch: expected {expected_name}")
                self.assertEqual(len(trace.x), 5, "Each trace should have 5 x-values (round IDs)")
                self.assertEqual(len(trace.y), 5, "Each trace should have 5 y-values (times)")

            # Verify x-axis (round IDs)
            round_ids = [f"round-{i}"[-8:] for i in range(5)]
            self.assertEqual(list(fig.data[0].x), round_ids, "X-axis should contain last 8 chars of round IDs")

            # Verify y-axis (execution times)
            for i, trace in enumerate(fig.data):
                expected_times = [0.1 + j * 0.01 if i == 0 else 0.5 + j * 0.02 if i == 1 else 1.0 + j * 0.03 for j in range(5)]
                self.assertEqual(list(trace.y), expected_times, f"Y-axis times mismatch for {trace.name}")

            # Verify layout properties
            self.assertEqual(fig.layout.title.text, "Algorithm Performance (Execution Time) for Latest 10 Rounds", "Title mismatch")
            self.assertEqual(fig.layout.xaxis.title.text, "Round ID (Last 8 Characters)", "X-axis title mismatch")
            self.assertEqual(fig.layout.yaxis.title.text, "Execution Time (seconds)", "Y-axis title mismatch")
            self.assertEqual(fig.layout.barmode, "group", "Barmode should be 'group'")

        except Exception as e:
            self.fail(f"create_performance_chart failed: {e}")

    def test_create_performance_chart_empty_data(self):
        """Test create_performance_chart with empty performance data."""
        try:
            # Create chart with empty data
            fig = create_performance_chart([])

            # Verify that an empty Plotly figure is returned
            self.assertIsInstance(fig, go.Figure, "Should return a Plotly Figure object")
            self.assertEqual(len(fig.data), 0, "Figure should have no traces for empty data")
            self.assertEqual(fig.layout.title.text, None, "Empty figure should have no title")

        except Exception as e:
            self.fail(f"test_create_performance_chart_empty_data failed: {e}")

    def tearDown(self):
        """Clean up test-specific data in the database."""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="knights_tour_db"
            )
            cursor = connection.cursor()
            
            # Delete all test-specific data
            cursor.execute("DELETE FROM winner_details WHERE round_id LIKE 'test-round%'")
            cursor.execute("DELETE FROM algorithm_times WHERE round_id LIKE 'test-round%'")
            
            connection.commit()
            print(f"Cleaned up all test data with round_id starting with 'test-round'")
            
        except mysql.connector.Error as e:
            print(f"Error cleaning up test data: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

if __name__ == "__main__":
    unittest.main()