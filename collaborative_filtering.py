import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings("ignore")

class CollaborativeFilteringRecommender:
    """
    Anime recommendation system using collaborative filtering.
    Supports both user-based and item-based approaches.
    """
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_item_matrix = None
        self.mean_user_ratings = None
        self.mean_item_ratings = None
        
    def fit(self, user_item_matrix: pd.DataFrame):
        """
        Fit the collaborative filtering model.
        """
        self.user_item_matrix = user_item_matrix.copy()
        
        # Calculate mean ratings
        self.mean_user_ratings = self.user_item_matrix.mean(axis=1)
        self.mean_item_ratings = self.user_item_matrix.mean(axis=0)
        
        # Compute user similarity matrix
        print("Computing user similarity matrix...")
        user_matrix = self.user_item_matrix.values
        self.user_similarity_matrix = cosine_similarity(user_matrix)
        self.user_similarity_matrix = pd.DataFrame(
            self.user_similarity_matrix,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        # Compute item similarity matrix
        print("Computing item similarity matrix...")
        item_matrix = self.user_item_matrix.T.values
        self.item_similarity_matrix = cosine_similarity(item_matrix)
        self.item_similarity_matrix = pd.DataFrame(
            self.item_similarity_matrix,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns
        )
        
        print("Model training completed!")
    
    def predict_user_based(self, user_id: int, anime_id: int, k: int = 20) -> float:
        """
        Predict rating using user-based collaborative filtering.
        """
        if user_id not in self.user_item_matrix.index:
            return self.mean_item_ratings[anime_id] if anime_id in self.mean_item_ratings else 0
        
        if anime_id not in self.user_item_matrix.columns:
            return self.mean_user_ratings[user_id] if user_id in self.mean_user_ratings else 0
        
        # Get similar users
        user_similarities = self.user_similarity_matrix[user_id].drop(user_id)
        user_similarities = user_similarities[user_similarities > 0].sort_values(ascending=False)[:k]
        
        if len(user_similarities) == 0:
            return self.mean_item_ratings[anime_id]
        
        # Calculate weighted average
        numerator = 0
        denominator = 0
        
        for similar_user, similarity in user_similarities.items():
            if self.user_item_matrix.loc[similar_user, anime_id] > 0:
                rating_diff = (self.user_item_matrix.loc[similar_user, anime_id] - 
                             self.mean_user_ratings[similar_user])
                numerator += similarity * rating_diff
                denominator += abs(similarity)
        
        if denominator == 0:
            return self.mean_user_ratings[user_id]
        
        predicted_rating = self.mean_user_ratings[user_id] + (numerator / denominator)
        return max(1, min(10, predicted_rating))
    
    def predict_item_based(self, user_id: int, anime_id: int, k: int = 20) -> float:
        """
        Predict rating using item-based collaborative filtering.
        """
        if user_id not in self.user_item_matrix.index:
            return self.mean_item_ratings[anime_id] if anime_id in self.mean_item_ratings else 0
        
        if anime_id not in self.user_item_matrix.columns:
            return self.mean_user_ratings[user_id] if user_id in self.mean_user_ratings else 0
        
        # Get user's rated items
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0].index
        
        if len(rated_items) == 0:
            return self.mean_item_ratings[anime_id]
        
        # Get similar items
        item_similarities = self.item_similarity_matrix[anime_id]
        similar_items = item_similarities[rated_items]
        similar_items = similar_items[similar_items > 0].sort_values(ascending=False)[:k]
        
        if len(similar_items) == 0:
            return self.mean_item_ratings[anime_id]
        
        # Calculate weighted average
        numerator = 0
        denominator = 0
        
        for similar_item, similarity in similar_items.items():
            numerator += similarity * user_ratings[similar_item]
            denominator += abs(similarity)
        
        if denominator == 0:
            return self.mean_item_ratings[anime_id]
        
        predicted_rating = numerator / denominator
        return max(1, min(10, predicted_rating))
    
    def recommend_user_based(self, user_id: int, n_recommendations: int = 10, k: int = 20) -> List[Tuple[int, str, float]]:
        """
        Get top-N anime recommendations for a user using user-based CF.
        """
        if user_id not in self.user_item_matrix.index:
            # Return top-rated anime for new users
            return self._get_popular_recommendations(n_recommendations)
        
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_anime = user_ratings[user_ratings == 0].index
        
        recommendations = []
        for anime_id in unrated_anime:
            predicted_rating = self.predict_user_based(user_id, anime_id, k)
            anime_info = self.data_loader.get_anime_info(anime_id)
            anime_name = anime_info.get('name', f'Anime {anime_id}')
            recommendations.append((anime_id, anime_name, predicted_rating))
        
        recommendations.sort(key=lambda x: x[2], reverse=True)
        return recommendations[:n_recommendations]
    
    def recommend_item_based(self, user_id: int, n_recommendations: int = 10, k: int = 20) -> List[Tuple[int, str, float]]:
        """
        Get top-N anime recommendations for a user using item-based CF.
        """
        if user_id not in self.user_item_matrix.index:
            return self._get_popular_recommendations(n_recommendations)
        
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_anime = user_ratings[user_ratings == 0].index
        
        recommendations = []
        for anime_id in unrated_anime:
            predicted_rating = self.predict_item_based(user_id, anime_id, k)
            anime_info = self.data_loader.get_anime_info(anime_id)
            anime_name = anime_info.get('name', f'Anime {anime_id}')
            recommendations.append((anime_id, anime_name, predicted_rating))
        
        recommendations.sort(key=lambda x: x[2], reverse=True)
        return recommendations[:n_recommendations]
    
    def _get_popular_recommendations(self, n: int) -> List[Tuple[int, str, float]]:
        """
        Get popular anime recommendations for new users.
        """
        popular_anime = self.mean_item_ratings.sort_values(ascending=False)[:n]
        recommendations = []
        
        for anime_id, avg_rating in popular_anime.items():
            anime_info = self.data_loader.get_anime_info(anime_id)
            anime_name = anime_info.get('name', f'Anime {anime_id}')
            recommendations.append((anime_id, anime_name, avg_rating))
        
        return recommendations
    
    def get_similar_users(self, user_id: int, n: int = 10) -> List[Tuple[int, float]]:
        """
        Get most similar users to the given user.
        """
        if user_id not in self.user_similarity_matrix.index:
            return []
        
        similarities = self.user_similarity_matrix[user_id].drop(user_id)
        similar_users = similarities.sort_values(ascending=False)[:n]
        
        return [(user, sim) for user, sim in similar_users.items()]
    
    def get_similar_anime(self, anime_id: int, n: int = 10) -> List[Tuple[int, str, float]]:
        """
        Get most similar anime to the given anime.
        """
        if anime_id not in self.item_similarity_matrix.index:
            return []
        
        similarities = self.item_similarity_matrix[anime_id].drop(anime_id)
        similar_anime = similarities.sort_values(ascending=False)[:n]
        
        recommendations = []
        for sim_anime_id, similarity in similar_anime.items():
            anime_info = self.data_loader.get_anime_info(sim_anime_id)
            anime_name = anime_info.get('name', f'Anime {sim_anime_id}')
            recommendations.append((sim_anime_id, anime_name, similarity))
        
        return recommendations
