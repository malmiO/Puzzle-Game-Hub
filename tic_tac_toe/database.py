import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError

# Database configuration for SQLAlchemy
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "puzzle_game_hub",
}

# Create SQLAlchemy engine
try:
    connection_string = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    engine = create_engine(connection_string, echo=False)
except OperationalError as e:
    st.error(f"Failed to create database engine: {e}")
    engine = None


def initialize_database():
    if engine is None:
        st.error("Database engine not initialized. Cannot proceed with database setup.")
        return

    try:
        # Create database if it doesn't exist
        temp_engine = create_engine(
            f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}"
        )
        with temp_engine.connect() as conn:
            conn.execute(text("CREATE DATABASE IF NOT EXISTS puzzle_game_hub"))
            conn.execute(text("USE puzzle_game_hub"))

        with engine.connect() as conn:
            # Create combined games table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS tic_tac_toe_games (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_name VARCHAR(255) NOT NULL,
                    result VARCHAR(50) NOT NULL,
                    moves TEXT,
                    game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create algorithm_performance table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS tic_tac_toe_algorithm_performance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    game_id INT NULL,
                    move_number INT NOT NULL,
                    greedy_time FLOAT NOT NULL,
                    minimax_time FLOAT NOT NULL
                )
            """
                )
            )

            conn.commit()
    except OperationalError as e:
        st.error(f"Database connection error: {e}")
    except ProgrammingError as e:
        st.error(f"Database query error: {e}")
    except SQLAlchemyError as e:
        st.error(f"General database error during initialization: {e}")
    except Exception as e:
        st.error(f"Unexpected error during database initialization: {e}")


def save_game_moves(game_id: int, player_name: str, result: str, moves: list) -> int:
    if engine is None:
        st.error("Database engine not initialized.")
        return None

    try:
        with engine.connect() as conn:
            # Convert moves list to a string
            moves_str = str(moves) if moves else "[]"

            if game_id is None:
                # Insert new game record
                result_obj = conn.execute(
                    text(
                        "INSERT INTO tic_tac_toe_games (player_name, result, moves) VALUES (:player_name, :result, :moves)"
                    ),
                    {"player_name": player_name, "result": result, "moves": moves_str},
                )
                game_id = result_obj.lastrowid
            else:
                # Update existing game record
                conn.execute(
                    text(
                        "UPDATE tic_tac_toe_games SET player_name = :player_name, result = :result, moves = :moves WHERE id = :game_id"
                    ),
                    {
                        "player_name": player_name,
                        "result": result,
                        "moves": moves_str,
                        "game_id": game_id,
                    },
                )

            conn.commit()
            return game_id
    except OperationalError as e:
        st.error(f"Database connection error while saving game moves: {e}")
        return None
    except ProgrammingError as e:
        st.error(f"Database query error while saving game moves: {e}")
        return None
    except SQLAlchemyError as e:
        st.error(f"General database error while saving game moves: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error while saving game moves: {e}")
        return None


def save_algorithm_performance(
    game_id: int,
    move_number: int,
    greedy_time: float,
    minimax_time: float,
    update_game_id: bool = False,
):
    if engine is None:
        st.error("Database engine not initialized.")
        return

    try:
        with engine.connect() as conn:
            if update_game_id:
                # Update existing algorithm_performance entries
                conn.execute(
                    text(
                        "UPDATE tic_tac_toe_algorithm_performance SET game_id = :game_id WHERE game_id IS NULL"
                    ),
                    {"game_id": game_id},
                )
            else:
                # Insert new performance record
                conn.execute(
                    text(
                        "INSERT INTO tic_tac_toe_algorithm_performance (game_id, move_number, greedy_time, minimax_time) VALUES (:game_id, :move_number, :greedy_time, :minimax_time)"
                    ),
                    {
                        "game_id": game_id,
                        "move_number": move_number,
                        "greedy_time": greedy_time,
                        "minimax_time": minimax_time,
                    },
                )
            conn.commit()
    except OperationalError as e:
        st.error(f"Database connection error while saving performance: {e}")
    except ProgrammingError as e:
        st.error(f"Database query error while saving performance: {e}")
    except SQLAlchemyError as e:
        st.error(f"General database error while saving performance: {e}")
    except Exception as e:
        st.error(f"Unexpected error while saving performance: {e}")


def get_performance_data(limit=10):
    if engine is None:
        st.error("Database engine not initialized.")
        return pd.DataFrame()

    try:
        query = """
            SELECT 
                g.id AS game_id,
                SUM(ap.greedy_time) AS total_greedy_time,
                SUM(ap.minimax_time) AS total_minimax_time
            FROM tic_tac_toe_games g
            JOIN tic_tac_toe_algorithm_performance ap ON g.id = ap.game_id
            GROUP BY g.id
            ORDER BY g.game_date DESC
            LIMIT :limit
        """

        df = pd.read_sql(text(query), engine, params={"limit": limit})
        if df.empty:
            return pd.DataFrame()

        # Create a sequential index for the x-axis (1 to 10)
        df["game_number"] = range(1, len(df) + 1)

        # Melt the DataFrame for plotting
        df_melted = pd.melt(
            df,
            id_vars=["game_number"],
            value_vars=["total_greedy_time", "total_minimax_time"],
            var_name="algorithm",
            value_name="time_taken",
        )
        df_melted["algorithm"] = df_melted["algorithm"].replace(
            {"total_greedy_time": "Greedy", "total_minimax_time": "Minimax"}
        )
        return df_melted
    except OperationalError as e:
        st.error(f"Database connection error while fetching performance data: {e}")
        return pd.DataFrame()
    except ProgrammingError as e:
        st.error(f"Database query error while fetching performance data: {e}")
        return pd.DataFrame()
    except SQLAlchemyError as e:
        st.error(f"General database error while fetching performance data: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error while fetching performance data: {e}")
        return pd.DataFrame()
