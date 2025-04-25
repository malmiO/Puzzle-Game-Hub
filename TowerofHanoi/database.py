import pymysql
import pandas as pd
from datetime import datetime

def init_db():
    conn = pymysql.connect(
        host='localhost',
        user='root', 
        password='', 
        charset='utf8mb4'
    )
    c = conn.cursor()
    
    # Create the database if it doesn't exist
    c.execute('CREATE DATABASE IF NOT EXISTS tower_of_hanoi')
    c.execute('USE tower_of_hanoi')
    
    # Create tables
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_games (
        game_id INT AUTO_INCREMENT PRIMARY KEY,
        player_name VARCHAR(255) NOT NULL,
        disk_count INT NOT NULL,
        moves_count INT NOT NULL,
        move_sequence TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS algorithm_performance (
        test_id INT AUTO_INCREMENT PRIMARY KEY,
        algorithm VARCHAR(255) NOT NULL,
        disk_count INT NOT NULL,
        execution_time FLOAT NOT NULL,
        moves_count INT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        parameters TEXT NULL,
        notes TEXT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def save_user_game(player_name, disk_count, moves_count, move_sequence):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tower_of_hanoi',
        charset='utf8mb4'
    )
    c = conn.cursor()
    c.execute('''
    INSERT INTO user_games (player_name, disk_count, moves_count, move_sequence)
    VALUES (%s, %s, %s, %s)
    ''', (player_name, disk_count, moves_count, move_sequence))
    conn.commit()
    conn.close()
# Add these wrapper functions to maintain compatibility
def save_result(player_name, disk_count, moves_count, move_sequence, algorithm_name, execution_time):
    """
    Wrapper function to maintain compatibility with app.py
    Routes to the appropriate function based on algorithm_name
    """
    if algorithm_name.startswith("Player Solution"):
        # For player results
        save_user_game(player_name, disk_count, moves_count, move_sequence)
    else:
        # For algorithm results
        save_algorithm_performance(algorithm_name, disk_count, execution_time, moves_count, 
                                  parameters=move_sequence if move_sequence else None)

def get_leaderboard():
    """
    Wrapper function to maintain compatibility with app.py
    """
    # This returns the user leaderboard, but you could modify this 
    # to return a combined leaderboard of users and algorithms if desired
    return get_user_leaderboard()

def save_algorithm_performance(algorithm, disk_count, execution_time, moves_count, parameters=None, notes=None):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tower_of_hanoi',
        charset='utf8mb4'
    )
    c = conn.cursor()
    c.execute('''
    INSERT INTO algorithm_performance (algorithm, disk_count, execution_time, moves_count, parameters, notes)
    VALUES (%s, %s, %s, %s, %s, %s)
    ''', (algorithm, disk_count, execution_time, moves_count, parameters, notes))
    conn.commit()
    conn.close()

def get_user_leaderboard():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tower_of_hanoi',
        charset='utf8mb4'
    )
    query = '''
    SELECT player_name, disk_count, moves_count, timestamp 
    FROM user_games 
    ORDER BY moves_count ASC, timestamp ASC
    LIMIT 10
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_algorithm_benchmarks():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tower_of_hanoi',
        charset='utf8mb4'
    )
    query = '''
    SELECT algorithm, disk_count, execution_time, moves_count, timestamp 
    FROM algorithm_performance 
    ORDER BY disk_count ASC, execution_time ASC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df