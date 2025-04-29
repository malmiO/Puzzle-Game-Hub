import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="puzzle_game_hub"
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def initialize_scoreboard_table():
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Create scoreboard table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS scoreboard (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_name VARCHAR(255) NOT NULL,
            game_name VARCHAR(255) NOT NULL,
            win_count INT NOT NULL DEFAULT 0,
            UNIQUE KEY unique_player_game (player_name(100), game_name(100))
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("scoreboard table created successfully.")
        
    except Error as e:
        print(f"Error initializing scoreboard table: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    initialize_scoreboard_table()