# Algorithm Documentation

## Collaborative Filtering Overview

Collaborative filtering is based on the idea that users who agreed in the past will agree in the future, and that they will like similar kinds of items as they liked in the past.

## User-Based Collaborative Filtering

### Algorithm Steps:
1. **Build User-Item Matrix**: Create a matrix where rows are users and columns are items
2. **Calculate User Similarities**: Use cosine similarity to find similar users
3. **Predict Ratings**: For unrated items, predict ratings based on similar users
4. **Generate Recommendations**: Recommend top-N items with highest predicted ratings

### Cosine Similarity Formula:
```
similarity(u, v) = (u · v) / (||u|| × ||v||)
```

### Rating Prediction Formula:
```
prediction(u, i) = mean(u) + Σ(similarity(u, v) × (rating(v, i) - mean(v))) / Σ|similarity(u, v)|
```

## Item-Based Collaborative Filtering

### Algorithm Steps:
1. **Build Item-User Matrix**: Transpose of user-item matrix
2. **Calculate Item Similarities**: Find items that are rated similarly by users
3. **Predict Ratings**: Based on similarity to items user has already rated
4. **Generate Recommendations**: Recommend items most similar to user's preferences

### Advantages and Disadvantages

#### User-Based CF:
**Pros:**
- Intuitive and explainable
- Works well with sufficient user data
- Good for serendipitous recommendations

**Cons:**
- Scalability issues with large user bases
- Sparsity problems
- Cold start problem for new users

#### Item-Based CF:
**Pros:**
- More stable over time
- Better scalability
- Pre-computation possible

**Cons:**
- Less diversity in recommendations
- Popularity bias
- Cold start for new items

## Implementation Details

### Similarity Thresholds
- Minimum similarity: 0.1 (ignore very low similarities)
- Neighborhood size (k): 20 users/items (configurable)

### Handling Edge Cases
- New users: Recommend popular items
- New items: Use content-based features
- No similar users/items: Fall back to average ratings

### Performance Optimizations
- Sparse matrix operations
- Pre-computed similarities
- Approximate nearest neighbors for large datasets
