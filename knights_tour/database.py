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
<<<<<<< HEAD
            database="puzzle_game_hub"  
=======
            database="knights_tour_db"  
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
        )
        cursor = connection.cursor()

        # Create database if it doesn't exist
<<<<<<< HEAD
        cursor.execute("CREATE DATABASE IF NOT EXISTS puzzle_game_hub")
        cursor.execute("USE puzzle_game_hub")
        print("Database 'puzzle_game_hub' selected.")

        # Create algorithm_times table with a unique constraint on round_id
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS knights_tour_algorithm_times (
=======
        cursor.execute("CREATE DATABASE IF NOT EXISTS knights_tour_db")
        cursor.execute("USE knights_tour_db")
        print("Database 'knights_tour_db' selected.")

        # Create algorithm_times table with a unique constraint on round_id
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS algorithm_times (
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
                id INT AUTO_INCREMENT PRIMARY KEY,
                round_id VARCHAR(36) NOT NULL,
                warnsdorff_time FLOAT NOT NULL,
                backtracking_time FLOAT NOT NULL,
                pure_backtracking_time FLOAT NOT NULL,
                timestamp DATETIME NOT NULL,
                UNIQUE (round_id)
            )
        """)
<<<<<<< HEAD
        print("Table 'knights_tour_algorithm_times' created or already exists.")

        # Create winner_details table with a foreign key to algorithm_times(round_id)
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS knights_tour_winner_details (
=======
        print("Table 'algorithm_times' created or already exists.")

        # Create winner_details table with a foreign key to algorithm_times(round_id)
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS winner_details (
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
                id INT AUTO_INCREMENT PRIMARY KEY,
                round_id VARCHAR(36) NOT NULL,
                player_name VARCHAR(255) NOT NULL,
                move_sequence TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
<<<<<<< HEAD
                FOREIGN KEY (round_id) REFERENCES knights_tour_algorithm_times(round_id) ON DELETE CASCADE
            )
        """)
        print("Table 'knights_tour_winner_details' created or already exists.")
=======
                FOREIGN KEY (round_id) REFERENCES algorithm_times(round_id) ON DELETE CASCADE
            )
        """)
        print("Table 'winner_details' created or already exists.")
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3

        connection.commit()

        # Verify that the tables exist
<<<<<<< HEAD
        cursor.execute("SHOW TABLES LIKE 'knights_tour_algorithm_times'")
        if not cursor.fetchone():
            raise DatabaseError("Failed to create 'knights_tour_algorithm_times' table.")

        cursor.execute("SHOW TABLES LIKE 'knights_tour_winner_details'")
        if not cursor.fetchone():
            raise DatabaseError("Failed to create 'knights_tour_winner_details' table.")
=======
        cursor.execute("SHOW TABLES LIKE 'algorithm_times'")
        if not cursor.fetchone():
            raise DatabaseError("Failed to create 'algorithm_times' table.")

        cursor.execute("SHOW TABLES LIKE 'winner_details'")
        if not cursor.fetchone():
            raise DatabaseError("Failed to create 'winner_details' table.")
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3

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
<<<<<<< HEAD
            database="puzzle_game_hub"
=======
            database="knights_tour_db"
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
        )
        cursor = connection.cursor()

        # Verify that the table exists
<<<<<<< HEAD
        cursor.execute("SHOW TABLES LIKE 'knights_tour_algorithm_times'")
        if not cursor.fetchone():
            raise DatabaseError("Table 'knights_tour_algorithm_times' does not exist in database 'puzzle_game_hub'.")

        # Check if a record exists for the round_id
        cursor.execute("SELECT id FROM knights_tour_algorithm_times WHERE round_id = %s", (round_id,))
=======
        cursor.execute("SHOW TABLES LIKE 'algorithm_times'")
        if not cursor.fetchone():
            raise DatabaseError("Table 'algorithm_times' does not exist in database 'knights_tour_db'.")

        # Check if a record exists for the round_id
        cursor.execute("SELECT id FROM algorithm_times WHERE round_id = %s", (round_id,))
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
        result = cursor.fetchone()
        
        if result:
            # Update the existing record
            query = """
<<<<<<< HEAD
            UPDATE knights_tour_algorithm_times 
=======
            UPDATE algorithm_times 
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
            SET warnsdorff_time = %s, backtracking_time = %s, pure_backtracking_time = %s, timestamp = NOW()
            WHERE round_id = %s
            """
            cursor.execute(query, (warnsdorff_time, backtracking_time, pure_backtracking_time, round_id))
            print(f"Updated algorithm times for round_id {round_id}.")
        else:
            # Insert a new record
            query = """
<<<<<<< HEAD
            INSERT INTO knights_tour_algorithm_times (round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp)
=======
            INSERT INTO algorithm_times (round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp)
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
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
<<<<<<< HEAD
            database="puzzle_game_hub"
=======
            database="knights_tour_db"
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
        )
        cursor = connection.cursor()

        # Verify that the table exists
<<<<<<< HEAD
        cursor.execute("SHOW TABLES LIKE 'knights_tour_winner_details'")
        if not cursor.fetchone():
            raise DatabaseError("Table 'knights_tour_winner_details' does not exist in database 'puzzle_game_hub'.")

        query = """
        INSERT INTO knights_tour_winner_details (round_id, player_name, move_sequence, timestamp)
=======
        cursor.execute("SHOW TABLES LIKE 'winner_details'")
        if not cursor.fetchone():
            raise DatabaseError("Table 'winner_details' does not exist in database 'knights_tour_db'.")

        query = """
        INSERT INTO winner_details (round_id, player_name, move_sequence, timestamp)
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
        VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(query, (round_id, player_name, move_sequence))
        connection.commit()
<<<<<<< HEAD
        print(f"Saved knight's tour winner details for round_id {round_id}.")
=======
        print(f"Saved winner details for round_id {round_id}.")
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3

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
<<<<<<< HEAD
            database="puzzle_game_hub"
=======
            database="knights_tour_db"
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
        )
        cursor = connection.cursor()
        query = """
        SELECT round_id, warnsdorff_time, backtracking_time, pure_backtracking_time, timestamp
<<<<<<< HEAD
        FROM knights_tour_algorithm_times
=======
        FROM algorithm_times
>>>>>>> c9287701bef99bcb586a58d27c077d1da6ced8f3
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