import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Dict, List, Tuple
import time

class RecommenderEvaluator:
    """
    Evaluates recommendation system performance using various metrics.
    """
    
    def __init__(self, recommender, data_loader):
        self.recommender = recommender
        self.data_loader = data_loader
        
    def evaluate_predictions(self, test_data: pd.DataFrame, method: str = "user_based", k: int = 20) -> Dict:
        """
        Evaluate prediction accuracy using RMSE and MAE.
        """
        predictions = []
        actual_ratings = []
        
        print(f"Evaluating {method} collaborative filtering...")
        start_time = time.time()
        
        for _, row in test_data.iterrows():
            user_id = row['user_id']
            anime_id = row['anime_id']
            actual_rating = row['rating']
            
            if method == "user_based":
                predicted_rating = self.recommender.predict_user_based(user_id, anime_id, k)
            else:  # item_based
                predicted_rating = self.recommender.predict_item_based(user_id, anime_id, k)
            
            predictions.append(predicted_rating)
            actual_ratings.append(actual_rating)
        
        evaluation_time = time.time() - start_time
        
        rmse = np.sqrt(mean_squared_error(actual_ratings, predictions))
        mae = mean_absolute_error(actual_ratings, predictions)
        
        # Calculate coverage (percentage of predictions that could be made)
        non_zero_predictions = sum(1 for p in predictions if p > 0)
        coverage = non_zero_predictions / len(predictions) * 100
        
        results = {
            'method': method,
            'rmse': rmse,
            'mae': mae,
            'coverage': coverage,
            'evaluation_time': evaluation_time,
            'num_predictions': len(predictions)
        }
        
        return results
    
    def evaluate_recommendations(self, test_users: List[int], method: str = "user_based", 
                               n_recommendations: int = 10, k: int = 20) -> Dict:
        """
        Evaluate recommendation quality using precision, recall, and diversity.
        """
        all_recommendations = []
        recommendation_times = []
        
        print(f"Generating recommendations for {len(test_users)} users...")
        
        for user_id in test_users:
            start_time = time.time()
            
            if method == "user_based":
                recommendations = self.recommender.recommend_user_based(user_id, n_recommendations, k)
            else:  # item_based
                recommendations = self.recommender.recommend_item_based(user_id, n_recommendations, k)
            
            recommendation_time = time.time() - start_time
            recommendation_times.append(recommendation_time)
            all_recommendations.extend([rec[0] for rec in recommendations])
        
        # Calculate diversity (number of unique recommendations)
        unique_recommendations = len(set(all_recommendations))
        total_recommendations = len(all_recommendations)
        diversity = unique_recommendations / total_recommendations * 100 if total_recommendations > 0 else 0
        
        # Calculate average recommendation time
        avg_recommendation_time = np.mean(recommendation_times)
        
        results = {
            'method': method,
            'diversity': diversity,
            'unique_recommendations': unique_recommendations,
            'total_recommendations': total_recommendations,
            'avg_recommendation_time': avg_recommendation_time,
            'num_users_evaluated': len(test_users)
        }
        
        return results
    
    def split_data(self, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split the rating data into train and test sets.
        """
        ratings_df = self.data_loader.ratings_df
        
        # Split by user to ensure we have ratings for all users in both sets
        users = ratings_df['user_id'].unique()
        train_users, test_users = train_test_split(users, test_size=test_size, random_state=random_state)
        
        train_data = ratings_df[ratings_df['user_id'].isin(train_users)]
        test_data = ratings_df[ratings_df['user_id'].isin(test_users)]
        
        # Ensure we have some overlap for evaluation
        if len(test_data) == 0:
            # Fallback: split by individual ratings
            train_data, test_data = train_test_split(ratings_df, test_size=test_size, random_state=random_state)
        
        print(f"Train set: {len(train_data)} ratings from {train_data['user_id'].nunique()} users")
        print(f"Test set: {len(test_data)} ratings from {test_data['user_id'].nunique()} users")
        
        return train_data, test_data
    
    def run_full_evaluation(self, test_size: float = 0.2) -> Dict:
        """
        Run a comprehensive evaluation of both user-based and item-based methods.
        """
        # Split data
        train_data, test_data = self.split_data(test_size)
        
        # Create training user-item matrix
        train_matrix = train_data.pivot_table(
            index='user_id', columns='anime_id', values='rating', fill_value=0
        )
        
        # Fit the model on training data
        self.recommender.fit(train_matrix)
        
        # Evaluate both methods
        results = {}
        
        # User-based evaluation
        user_based_predictions = self.evaluate_predictions(test_data, 'user_based')
        test_users = test_data['user_id'].unique()[:20]  # Limit for efficiency
        user_based_recommendations = self.evaluate_recommendations(test_users, 'user_based')
        
        results['user_based'] = {**user_based_predictions, **user_based_recommendations}
        
        # Item-based evaluation
        item_based_predictions = self.evaluate_predictions(test_data, 'item_based')
        item_based_recommendations = self.evaluate_recommendations(test_users, 'item_based')
        
        results['item_based'] = {**item_based_predictions, **item_based_recommendations}
        
        return results
    
    def print_evaluation_results(self, results: Dict):
        """
        Print evaluation results in a readable format.
        """
        print("\n=== RECOMMENDATION SYSTEM EVALUATION RESULTS ===")
        
        for method, metrics in results.items():
            print(f"\n{method.upper()} COLLABORATIVE FILTERING:")
            print(f"  Prediction Accuracy:")
            print(f"    RMSE: {metrics.get('rmse', 0):.4f}")
            print(f"    MAE: {metrics.get('mae', 0):.4f}")
            print(f"    Coverage: {metrics.get('coverage', 0):.2f}%")
            print(f"  Recommendation Quality:")
            print(f"    Diversity: {metrics.get('diversity', 0):.2f}%")
            print(f"    Unique Recommendations: {metrics.get('unique_recommendations', 0)}")
            print(f"  Performance:")
            print(f"    Evaluation Time: {metrics.get('evaluation_time', 0):.2f}s")
            print(f"    Avg Recommendation Time: {metrics.get('avg_recommendation_time', 0):.4f}s")
