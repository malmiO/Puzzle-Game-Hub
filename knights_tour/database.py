import mysql.connector
from mysql.connector import DatabaseError, InterfaceError, ProgrammingError

def initialize_database():
    connection = None
    cursor = None
    try:
        # Connect to MySQL server (without specifying a database)
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="",
            database="puzzle_game_hub"  
        )
        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS puzzle_game_hub")
        cursor.execute("USE puzzle_game_hub")
        print("Database 'puzzle_game_hub' selected.")

        # Create algorithm_times table with a unique constraint on round_id
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS knights_tour_algorithm_times (
                id INT AUTO_INCREMENT PRIMARY KEY,
                round_id VARCHAR(36) NOT NULL,
                warnsdorff_time FLOAT NOT NULL,
                backtracking_time FLOAT NOT NULL,
                pure_backtracking_time FLOAT NOT NULL,
                timestamp DATETIME NOT NULL,
                UNIQUE (round_id)
            )
        """)
        print("Table 'knights_tour_algorithm_times' created or already exists.")

        # Create winner_details table with a foreign key to algorithm_times(round_id)
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS knights_tour_winner_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                round_id VARCHAR(36) NOT NULL,
                player_name VARCHAR(255) NOT NULL,
                move_sequence TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (round_id) REFERENCES knights_tour_algorithm_times(round_id) ON DELETE CASCADE
            )
        """)
        print("Table 'knights_tour_winner_details' created or already exists.")

        connection.commit()

        # Verify that the tables exist
        cursor.execute("SHOW TABLES LIKE 'knights_tour_algorithm_times'")
        if not cursor.fetchone():
            raise DatabaseError("Failed to create 'knights_tour_algorithm_times' table.")

        cursor.execute("SHOW TABLES LIKE 'knights_tour_winner_details'")
        if not cursor.fetchone():
            raise DatabaseError("Failed to create 'knights_tour_winner_details' table.")

        print("Database initialization completed successfully.")

    except InterfaceError as e:
        print(f"Connection error during database initialization: {e}")
        raise
    except ProgrammingError as e:
        print(f"SQL syntax error during database initialization: {e}")
        raise
    except DatabaseError as e:
        print(f"Database error during initialization: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during database initialization: {e}")
        raise
    finally:
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                print("Database connection closed after initialization.")
        except Exception as e:
            print(f"Error closing database resources: {e}")

def save_algorithm_times(round_id, warnsdorff_time, backtracking_time, pure_backtracking_time):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="puzzle_game_hub"
        )
        cursor = connection.cursor()

        # Verify that the table exists
        cursor.execute("SHOW TABLES LIKE 'knights_tour_algorithm_times'")
        if not cursor.fetchone():
            raise DatabaseError("Table 'knights_tour_algorithm_times' does not exist in database 'puzzle_game_hub'.")

        # Check if a record exists for the round_id
        cursor.execute("SELECT id FROM knights_tour_algorithm_times WHERE round_id = %s", (round_id,))
        result = cursor.fetchone()
        
        if result:
            # Update the existing record
            query = """
            UPDATE knights_tour_algorithm_times 
            SET warnsdorff_time = %s, backtracking_time = %s, pure_backtracking_time = %s, timestamp = NOW()
            WHERE round_id = %s
            """
            cursor.execute(query, (warnsdorff_time, backtracking_time, pure_backtracking_time, round_id))
            print(f"Updated algorithm times for round_id {round_id}.")
        else:
            # Insert a new record
            query = """
            INSERT INTO knights_tour_algorithm_times (round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (round_id, warnsdorff_time, backtracking_time, pure_backtracking_time))
            print(f"Inserted algorithm times for round_id {round_id}.")
        
        connection.commit()

    except InterfaceError as e:
        print(f"Connection error in save_algorithm_times: {e}")
        raise
    except ProgrammingError as e:
        print(f"SQL syntax error in save_algorithm_times: {e}")
        raise
    except DatabaseError as e:
        print(f"Database error in save_algorithm_times: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in save_algorithm_times: {e}")
        raise
    finally:
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                print("Database connection closed after saving algorithm times.")
        except Exception as e:
            print(f"Error closing database resources: {e}")

def save_winner_details(round_id, player_name, move_sequence):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="puzzle_game_hub"
        )
        cursor = connection.cursor()

        # Verify that the table exists
        cursor.execute("SHOW TABLES LIKE 'knights_tour_winner_details'")
        if not cursor.fetchone():
            raise DatabaseError("Table 'knights_tour_winner_details' does not exist in database 'puzzle_game_hub'.")

        query = """
        INSERT INTO knights_tour_winner_details (round_id, player_name, move_sequence, timestamp)
        VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(query, (round_id, player_name, move_sequence))
        connection.commit()
        print(f"Saved knight's tour winner details for round_id {round_id}.")

    except InterfaceError as e:
        print(f"Connection error in save_winner_details: {e}")
        raise
    except ProgrammingError as e:
        print(f"SQL syntax error in save_winner_details: {e}")
        raise
    except DatabaseError as e:
        print(f"Database error in save_winner_details: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in save_winner_details: {e}")
        raise
    finally:
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                print("Database connection closed after saving winner details.")
        except Exception as e:
            print(f"Error closing database resources: {e}")

def fetch_algorithm_performance():
    """Fetch performance data for the latest 10 game rounds from the database."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="puzzle_game_hub"
        )
        cursor = connection.cursor()
        query = """
        SELECT round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp
        FROM knights_tour_algorithm_times
        ORDER BY timestamp DESC
        LIMIT 10
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except InterfaceError as e:
        print(f"Connection error in fetch_algorithm_performance: {e}")
        raise
    except ProgrammingError as e:
        print(f"SQL syntax error in fetch_algorithm_performance: {e}")
        raise
    except DatabaseError as e:
        print(f"Database error in fetch_algorithm_performance: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error in fetch_algorithm_performance: {e}")
        raise
    finally:
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                print("Database connection closed after fetching performance data.")
        except Exception as e:
            print(f"Error closing database resources: {e}")

# Initialize the database when the module is imported
try:
    initialize_database()
except Exception as e:
    print(f"Failed to initialize database: {e}")
    raise