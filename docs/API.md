# API Documentation

## Core Classes

### AnimeDataLoader

Handles data loading and preprocessing.

```python
loader = AnimeDataLoader()
anime_df, ratings_df = loader.load_sample_data()
user_item_matrix = loader.create_user_item_matrix()
```

### CollaborativeFilteringRecommender

Main recommendation engine.

```python
recommender = CollaborativeFilteringRecommender(loader)
recommender.fit(user_item_matrix)

# Get recommendations
recommendations = recommender.recommend_user_based(user_id=1, n_recommendations=5)
similar_anime = recommender.get_similar_anime(anime_id=1, n=5)
```

### RecommenderEvaluator

Performance evaluation tools.

```python
evaluator = RecommenderEvaluator(recommender, loader)
results = evaluator.run_full_evaluation()
```

## Method Reference

### Recommendation Methods
- `recommend_user_based(user_id, n_recommendations, k)`
- `recommend_item_based(user_id, n_recommendations, k)`
- `get_similar_users(user_id, n)`
- `get_similar_anime(anime_id, n)`

### Prediction Methods
- `predict_user_based(user_id, anime_id, k)`
- `predict_item_based(user_id, anime_id, k)`

### Evaluation Methods
- `evaluate_predictions(test_data, method, k)`
- `evaluate_recommendations(test_users, method, n_recommendations, k)`
- `run_full_evaluation(test_size)`
