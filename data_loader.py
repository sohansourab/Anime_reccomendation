import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Tuple, Optional
import os

class AnimeDataLoader:
    def __init__(self):
        self.anime_df = None
        self.ratings_df = None
        self.user_item_matrix = None
        
    def load_sample_data(self):
        anime_data = {
            "anime_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "name": [
                "Attack on Titan", "Death Note", "One Piece", "Naruto", "Dragon Ball Z",
                "My Hero Academia", "Demon Slayer", "Fullmetal Alchemist", "Hunter x Hunter",
                "One Punch Man", "Tokyo Ghoul", "Bleach", "Jujutsu Kaisen", "Mob Psycho 100",
                "Code Geass"
            ],
            "genre": [
                "Action,Drama", "Supernatural,Thriller", "Adventure,Comedy", "Action,Adventure",
                "Action,Adventure", "Action,School", "Action,Supernatural", "Adventure,Drama",
                "Adventure,Fantasy", "Action,Comedy", "Action,Horror", "Action,Supernatural",
                "Action,School", "Comedy,Supernatural", "Drama,Mecha"
            ],
            "type": ["TV"] * 15,
            "episodes": [87, 37, 1000, 720, 291, 138, 44, 64, 148, 24, 48, 366, 24, 37, 50],
            "rating": [9.0, 8.6, 9.0, 8.4, 8.7, 8.5, 8.7, 9.1, 9.0, 8.8, 8.0, 8.2, 8.6, 8.9, 8.9]
        }
        self.anime_df = pd.DataFrame(anime_data)
        print(f"Loaded {len(self.anime_df)} anime")
        return self.anime_df
