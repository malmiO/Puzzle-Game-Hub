import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# Page setup
st.set_page_config(
    page_title="Puzzle Game Hub",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom right, #0a0a0a, #1a1a1a);
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    
    .game-card {
        background: linear-gradient(#1c1c1c, #1c1c1c);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }

    
    .game-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.4), 0 0 15px rgba(65, 105, 225, 0.3);
    }

    .game-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin: 10px 0 5px;
        color: #ffffff;
    }

    .game-desc {
        font-size: 0.9rem;
        color: #cccccc;
        margin-bottom: 15px;
    }

    .stButton>button {
        color: #ffffff;
        background-color: #4169e1;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #6495ed;
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .footer {
        margin-top: 50px;
        padding: 20px 0;
        border-top: 1px solid #333333;
        color: #999999;
        font-size: 0.9rem;
        text-align: center;
    }

    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>🧩 Puzzle Game Hub</h1>", unsafe_allow_html=True)

# Function to generate placeholder images with game names
def get_placeholder_image(title, seed, width=400, height=225):
    np.random.seed(seed)
    imarray = np.random.rand(height, width, 3) * 255
    theme_color = np.array([30, 60, 90]) + np.random.rand(3) * 50
    imarray = (imarray * 0.2) + theme_color
    imarray = imarray.astype(np.uint8)
    img = Image.fromarray(imarray)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), title, fill="#ffffff", font=font, stroke_width=2, stroke_fill="#000000")
    return img

# Game data
games = [
    {
        "title": "Tic-Tac-Toe",
        "description": "Classic two-player game where you try to get three in a row.",
        "creator": "Team Member 1",
        "category": "Strategy",
        "difficulty": "Easy",
        "players": "2 Players",
        "file": "tic_tac_toe/app.py",
        "seed": 42
    },
    {
        "title": "Traveling Salesman Problem",
        "description": "Find the shortest possible route that visits each city once and returns to the origin.",
        "creator": "Team Member 2",
        "category": "Puzzle",
        "difficulty": "Medium",
        "players": "1 Player",
        "file": "tsp/app.py",
        "seed": 123
    },
    {
        "title": "Tower of Hanoi",
        "description": "Move the entire stack of disks to another rod following specific rules.",
        "creator": "Team Member 3",
        "category": "Puzzle",
        "difficulty": "Medium",
        "players": "1 Player",
        "file": "tower_of_hanoi/app.py",
        "seed": 234
    },
    {
        "title": "Eight Queens Puzzle",
        "description": "Place eight chess queens on an 8×8 chessboard so that no two queens threaten each other.",
        "creator": "Team Member 4",
        "category": "Puzzle",
        "difficulty": "Hard",
        "players": "1 Player",
        "file": "eight_queens/app.py",
        "seed": 345
    },
    {
        "title": "Knight's Tour Problem",
        "description": "Find a sequence of moves for a knight to visit every square on a chessboard exactly once.",
        "creator": "Team Member 5",
        "category": "Puzzle",
        "difficulty": "Hard",
        "players": "1 Player",
        "file": "knights_tour/app.py",
        "seed": 456
    }
]

# Sidebar for filters
with st.sidebar:
    st.header("Filters")
    category = st.selectbox("Category", ["All", "Puzzle", "Strategy"])
    difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    search_term = st.text_input("Search for a game...")

# Filter games based on selections
filtered_games = [game for game in games if 
                  (category == "All" or game["category"] == category) and
                  (difficulty == "All" or game["difficulty"] == difficulty) and
                  (search_term.lower() in game["title"].lower() or search_term.lower() in game["description"].lower())]

# Display game cards in a grid layout
cols = st.columns(3)  # Display 3 games per row

for idx, game in enumerate(filtered_games):
    with cols[idx % 3]:
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.image(get_placeholder_image(game["title"], game["seed"]), use_container_width=True)
        st.markdown(f"""
            <div class='game-title'>{game['title']}</div>
            <p class='game-desc'>{game['description']}</p>
        """, unsafe_allow_html=True)
        st.button("Play Now", key=f"play_{game['title']}", on_click=lambda file=game["file"]: os.system(f"streamlit run {file}"))
        st.markdown("</div>", unsafe_allow_html=True)


# Footer
st.markdown("<div class='footer'>© 2025 Game Collection Team | All Rights Reserved</div>", unsafe_allow_html=True)