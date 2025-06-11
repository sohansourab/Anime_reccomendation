#!/usr/bin/env python3
"""
Test script for the anime recommendation system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_loader():
    """Test the data loading functionality."""
    print("Testing data loader...")
    
    try:
        from data_loader import AnimeDataLoader
        
        loader = AnimeDataLoader()
        anime_df, ratings_df = loader.load_sample_data()
        user_item_matrix = loader.create_user_item_matrix()
        
        assert len(anime_df) > 0, "No anime data loaded"
        assert len(ratings_df) > 0, "No ratings data loaded"
        assert user_item_matrix.shape[0] > 0, "Empty user-item matrix"
        
        print("✓ Data loader working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Data loader test failed: {e}")
        return False

def test_collaborative_filtering():
    """Test the collaborative filtering functionality."""
    print("Testing collaborative filtering...")
    
    try:
        from data_loader import AnimeDataLoader
        from collaborative_filtering import CollaborativeFilteringRecommender
        
        loader = AnimeDataLoader()
        loader.load_sample_data()
        user_item_matrix = loader.create_user_item_matrix()
        
        recommender = CollaborativeFilteringRecommender(loader)
        recommender.fit(user_item_matrix)
        
        # Test recommendations
        user_recommendations = recommender.recommend_user_based(1, 5)
        item_recommendations = recommender.recommend_item_based(1, 5)
        
        assert len(user_recommendations) > 0, "No user-based recommendations"
        assert len(item_recommendations) > 0, "No item-based recommendations"
        
        # Test similarity
        similar_users = recommender.get_similar_users(1, 5)
        similar_anime = recommender.get_similar_anime(1, 5)
        
        print("✓ Collaborative filtering working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Collaborative filtering test failed: {e}")
        return False

def test_evaluator():
    """Test the evaluation functionality."""
    print("Testing evaluator...")
    
    try:
        from data_loader import AnimeDataLoader
        from collaborative_filtering import CollaborativeFilteringRecommender
        from evaluator import RecommenderEvaluator
        
        loader = AnimeDataLoader()
        loader.load_sample_data()
        user_item_matrix = loader.create_user_item_matrix()
        
        recommender = CollaborativeFilteringRecommender(loader)
        recommender.fit(user_item_matrix)
        
        evaluator = RecommenderEvaluator(recommender, loader)
        train_data, test_data = evaluator.split_data(test_size=0.2)
        
        assert len(train_data) > 0, "No training data"
        assert len(test_data) > 0, "No test data"
        
        print("✓ Evaluator working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Evaluator test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running Anime Recommendation System Tests\n")
    
    tests = [
        test_data_loader,
        test_collaborative_filtering,
        test_evaluator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The recommendation system is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == '__main__':
    exit(main())
