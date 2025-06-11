#!/usr/bin/env python3
"""
Anime Recommendation System
A collaborative filtering-based anime recommendation system.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
import argparse
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import AnimeDataLoader
from collaborative_filtering import CollaborativeFilteringRecommender
from evaluator import RecommenderEvaluator

class AnimeRecommendationSystem:
    """
    Main class for the anime recommendation system.
    """
    
    def __init__(self):
        self.data_loader = AnimeDataLoader()
        self.recommender = None
        self.evaluator = None
        self.is_fitted = False
    
    def load_data(self):
        """Load and prepare the anime rating data."""
        print("Loading anime rating data...")
        anime_df, ratings_df = self.data_loader.load_sample_data()
        
        print("\nDataset Statistics:")
        stats = self.data_loader.get_rating_statistics()
        for key, value in stats.items():
            if key == 'rating_distribution':
                print(f"  {key}:")
                for rating, count in value.items():
                    print(f"    Rating {rating}: {count} users")
            else:
                print(f"  {key}: {value}")
        
        return anime_df, ratings_df
    
    def setup_recommender(self):
        """Initialize and train the recommendation system."""
        print("\nSetting up recommendation system...")
        
        # Create user-item matrix
        user_item_matrix = self.data_loader.create_user_item_matrix()
        
        # Initialize recommender
        self.recommender = CollaborativeFilteringRecommender(self.data_loader)
        
        # Fit the model
        self.recommender.fit(user_item_matrix)
        self.is_fitted = True
        
        # Initialize evaluator
        self.evaluator = RecommenderEvaluator(self.recommender, self.data_loader)
        
        print("Recommendation system ready!")
    
    def get_user_recommendations(self, user_id: int, method: str = 'user_based', 
                               n_recommendations: int = 5) -> List[Tuple[int, str, float]]:
        """Get anime recommendations for a specific user."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call setup_recommender() first.")
        
        if method == 'user_based':
            recommendations = self.recommender.recommend_user_based(user_id, n_recommendations)
        elif method == 'item_based':
            recommendations = self.recommender.recommend_item_based(user_id, n_recommendations)
        else:
            raise ValueError("Method must be 'user_based' or 'item_based'")
        
        return recommendations
    
    def get_similar_anime(self, anime_id: int, n_similar: int = 5) -> List[Tuple[int, str, float]]:
        """Get anime similar to the given anime."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call setup_recommender() first.")
        
        return self.recommender.get_similar_anime(anime_id, n_similar)
    
    def display_user_profile(self, user_id: int):
        """Display user's rating history."""
        user_ratings = self.data_loader.get_user_ratings(user_id)
        
        if user_ratings.empty:
            print(f"No ratings found for user {user_id}")
            return
        
        print(f"\nUser {user_id} Rating History:")
        print("-" * 50)
        for _, row in user_ratings.iterrows():
            print(f"  {row['name']} - Rating: {row['rating']}")
        
        avg_rating = user_ratings['rating'].mean()
        print(f"\nAverage Rating: {avg_rating:.2f}")
    
    def display_recommendations(self, user_id: int, method: str = 'user_based', n: int = 5):
        """Display recommendations for a user."""
        print(f"\nTop {n} {method.replace('_', '-').title()} Recommendations for User {user_id}:")
        print("-" * 60)
        
        try:
            recommendations = self.get_user_recommendations(user_id, method, n)
            
            if not recommendations:
                print("  No recommendations available for this user.")
                return
            
            for i, (anime_id, name, predicted_rating) in enumerate(recommendations, 1):
                print(f"  {i}. {name} (Predicted Rating: {predicted_rating:.2f})")
                
        except Exception as e:
            print(f"  Error generating recommendations: {e}")
    
    def display_similar_anime(self, anime_id: int, n: int = 5):
        """Display anime similar to the given anime."""
        anime_info = self.data_loader.get_anime_info(anime_id)
        anime_name = anime_info.get('name', f'Anime {anime_id}')
        
        print(f"\nAnime Similar to \'{anime_name}\':")
        print("-" * 50)
        
        try:
            similar_anime = self.get_similar_anime(anime_id, n)
            
            if not similar_anime:
                print("  No similar anime found.")
                return
            
            for i, (sim_anime_id, name, similarity) in enumerate(similar_anime, 1):
                print(f"  {i}. {name} (Similarity: {similarity:.3f})")
                
        except Exception as e:
            print(f"  Error finding similar anime: {e}")
    
    def run_evaluation(self):
        """Run a comprehensive evaluation of the recommendation system."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call setup_recommender() first.")
        
        print("\nRunning comprehensive evaluation...")
        results = self.evaluator.run_full_evaluation()
        self.evaluator.print_evaluation_results(results)
        
        return results
    
    def interactive_demo(self):
        """Run an interactive demonstration of the recommendation system."""
        print("\n=== ANIME RECOMMENDATION SYSTEM DEMO ===")
        
        while True:
            print("\nOptions:")
            print("1. Get user recommendations (user-based)")
            print("2. Get user recommendations (item-based)")
            print("3. View user profile")
            print("4. Find similar anime")
            print("5. List all anime")
            print("6. Run evaluation")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            try:
                if choice == '1':
                    user_id = int(input("Enter user ID (1-100): "))
                    self.display_user_profile(user_id)
                    self.display_recommendations(user_id, 'user_based')
                    
                elif choice == '2':
                    user_id = int(input("Enter user ID (1-100): "))
                    self.display_user_profile(user_id)
                    self.display_recommendations(user_id, 'item_based')
                    
                elif choice == '3':
                    user_id = int(input("Enter user ID (1-100): "))
                    self.display_user_profile(user_id)
                    
                elif choice == '4':
                    anime_id = int(input("Enter anime ID (1-15): "))
                    self.display_similar_anime(anime_id)
                    
                elif choice == '5':
                    print("\nAvailable Anime:")
                    print("-" * 40)
                    for _, row in self.data_loader.anime_df.iterrows():
                        print(f"  {row['anime_id']}. {row['name']} ({row['genre']}) - {row['rating']}/10")
                
                elif choice == '6':
                    self.run_evaluation()
                    
                elif choice == '7':
                    print("Thank you for using the Anime Recommendation System!")
                    break
                    
                else:
                    print("Invalid choice. Please enter a number between 1-7.")
                    
            except ValueError:
                print("Invalid input. Please enter a valid number.")
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    """Main function to run the anime recommendation system."""
    parser = argparse.ArgumentParser(description='Anime Recommendation System')
    parser.add_argument('--demo', action='store_true', help='Run interactive demo')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation only')
    parser.add_argument('--user-id', type=int, help='Get recommendations for specific user')
    parser.add_argument('--method', choices=['user_based', 'item_based'], 
                       default='user_based', help='Recommendation method')
    parser.add_argument('--num-recommendations', type=int, default=5, 
                       help='Number of recommendations to show')
    
    args = parser.parse_args()
    
    # Initialize system
    system = AnimeRecommendationSystem()
    
    try:
        # Load data and setup recommender
        system.load_data()
        system.setup_recommender()
        
        if args.demo:
            system.interactive_demo()
        elif args.evaluate:
            system.run_evaluation()
        elif args.user_id:
            system.display_user_profile(args.user_id)
            system.display_recommendations(args.user_id, args.method, args.num_recommendations)
        else:
            # Default: run a quick demonstration
            print("\n=== QUICK DEMONSTRATION ===")
            
            # Show sample user profile and recommendations
            sample_user = 1
            system.display_user_profile(sample_user)
            system.display_recommendations(sample_user, 'user_based')
            system.display_recommendations(sample_user, 'item_based')
            
            # Show similar anime
            sample_anime = 1  # Attack on Titan
            system.display_similar_anime(sample_anime)
            
            print("\nRun with --demo for interactive mode or --help for more options.")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
