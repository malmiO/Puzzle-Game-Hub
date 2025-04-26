import streamlit as st
import base64
from PIL import Image
import numpy as np

# Set page configuration with dark theme
st.set_page_config(
    page_title="Classic Games Collection",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and better styling
st.markdown("""
<style>
    .main {
        background-color: #121212;
        color: white;
    }
    
    h1, h2, h3, h4 {
        color: white !important;
    }
    
    .stButton>button {
        color: white;
        background-color: #333333;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #555555;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .game-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        transition: all 0.3s;
    }
    
    .game-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    
    .game-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 5px;
    }
    
    .game-creator {
        color: #aaaaaa;
        font-size: 0.8rem;
    }
    
    .category-label {
        background-color: #444444;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.7rem;
        margin-right: 5px;
    }
    
    .filter-container {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .footer {
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #333333;
        color: #999999;
        font-size: 0.8rem;
        text-align: center;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Function to generate placeholder images for games
def get_placeholder_image(seed, width=400, height=225):
    # Generate a random image based on seed
    np.random.seed(seed)
    imarray = np.random.rand(height, width, 3) * 255
    # Make the image dark with some color theme
    theme_color = np.array([30, 60, 90]) + np.random.rand(3) * 50
    imarray = (imarray * 0.2) + theme_color
    imarray = imarray.astype(np.uint8)
    return Image.fromarray(imarray)

# Game data with metadata
games = [
    {
        "title": "Tic Tac Toe",
        "description": "Classic two-player game where you try to get three in a row.",
        "creator": "Team Member 1",
        "category": "Strategy",
        "difficulty": "Easy",
        "players": "2 Players",
        "file": "tictactoe_game.py",
        "seed": 42
    },
    {
        "title": "Traveling Salesman Problem",
        "description": "Find the shortest possible route that visits each city once and returns to the origin.",
        "creator": "Team Member 2",
        "category": "Puzzle",
        "difficulty": "Hard",
        "players": "1 Player",
        "file": "traveling_salesman.py",
        "seed": 123
    },
    {
        "title": "Tower of Hanoi",
        "description": "Move the entire stack of disks to another rod following specific rules.",
        "creator": "Team Member 3",
        "category": "Puzzle",
        "difficulty": "Medium",
        "players": "1 Player",
        "file": "tower_of_hanoi.py",
        "seed": 234
    },
    {
        "title": "Eight Queens Puzzle",
        "description": "Place eight chess queens on an 8×8 chessboard so that no two queens threaten each other.",
        "creator": "Team Member 4",
        "category": "Puzzle",
        "difficulty": "Hard",
        "players": "1 Player",
        "file": "eight_queens.py",
        "seed": 345
    },
    {
        "title": "Knight's Tour Problem",
        "description": "Find a sequence of moves for a knight to visit every square on a chessboard exactly once.",
        "creator": "Team Member 5",
        "category": "Puzzle",
        "difficulty": "Hard",
        "players": "1 Player",
        "file": "knights_tour.py",
        "seed": 456
    }
]

# Main title section
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Classic Games Collection</h1>", unsafe_allow_html=True)

st.markdown("""
<p style='text-align: center; font-size: 1.2rem; margin-bottom: 30px;'>
Experience a collection of classic puzzle and strategy games. Challenge your mind with these
timeless problems implemented as interactive games.
</p>
""", unsafe_allow_html=True)

# Filter section
with st.container():
    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Show:")
        sort_by = st.selectbox("", ["All Games", "Puzzle Games", "Strategy Games", "Easy Games", "Hard Games"], label_visibility="collapsed")
    
    with col2:
        st.markdown("### Filter By:")
        player_count = st.radio("", ["All", "1 Player", "2 Players"], horizontal=True, label_visibility="collapsed")
    
    with col3:
        st.markdown("### Search:")
        search_term = st.text_input("", placeholder="Search games...", label_visibility="collapsed")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Filter games based on selections
filtered_games = games.copy()

if sort_by == "Puzzle Games":
    filtered_games = [game for game in filtered_games if game["category"] == "Puzzle"]
elif sort_by == "Strategy Games":
    filtered_games = [game for game in filtered_games if game["category"] == "Strategy"]
elif sort_by == "Easy Games":
    filtered_games = [game for game in filtered_games if game["difficulty"] == "Easy"]
elif sort_by == "Hard Games":
    filtered_games = [game for game in filtered_games if game["difficulty"] == "Hard"]

if player_count != "All":
    filtered_games = [game for game in filtered_games if game["players"] == player_count]

if search_term:
    filtered_games = [game for game in filtered_games if search_term.lower() in game["title"].lower() or search_term.lower() in game["description"].lower()]

# Function to launch games
def launch_game(game_file):
    import os
    import subprocess
    try:
        # Get the directory where the current script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the game script
        game_path = os.path.join(current_dir, game_file)
        
        # Launch the game in a new process
        subprocess.Popen(["streamlit", "run", game_path])
        st.success(f"Launching {game_file}...")
    except Exception as e:
        st.error(f"Error launching game: {e}")
        st.info("Make sure all game files are in the same directory as this homepage.")

# Create game grid
num_columns = 3
rows = [filtered_games[i:i+num_columns] for i in range(0, len(filtered_games), num_columns)]

for row in rows:
    cols = st.columns(num_columns)
    for i, game in enumerate(row):
        if i < len(cols):
            with cols[i]:
                st.markdown("<div class='game-card'>", unsafe_allow_html=True)
                
                # Generate game image
                img = get_placeholder_image(game["seed"])
                st.image(img, use_column_width=True)
                
                # Game category
                st.markdown(f"<span class='category-label'>{game['category']}</span><span class='category-label'>{game['difficulty']}</span>", unsafe_allow_html=True)
                
                # Game title
                st.markdown(f"<div class='game-title'>{game['title']}</div>", unsafe_allow_html=True)
                
                # Game creator
                st.markdown(f"<div class='game-creator'>By {game['creator']}</div>", unsafe_allow_html=True)
                
                # Game description (truncated)
                if len(game["description"]) > 100:
                    short_desc = game["description"][:100] + "..."
                else:
                    short_desc = game["description"]
                st.markdown(f"<p style='font-size: 0.9rem;'>{short_desc}</p>", unsafe_allow_html=True)
                
                # Launch button
                if st.button("Play Now", key=f"play_{game['title']}", use_container_width=True):
                    launch_game(game["file"])
                
                st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("© 2025 Game Collection Team | All Rights Reserved", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Help expander at the bottom
with st.expander("Need Help?"):
    st.markdown("""
    ### Setup Instructions
    
    1. Save all game files in the same directory as this homepage.
    2. Make sure you have Streamlit installed: `pip install streamlit`
    3. Run this homepage using: `streamlit run homepage.py`
    
    ### Game Files Required
    - `tictactoe_game.py`
    - `traveling_salesman.py`  
    - `tower_of_hanoi.py`
    - `eight_queens.py`
    - `knights_tour.py`
    
    ### Troubleshooting
    If games don't launch, check that all files exist and are properly formatted as Streamlit apps.
    """)