#!/usr/bin/env python3
"""
Simplified Anime Recommendation System Demo
Uses only Python standard library for demonstration.
"""

import math
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

class SimpleAnimeRecommender:
    """
    A simplified anime recommendation system using collaborative filtering.
    Implements core concepts without external dependencies.
    """
    
    def __init__(self):
        self.anime_db = {
            1: {'name': 'Attack on Titan', 'genre': 'Action,Drama', 'rating': 9.0},
            2: {'name': 'Death Note', 'genre': 'Supernatural,Thriller', 'rating': 8.6},
            3: {'name': 'One Piece', 'genre': 'Adventure,Comedy', 'rating': 9.0},
            4: {'name': 'Naruto', 'genre': 'Action,Adventure', 'rating': 8.4},
            5: {'name': 'Dragon Ball Z', 'genre': 'Action,Adventure', 'rating': 8.7},
            6: {'name': 'My Hero Academia', 'genre': 'Action,School', 'rating': 8.5},
            7: {'name': 'Demon Slayer', 'genre': 'Action,Supernatural', 'rating': 8.7},
            8: {'name': 'Fullmetal Alchemist', 'genre': 'Adventure,Drama', 'rating': 9.1},
            9: {'name': 'Hunter x Hunter', 'genre': 'Adventure,Fantasy', 'rating': 9.0},
            10: {'name': 'One Punch Man', 'genre': 'Action,Comedy', 'rating': 8.8}
        }
        
        # Sample user ratings (user_id: {anime_id: rating})
        self.user_ratings = self._generate_sample_ratings()
        
    def _generate_sample_ratings(self) -> Dict[int, Dict[int, int]]:
        """Generate sample user ratings for demonstration."""
        random.seed(42)  # For reproducible results
        ratings = defaultdict(dict)
        
        # Generate ratings for 20 users
        for user_id in range(1, 21):
            # Each user rates 4-8 random anime
            num_ratings = random.randint(4, 8)
            anime_ids = random.sample(list(self.anime_db.keys()), num_ratings)
            
            for anime_id in anime_ids:
                # Generate realistic ratings based on anime popularity
                base_rating = self.anime_db[anime_id]['rating']
                user_rating = max(1, min(10, int(random.gauss(base_rating, 1.5))))
                ratings[user_id][anime_id] = user_rating
                
        return dict(ratings)
    
    def cosine_similarity(self, ratings1: Dict[int, int], ratings2: Dict[int, int]) -> float:
        """Calculate cosine similarity between two users."""
        common_items = set(ratings1.keys()) & set(ratings2.keys())
        
        if len(common_items) == 0:
            return 0.0
        
        # Calculate dot product and magnitudes
        dot_product = sum(ratings1[item] * ratings2[item] for item in common_items)
        magnitude1 = math.sqrt(sum(ratings1[item] ** 2 for item in common_items))
        magnitude2 = math.sqrt(sum(ratings2[item] ** 2 for item in common_items))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)
    
    def get_similar_users(self, target_user: int, n: int = 5) -> List[Tuple[int, float]]:
        """Find users most similar to the target user."""
        if target_user not in self.user_ratings:
            return []
        
        similarities = []
        target_ratings = self.user_ratings[target_user]
        
        for user_id, ratings in self.user_ratings.items():
            if user_id != target_user:
                similarity = self.cosine_similarity(target_ratings, ratings)
                similarities.append((user_id, similarity))
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]
    
    def predict_rating(self, user_id: int, anime_id: int) -> float:
        """Predict rating for a user-anime pair using collaborative filtering."""
        if user_id not in self.user_ratings:
            # Return average rating for new users
            return self.anime_db.get(anime_id, {}).get('rating', 5.0)
        
        user_ratings = self.user_ratings[user_id]
        
        # If user already rated this anime, return the rating
        if anime_id in user_ratings:
            return user_ratings[anime_id]
        
        # Find similar users who rated this anime
        similar_users = self.get_similar_users(user_id)
        
        weighted_sum = 0
        similarity_sum = 0
        
        for similar_user, similarity in similar_users:
            if anime_id in self.user_ratings[similar_user]:
                rating = self.user_ratings[similar_user][anime_id]
                weighted_sum += similarity * rating
                similarity_sum += abs(similarity)
        
        if similarity_sum == 0:
            # Fallback to anime average rating
            return self.anime_db.get(anime_id, {}).get('rating', 5.0)
        
        predicted_rating = weighted_sum / similarity_sum
        return max(1, min(10, predicted_rating))
    
    def recommend_anime(self, user_id: int, n: int = 5) -> List[Tuple[int, str, float]]:
        """Get top N anime recommendations for a user."""
        if user_id not in self.user_ratings:
            # Return popular anime for new users
            popular_anime = sorted(self.anime_db.items(), 
                                 key=lambda x: x[1]['rating'], reverse=True)
            return [(aid, info['name'], info['rating']) 
                   for aid, info in popular_anime[:n]]
        
        user_ratings = self.user_ratings[user_id]
        unrated_anime = [aid for aid in self.anime_db.keys() if aid not in user_ratings]
        
        recommendations = []
        for anime_id in unrated_anime:
            predicted_rating = self.predict_rating(user_id, anime_id)
            name = self.anime_db[anime_id]['name']
            recommendations.append((anime_id, name, predicted_rating))
        
        # Sort by predicted rating
        recommendations.sort(key=lambda x: x[2], reverse=True)
        return recommendations[:n]
    
    def get_user_profile(self, user_id: int) -> List[Tuple[str, int]]:
        """Get user's rating history."""
        if user_id not in self.user_ratings:
            return []
        
        profile = []
        for anime_id, rating in self.user_ratings[user_id].items():
            name = self.anime_db[anime_id]['name']
            profile.append((name, rating))
        
        return sorted(profile, key=lambda x: x[1], reverse=True)
    
    def find_similar_anime(self, target_anime: int, n: int = 3) -> List[Tuple[int, str, float]]:
        """Find anime similar to the target anime based on user ratings."""
        if target_anime not in self.anime_db:
            return []
        
        # Get users who rated the target anime
        target_raters = {uid: ratings[target_anime] 
                        for uid, ratings in self.user_ratings.items() 
                        if target_anime in ratings}
        
        if not target_raters:
            return []
        
        similarities = []
        
        for anime_id, anime_info in self.anime_db.items():
            if anime_id == target_anime:
                continue
                
            # Get users who rated this anime
            anime_raters = {uid: ratings[anime_id] 
                          for uid, ratings in self.user_ratings.items() 
                          if anime_id in ratings}
            
            if not anime_raters:
                continue
            
            # Calculate similarity based on common users' ratings
            common_users = set(target_raters.keys()) & set(anime_raters.keys())
            
            if len(common_users) < 2:  # Need at least 2 common users
                continue
            
            target_ratings = {uid: target_raters[uid] for uid in common_users}
            anime_ratings = {uid: anime_raters[uid] for uid in common_users}
            
            similarity = self.cosine_similarity(target_ratings, anime_ratings)
            similarities.append((anime_id, anime_info['name'], similarity))
        
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:n]
    
    def demo(self):
        """Run a demonstration of the recommendation system."""
        print("🎌 ANIME RECOMMENDATION SYSTEM DEMO 🎌\n")
        
        # Show available anime
        print("📺 Available Anime:")
        print("-" * 50)
        for aid, info in self.anime_db.items():
            print(f"  {aid:2d}. {info['name']:<20} ({info['genre']:<20}) - {info['rating']}/10")
        
        print(f"\n👥 Generated ratings for {len(self.user_ratings)} users\n")
        
        # Demo user profile
        demo_user = 1
        print(f"👤 User {demo_user} Profile:")
        print("-" * 30)
        profile = self.get_user_profile(demo_user)
        for name, rating in profile:
            print(f"  {name:<20} - {rating}/10")
        
        avg_rating = sum(rating for _, rating in profile) / len(profile) if profile else 0
        print(f"  Average Rating: {avg_rating:.1f}/10\n")
        
        # Show recommendations
        print(f"🔮 Top 5 Recommendations for User {demo_user}:")
        print("-" * 45)
        recommendations = self.recommend_anime(demo_user, 5)
        for i, (aid, name, pred_rating) in enumerate(recommendations, 1):
            print(f"  {i}. {name:<20} (Predicted: {pred_rating:.1f}/10)")
        
        # Show similar users
        print(f"\n👥 Users Similar to User {demo_user}:")
        print("-" * 35)
        similar_users = self.get_similar_users(demo_user, 3)
        for user, similarity in similar_users:
            print(f"  User {user:<2} (Similarity: {similarity:.3f})")
        
        # Show similar anime
        demo_anime = 1  # Attack on Titan
        anime_name = self.anime_db[demo_anime]['name']
        print(f"\n🎭 Anime Similar to '{anime_name}':")
        print("-" * 40)
        similar_anime = self.find_similar_anime(demo_anime, 3)
        for aid, name, similarity in similar_anime:
            print(f"  {name:<20} (Similarity: {similarity:.3f})")
        
        # Simple evaluation
        print(f"\n📊 System Statistics:")
        print("-" * 25)
        total_ratings = sum(len(ratings) for ratings in self.user_ratings.values())
        total_possible = len(self.user_ratings) * len(self.anime_db)
        sparsity = (1 - total_ratings / total_possible) * 100
        
        print(f"  Total Users: {len(self.user_ratings)}")
        print(f"  Total Anime: {len(self.anime_db)}")
        print(f"  Total Ratings: {total_ratings}")
        print(f"  Data Sparsity: {sparsity:.1f}%")
        
        print("\n✨ Demo completed! This shows the core concepts of collaborative filtering.")
        print("\n🚀 For a production system, you would:")
        print("   • Use larger datasets (MyAnimeList, AniList)")
        print("   • Implement matrix factorization techniques")
        print("   • Add content-based filtering")
        print("   • Use machine learning libraries (scikit-learn, TensorFlow)")
        print("   • Implement real-time recommendation updates")

def main():
    """Main function to run the demo."""
    recommender = SimpleAnimeRecommender()
    recommender.demo()

if __name__ == '__main__':
    main()
