import streamlit as st
import mysql.connector
import pandas as pd

# Page setup
st.set_page_config(
    page_title="Scoreboard - Puzzle Game Hub",
    page_icon="🏆",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom right, #0a0a0a, #1a1a1a);
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    
    .stDataFrame {
        background: #1c1c1c;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .footer {
        margin-top: 50px;
        padding: 20px 0;
        border-top: 1px solid #333333;
        color: #999999;
        font-size: 0.9rem;
        text-align: center;
    }

    /* Hide the top navigation menu */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>🏆 Scoreboard</h1>", unsafe_allow_html=True)

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="puzzle_game_hub"
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# Function to save fetched data to the scoreboard table
def save_to_scoreboard(df):
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Clear existing data in the scoreboard table
        cursor.execute("TRUNCATE TABLE scoreboard")
        
        # Insert fetched data into the scoreboard table
        insert_query = """
        INSERT INTO scoreboard (player_name, game_name, win_count)
        VALUES (%s, %s, %s)
        """
        for _, row in df.iterrows():
            cursor.execute(insert_query, (row["Player Name"], row["Game Name"], row["Win Count"]))
        
        connection.commit()
        print(f"Saved {len(df)} records to the scoreboard table.")
        
    except mysql.connector.Error as e:
        st.error(f"Error saving to scoreboard table: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Function to fetch win counts
def fetch_win_counts():
    connection = get_db_connection()
    if not connection:
        return pd.DataFrame(columns=["Player Name", "Game Name", "Win Count"])
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Tic-Tac-Toe wins
        ttt_query = """
        SELECT player_name AS 'Player Name', 'Tic-Tac-Toe' AS 'Game Name', COUNT(*) AS 'Win Count'
        FROM tic_tac_toe_games
        WHERE result = 'Win'
        GROUP BY player_name
        """
        
        # TSP wins
        tsp_query = """
        SELECT player_name AS 'Player Name', 'Traveling Salesman Problem' AS 'Game Name', COUNT(*) AS 'Win Count'
        FROM tsp_game_results
        WHERE is_optimal = TRUE
        GROUP BY player_name
        """
        
        # Tower of Hanoi wins (optimal moves: 2^disk_count - 1)
        toh_query = """
        SELECT player_name AS 'Player Name', 'Tower of Hanoi' AS 'Game Name', COUNT(*) AS 'Win Count'
        FROM tower_of_hanoi_user_games
        WHERE moves_count = (POW(2, disk_count) - 1)
        GROUP BY player_name
        """
        
        # Knight's Tour wins
        kt_query = """
        SELECT player_name AS 'Player Name', 'Knight''s Tour Problem' AS 'Game Name', COUNT(*) AS 'Win Count'
        FROM knights_tour_winner_details
        GROUP BY player_name
        """
        
        # Eight Queens wins
        eq_query = """
        SELECT player_name AS 'Player Name', 'Eight Queens Puzzle' AS 'Game Name', COUNT(*) AS 'Win Count'
        FROM player_answers
        WHERE correct_solution IS NOT NULL   -- or another condition that marks a correct solution
        GROUP BY player_name
        """


        
        # Combine results
        queries = [ttt_query, tsp_query, toh_query, kt_query, eq_query]
        dfs = []
        
        for query in queries:
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    dfs.append(pd.DataFrame(results))
            except mysql.connector.Error as e:
                st.warning(f"Error fetching data for a game: {e}")
                continue
        
        cursor.close()
        connection.close()
        
        if not dfs:
            return pd.DataFrame(columns=["Player Name", "Game Name", "Win Count"])
        
        # Concatenate and sort
        result_df = pd.concat(dfs, ignore_index=True)
        result_df = result_df.groupby(["Player Name", "Game Name"], as_index=False)["Win Count"].sum()
        result_df = result_df.sort_values(by="Win Count", ascending=False)
        
        # Save the fetched data to the scoreboard table
        save_to_scoreboard(result_df)
        
        return result_df
    
    except mysql.connector.Error as e:
        st.error(f"Error fetching win counts: {e}")
        return pd.DataFrame(columns=["Player Name", "Game Name", "Win Count"])
    finally:
        if connection and connection.is_connected():
            connection.close()

# Display scoreboard
scoreboard_df = fetch_win_counts()
if not scoreboard_df.empty:
    st.dataframe(
        scoreboard_df,
        hide_index=True,
        column_config={
            "Player Name": st.column_config.TextColumn("Player"),
            "Game Name": st.column_config.TextColumn("Game"),
            "Win Count": st.column_config.NumberColumn("Wins", format="%d")
        },
        use_container_width=True
    )
else:
    st.write("No wins recorded yet.")

# Button to return to home page
if st.button("Back to Home"):
    st.switch_page("main.py")

# Footer
st.markdown("<div class='footer'>© 2025 Game Collection Team | All Rights Reserved</div>", unsafe_allow_html=True)