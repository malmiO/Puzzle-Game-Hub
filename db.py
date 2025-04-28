import mysql.connector
import json
from datetime import datetime

# Establish connection to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change this to your MySQL username
        password="",  # Change this to your MySQL password
        database="eight_queens"  # Ensure this database exists in MySQL
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS solutions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        method VARCHAR(255),
        time_taken FLOAT,
        total_solutions INT,
        solutions TEXT,
        created_at DATETIME
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        player_name VARCHAR(255),
        correct_solution TEXT,
        created_at DATETIME
    )''')

    conn.commit()
    conn.close()

def save_player_answer(player_name, correct_solution):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO player_answers (player_name, correct_solution, created_at)
    VALUES (%s, %s, %s)
    ''', 
    (player_name, json.dumps(correct_solution), datetime.now()))

    conn.commit()
    conn.close()

def solution_exists(method):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM solutions WHERE method = %s", (method,))
    exists = cursor.fetchone()[0] > 0

    conn.close()
    return exists

def save_to_db(method, time_taken, solutions):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for duplicate
    cursor.execute("SELECT solutions FROM solutions WHERE method = %s", (method,))
    existing = [json.loads(row[0]) for row in cursor.fetchall()]

    if solutions in existing:
        conn.close()
        return  # Don't save duplicate solutions

    total_solutions = len(solutions)

    cursor.execute('''
    INSERT INTO solutions (method, time_taken, total_solutions, solutions, created_at)
    VALUES (%s, %s, %s, %s, %s)
    ''', 
    (method, time_taken, total_solutions, json.dumps(solutions), datetime.now()))

    conn.commit()
    conn.close()

def player_solution_exists(player_name, solution):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT COUNT(*) FROM player_answers WHERE player_name = %s AND correct_solution = %s
    ''', 
    (player_name, json.dumps(solution)))

    exists = cursor.fetchone()[0] > 0

    conn.close()
    return exists

def get_recognized_solutions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT correct_solution FROM player_answers WHERE correct_solution IS NOT NULL")
    recognized_solutions = [json.loads(row[0]) for row in cursor.fetchall()]

    conn.close()
    return recognized_solutions

def is_solution_recognized(solution):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM player_answers WHERE correct_solution = %s", (json.dumps(solution),))
    exists = cursor.fetchone()[0] > 0

    conn.close()
    return exists

def count_unique_player_solutions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT correct_solution FROM player_answers WHERE correct_solution IS NOT NULL")
    unique_solutions = set(row[0] for row in cursor.fetchall())

    conn.close()
    return len(unique_solutions)

def reset_player_solutions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM player_answers")
    conn.commit()
    conn.close()