### 5. **Evaluation and Optimization**

- Evaluate model performance using appropriate metrics (e.g., RMSE, MAE).
- Optimize models through hyperparameter tuning and cross-validation.

### 6. **Deployment**

Deploy the trained model using AWS SageMaker, Flask API, or any other preferred deployment method. Integrate with the user interface for real-time recommendations.

### Example Deployment with Flask
```python
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    processed_review = preprocess_text(data['review'])
    tfidf_features = tfidf_vectorizer.transform([processed_review]).toarray()
    numerical_features = np.array([data['avg_rating'], data['latitude'], data['distance_to_ski_resort'], data['distance_to_city_center']])
    combined_features = np.hstack((tfidf_features, numerical_features.reshape(1, -1)))
    
    prediction = model.predict(combined_features)
    return jsonify({'prediction': prediction[0]})

if __name__ == '__main__':
    app.run(debug=True)
```

-----------------------------------------------------------------------------------------------------------------

To reduce overfitting, we can modify your training procedure by applying several strategies:

### 1. **Add Regularization to the Models**
Regularization techniques like `L2` (Ridge) or `L1` (Lasso) penalize large weights in the model and help reduce overfitting. Some models you’re using already support this:

- **Gradient Boosting** and **Random Forest**: You can tune hyperparameters like `max_depth`, `min_samples_split`, `min_samples_leaf`, and `n_estimators`. These control the complexity of the trees and help regularize the model.
- **Support Vector Machine (SVM)**: Use the regularization parameter `C`. A lower value of `C` increases regularization and helps prevent overfitting.
- **Neural Network**: You can add regularization parameters (e.g., L2 penalty) in the `MLPRegressor`.

### 2. **Early Stopping for Gradient Boosting and Neural Networks**
Use early stopping to prevent overfitting during training. This stops training once the validation error starts to increase.

### 3. **Cross-Validation for Model Selection**
Use `cross-validation` to select the best hyperparameters. You are already doing `RandomizedSearchCV`, but increasing the number of iterations and using cross-validation on the training data can help avoid overfitting by selecting more generalized models.

### 4. **Feature Scaling**
You are scaling the data with `StandardScaler`. Ensure all models that benefit from scaled data (e.g., `SVM` and `Neural Networks`) are using scaled input. For tree-based models, scaling does not affect their performance as much.

### 5. **Increase Regularization Parameters**
In models like `GradientBoostingRegressor` and `RandomForestRegressor`, higher regularization (like increasing `min_samples_split`, `min_samples_leaf`, or reducing `max_depth`) will help in reducing overfitting.

### Key Adjustments:
1. **Tuned Regularization for Tree Models**: Increased `min_samples_split` and `min_samples_leaf`, and reduced `max_depth` to prevent overfitting.
2. **Gradient Boosting**: Added subsampling and reduced `max_depth` to build weaker learners.
3. **Neural Network**: Added early stopping and `alpha` for L2 regularization.

### Other Considerations:
- **Increase Cross-Validation**: Consider increasing the number of cross-validation folds in `RandomizedSearchCV` (e.g., `cv=5` or `cv=10`) for more robust model selection.
- **Check for Feature Importance**: Remove or scale down less important features, which may contribute to overfitting.
