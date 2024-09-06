# NLP results explanation

## TF-IDF Results

### 1. Word Cloud of Important Words (TF-IDF)
The **word cloud** represents the most important words extracted from the review texts using the TF-IDF (Term Frequency-Inverse Document Frequency) method. Larger words are more significant, meaning they occur frequently in the reviews but are also distinctive to particular reviews.

- **Interpretation**: Words like *"good"*, *"hotel"*, *"clean"*, and *"staff"* are large and prominent, which indicates these words frequently appear in reviews and are considered important across different documents (reviews).
- **Usefulness**: This visualization helps us identify which terms are emphasized in customer reviews. For example, *"staff"*, *"room"*, and *"breakfast"* are key focus points, which are typical aspects that could affect a review's sentiment. However, it doesn't give direct insight into how these words impact ratings.

### 2. TF-IDF Reduced to 2D Space (Colored by Review Rating)
This plot uses **dimensionality reduction** to map high-dimensional TF-IDF vectors into a 2D space. Each point represents a review, and the color represents its review rating (as indicated by the color bar).

- **Interpretation**: The scatter plot shows how the TF-IDF vectors, which are the transformed representations of the reviews, cluster in this reduced 2D space. The color gradient (from blue to red) indicates the review rating. Most reviews seem to cluster within certain bounds, with some variation in specific areas.
- **Usefulness**: This visualization gives a sense of how reviews with similar word distributions group together. While the plot shows some grouping based on the review content, the lack of clear separation between high and low ratings suggests that TF-IDF may capture some aspects of the reviews but not enough to clearly distinguish reviews by rating alone. The proximity of blue (low ratings) and red (high ratings) points indicates that similar words may be used across different review ratings.

### 3. Top 15 Words Correlated with Review Ratings
This **heatmap** shows the top 15 words that are positively correlated with the review ratings. Words like *"great"*, *"excellent"*, and *"friendly"* have higher correlations with better review ratings.

- **Interpretation**: Words such as *"great"*, *"excellent"*, *"friendly"*, and *"clean"* are positively correlated with higher ratings, which indicates that these words tend to appear more often in positive reviews (higher review ratings). The correlation values aren't very high, but they still suggest some relationship between these words and higher ratings.
- **Usefulness**: This plot is useful because it indicates that certain positive words are predictive of higher review ratings. However, the relatively low correlation values (none above 0.16) suggest that while there is a relationship between these words and review ratings, it is not a very strong one. Other factors in the review text or additional features might be more predictive of the rating.

### **Summary and Utility of TF-IDF:**
- **Strengths**: TF-IDF provides a way to understand the relative importance of words in the reviews and their relationship with ratings. The word cloud and correlated word analysis reveal important insights into the language customers use and highlight patterns that might influence the overall review score.
- **Limitations**: Despite capturing word importance, TF-IDF seems to have limitations in clearly separating reviews based on ratings. The scatter plot shows no clear, distinct clusters, meaning the TF-IDF vectors alone do not fully capture the differences between high- and low-rated reviews. Also, the correlations between individual words and review ratings are relatively weak, indicating that word importance alone (without other contextual or structural information) might not be enough to make strong predictions about review ratings.

Thus, **TF-IDF is a useful feature**, but it might not be sufficient by itself for predicting review ratings. It can be one of many features in a more complex model that also considers other aspects like sentiment, review length, or even deeper semantic embeddings.


## Word Embeddings

### 1. **Word Embeddings Reduced to 2D Space (Colored by Review Rating)**

- **Plot Overview**: This is a PCA (Principal Component Analysis) projection of the word embeddings into 2D space. Each point represents a review, and the color of the points corresponds to the review rating, ranging from blue (lower ratings) to red (higher ratings).
  
- **Interpretation**:
  - The reviews tend to cluster in specific regions of the plot, which indicates that the word embeddings capture similarities in reviews' semantic content.
  - Reviews with higher ratings (lighter colors) are spread more evenly, while the lower ratings (darker colors) seem to concentrate in certain areas.
  - The variability seen in this plot indicates that reviews with different ratings often use different semantic content, which is what we would expect if the reviews reflect different experiences.

- **Insights for the ML Model**:
  - The embeddings effectively capture useful distinctions between reviews based on semantic meaning, and PCA helps visualize the diversity in reviews. Since there is a spread across different review ratings, embeddings can likely help in predicting review ratings by clustering similar reviews together.
  - The plot suggests that word embeddings would be useful in a model for distinguishing between different reviews based on their content.

### 2. **Word Cloud of Important Words (Word Embeddings)**

- **Plot Overview**: This word cloud shows the most important and frequently used words in the reviews. The size of each word represents its frequency or relevance, determined using word embeddings.
  
- **Interpretation**:
  - Words like "room", "hotel", "breakfast", "stay", and "good" are some of the largest, indicating they are key terms in the reviews.
  - The presence of other contextual words like "parking", "service", and "location" highlights the specific aspects of the hotel experiences that customers care about.
  - This word cloud illustrates the semantic information captured by the embeddings, showing the key topics around which the reviews are centered.

- **Insights for the ML Model**:
  - The word embeddings are capturing useful contextual relationships between terms. Words that frequently co-occur and are semantically similar are placed close to each other in the embedding space. This reinforces that embeddings provide meaningful features that can differentiate between reviews.
  - The diversity of words, ranging from "price" to "restaurant" and "clean", indicates that the model can capture various aspects of the review experience, making embeddings useful for the prediction task.

### 3. **Correlation Between PCA Components and Review Ratings**

- **Plot Overview**: This heatmap shows the correlation between the first two PCA components of the word embeddings and the review ratings.
  
- **Interpretation**:
  - The first PCA component (`pca_1`) has a slight negative correlation (-0.15) with the review rating. This suggests that as values on this component increase, the review ratings tend to decrease, though the correlation is not very strong.
  - The second PCA component (`pca_2`) has a positive correlation (0.49) with the review rating. This is a stronger relationship, indicating that this component captures information that aligns well with review ratings, where higher values correspond to higher ratings.

- **Insights for the ML Model**:
  - The fact that the second PCA component correlates positively with the review ratings suggests that word embeddings capture aspects of the reviews that are highly related to rating sentiment.
  - The correlation values are moderate, meaning that embeddings capture some aspects of the reviews that influence ratings, but there may be other factors outside the textual data (e.g., user biases or external factors) that could also impact ratings.

### **Conclusion on Using Word Embeddings in the ML Model**:

Word embeddings appear to be a highly valuable feature for the ML model. Here's why:
- **Semantic Richness**: Embeddings capture nuanced relationships between words, which means the model can differentiate between reviews based on the contextual meaning of the words used.
- **Clustering and Spread**: The PCA reduction shows that different reviews with varying ratings cluster together based on their embeddings, suggesting that embeddings can help the model learn from patterns in the reviews.
- **Correlations with Ratings**: The strong correlation of the second PCA component with review ratings suggests that embeddings can explain a significant portion of the variance in review ratings, making them a good predictor for the model.

Incorporating word embeddings into your ML model should help improve its performance by capturing semantic and contextual information from the review texts, which could enhance its predictive power.

## N-Grams

### 1. **Word Cloud of Important Bi-grams (TF-IDF)**:
   - **What it shows**: This word cloud highlights the most significant bi-grams (two-word phrases) in the dataset based on their TF-IDF scores. Larger and bolder words represent bi-grams that occur frequently but are also weighted by their importance (distinctiveness) across all reviews.
   - **Key Insights**:
     - Some key phrases such as "good location," "friendly staff," and "great hotel" are repeated frequently and carry significant meaning.
     - These common bi-grams align with frequent topics of discussion in reviews, like hotel location, service, and staff quality, which could be useful indicators for predicting ratings.
   - **Interpretation**: The presence of common bi-grams like "friendly staff" and "great location" suggests that certain combinations of words carry more weight in user sentiment and satisfaction. This can be valuable for modeling, especially in identifying key aspects of reviews that influence overall sentiment and rating.

### 2. **Bi-grams Reduced to 2D Space (Colored by Review Rating)**:
   - **What it shows**: This plot reduces the TF-IDF representation of bi-grams to two dimensions using SVD (Singular Value Decomposition), with points colored by review ratings. Each point represents a review, and its position in 2D space is influenced by the bi-gram combinations within it.
   - **Key Insights**:
     - The plot shows a general clustering of data points, although there isn't a very strong visible separation between reviews with different ratings.
     - There is some spread in the data, but the differentiation of ratings based on bi-grams seems limited based on the color distribution across the plot.
   - **Interpretation**: While bi-grams capture more information than unigrams (individual words), this plot suggests that bi-grams alone may not provide enough separation between different review ratings. More sophisticated or complementary features might be required to improve prediction accuracy.

### 3. **Correlation Between SVD Components and Review Ratings**:
   - **What it shows**: This heatmap displays the correlation between the first two SVD components (which represent the most important dimensions of bi-grams in 2D space) and the review ratings.
   - **Key Insights**:
     - The correlations are relatively low, with a maximum of 0.09 between Component 1 and the review rating.
     - This suggests that the bi-gram components are not strongly correlated with review ratings, meaning that bi-grams may not be highly predictive of the review ratings in this case.
   - **Interpretation**: The low correlation values imply that while bi-grams capture some structure in the review text, they don't strongly correlate with the target variable (review rating). This might indicate that while bi-grams can capture valuable information, additional features or transformations may be needed to improve model performance.

### **Conclusion on Bi-grams for ML Modeling**:
Bi-grams provide useful insight into the structure of the reviews, capturing key phrases that are likely meaningful to users. However, based on the analysis:
- **Strengths**:
  - Bi-grams help identify important phrases like "friendly staff" and "good location," which are valuable in understanding user sentiment.
  - They can be useful for models that need to consider word combinations rather than individual words.
- **Limitations**:
  - The correlation with review ratings is relatively low, which suggests that on their own, bi-grams might not be the most effective feature for predicting ratings.
  - Complementing this with other features, such as embeddings or metadata (e.g., review length, sentiment scores), or exploring tri-grams might provide a more robust signal for a predictive model.

Thus, while bi-grams are informative, they should likely be combined with other features to be truly valuable in an ML model designed to predict review ratings.


## Sentiment Analysis

### 1. **Sentiment Distribution Across Reviews**
In the first plot, we see the distribution of reviews classified as **Positive**, **Neutral**, or **Negative** based on sentiment analysis. This chart shows the sentiment analysis applied across the entire dataset.

#### Key Insights:
- **Positive Reviews** make up 80% of the total reviews, which dominates the distribution. This indicates that most users leave favorable reviews.
- **Neutral Reviews** account for about 11% of the total.
- **Negative Reviews** represent the smallest portion at 8.8%.

This distribution gives a sense of the overall sentiment tone in the dataset. The high proportion of positive reviews might suggest a bias towards positive experiences, but this could also affect the performance of an ML model, especially when training it to distinguish ratings based on sentiment alone.

### 2. **Sentiment Comparison Across Regions (One-Hot Encoded)**
This is a **stacked bar chart** showing the distribution of sentiments across different regions, now represented with one-hot encoded variables for each region.

#### Key Insights:
- All regions seem to follow a similar pattern, with **Positive Sentiments** making up the bulk of the reviews.
- **Negative Sentiments** are generally quite small across all regions, but there are some variations.
- Some regions, like **Ordino**, show a slightly higher negative sentiment ratio, while others, like **Encamp**, have fewer negative reviews.

This plot can be useful for detecting if sentiment varies significantly between different regions or locales, which could provide additional features to the ML model. However, because the variance across regions seems minimal, this feature may only provide limited additional predictive power in some cases.

### **Sentiment Analysis and its Usefulness for ML Model**
Sentiment analysis could be **useful** as a feature in the ML model because:
1. **Direct Correlation to Review Ratings**: Sentiment is a good proxy for overall satisfaction, and typically positive sentiment correlates with higher ratings, while negative sentiment correlates with lower ones.
2. **Added Predictive Value**: Since review texts express subjective feelings and impressions, they can serve as a strong predictor of numerical ratings. Sentiment analysis, when combined with other features like word embeddings or TF-IDF, can give the model a better understanding of whether the review aligns with the given score.

However, given the **imbalance** (with 80% positive reviews), the model might need techniques such as **class weighting** or **sampling strategies** to handle this skewed distribution and improve its predictions for negative and neutral sentiments.

#### Conclusion:
Sentiment analysis is a **valuable feature** for predicting review ratings. Despite the imbalance, it could add significant value when combined with other features (e.g., n-grams or word embeddings).


## Text Length and Readability Scores

### 1. **Distribution of Review Lengths (Number of Words)**

- **What the plot shows**: This histogram visualizes the distribution of the number of words per review. Most reviews are relatively short, with the majority containing fewer than 200 words. The curve peaks early, indicating that most reviews are quite concise, with a steep drop-off in frequency as the review length increases.
  
- **Analysis**: Short reviews dominate, while longer, more detailed reviews are less common. This information is useful because the length of a review might correlate with how thorough the review is. For example, longer reviews might indicate a more detailed experience or more extreme satisfaction/dissatisfaction.
  
- **Should this feature be used in the ML model?**: Yes, text length is a good feature to include because it could capture review thoroughness or user engagement, both of which might correlate with review ratings.


### 2. **Flesch-Kincaid Grade Level vs. Review Rating**

- **What the plot shows**: This scatter plot compares the Flesch-Kincaid grade level (a measure of how difficult the text is to read) to the review rating. The color of each point corresponds to the review rating. A few reviews have very high grade levels (complex language), but the majority fall under 100.
  
- **Analysis**: Reviews with lower grade levels are more common, and higher-grade reviews (more complex language) are relatively rare. Reviews with higher ratings tend to have lower Flesch-Kincaid scores (indicating simpler language), though the relationship is not clear-cut. This shows that people tend to write simpler reviews, especially when their rating is high.
  
- **Should this feature be used in the ML model?**: Yes, readability scores like the Flesch-Kincaid grade level can be useful for distinguishing between reviews. Reviews that are too simple or too complex may correlate differently with ratings, providing more nuanced insights into reviewer intent and satisfaction.


### 3. **Distribution of Flesch Reading Ease Scores**

- **What the plot shows**: This histogram displays the distribution of Flesch Reading Ease scores. The Flesch Reading Ease score measures how easy a review is to read: higher scores indicate easier reading (simple language), and lower (or negative) scores indicate more complex or difficult language. The distribution shows that most reviews are on the more difficult end of the scale, with the highest concentration of reviews having lower reading ease scores.
  
- **Analysis**: The majority of reviews are somewhat difficult to read, as indicated by the lower scores on the Flesch scale. There are fewer extremely easy or extremely complex reviews. This is an important observation because it shows that most users write reviews using moderately complex language. Negative values might indicate unusual or misparsed text, which could be worth investigating.
  
- **Should this feature be used in the ML model?**: Yes, including the Flesch Reading Ease score provides an additional measure of complexity, which may help distinguish between review types and rating outcomes. If reviewers with extreme satisfaction or dissatisfaction write more complex reviews, this feature could be highly informative.


### **Conclusion**

Both text length and readability are useful features for an ML model:

- **Text Length**: Correlates with review detail and engagement. More detailed reviews might capture more extreme user experiences (both positive and negative).
  
- **Readability Scores (Flesch-Kincaid and Flesch Reading Ease)**: These scores provide insights into how complex or simple the review language is. Simpler language could be associated with casual reviewers, while more complex language could indicate greater effort or thoroughness, which might relate to specific ratings.


## Topic Modelling (LDA)

### 1. **Word Cloud for Each Topic:**
   - **Description:** The first image shows the most important words for five topics generated by LDA. Each topic is represented by words that appear most frequently in the documents assigned to that topic. The size of each word represents its importance within the topic.
     - **Topic 1:** Words like "hotel," "room," and "staff" dominate, suggesting a general topic around hotel stay experiences.
     - **Topic 2:** Words like "avec" and "est" suggest that this topic might capture reviews in French, possibly about the location or service.
     - **Topic 3:** Common review words like "good," "breakfast," and "clean" point toward reviews focusing on cleanliness and food.
     - **Topic 4:** This topic includes many Spanish words like "para," "con," and "hotel," indicating Spanish-language reviews possibly discussing services or amenities.
     - **Topic 5:** Catalan words like "per" and "molt" appear in this topic, which could represent reviews in Catalan.

   - **Insights:** 
     - The word clouds effectively show that LDA can separate reviews into interpretable topics related to different aspects of hotel stays, such as cleanliness, service, or language differences.
     - This segmentation could be useful in identifying which topics have the greatest influence on review ratings, helping the ML model to account for what aspects of the review text contribute to a particular rating.

### 2. **Topic Distributions for Reviews:**
   - **Description:** The second plot is a heatmap showing how reviews are distributed across different topics. Each row corresponds to a topic, and the intensity of the color (red for higher values and blue for lower values) shows the probability of each review belonging to that topic.
     - **Topic 0 and 1:** Certain reviews are strongly associated with these topics (indicated by the strong red colors), suggesting these topics are dominant in these reviews.
     - **Topic 3 and 4:** These topics are more weakly associated across reviews, with lower probabilities (more blue bars).
     - **Topic 2:** This seems to cover a mix of different reviews with varying degrees of association.
     
   - **Insights:**
     - This visualization shows how different topics contribute to each review and demonstrates the extent to which reviews are associated with each of the five identified topics. If certain topics (e.g., cleanliness, service) are found to correlate strongly with specific ratings (positive or negative), this can be useful for the ML model to weigh those topics more heavily when predicting ratings.
     - For example, reviews that strongly associate with "cleanliness" (say, Topic 1) might have higher ratings than those associated with a topic about "poor service" (if one exists).

### **Conclusion**

Would LDA be Useful in Your ML Model? **Yes**, LDA could be highly useful for your ML model for several reasons:
1. **Topic Discrimination:** The LDA model segments the review corpus into distinct topics that represent different aspects of hotel reviews (cleanliness, service, amenities, etc.). These can be strong predictors of ratings.
2. **Review Categorization:** By assigning reviews to topics, the ML model can better understand which aspects of a review are more important to the reviewer, potentially improving rating predictions.
3. **Latent Features:** The topic probabilities (e.g., 20% cleanliness, 50% service, etc.) generated by LDA can be used as additional input features in the model, providing a more nuanced understanding of the review content.

By integrating LDA topic distributions into your feature set, you allow the model to capture the underlying themes of the reviews, which could improve prediction accuracy when correlating these themes with ratings.


## Final Recommendations for NLP Techniques to Include:
1. **Word Embeddings (BERT)**: For capturing deep semantic meaning and context.
2. **TF-IDF**: To capture basic term importance across reviews.
3. **Sentiment Analysis**: To provide a direct feature correlating with the rating.
4. **Text Length and Readability**: For review detail and complexity.
5. **LDA Topics**: To capture underlying themes that influence the review rating.
6. **N-Grams (Selectively)**: For identifying key phrases that correlate with the review rating.

By combining these features, you can leverage the strengths of each NLP technique. The more advanced techniques (e.g., embeddings and topic modeling) will capture deeper insights, while the simpler techniques (TF-IDF, n-grams) provide additional context and structure.

### Script Outline for Implementation:

Based on these recommendations, you can adjust your script to apply these selected NLP techniques and generate a comprehensive dataset for your ML model. Here's how you can structure your script to include these features:

1. **Apply BERT embeddings**: To capture semantic content.
2. **Apply TF-IDF**: For word importance.
3. **Apply sentiment analysis**: For direct sentiment information.
4. **Apply text length and readability scores**: For detail and complexity.
5. **Apply LDA topic modeling**: To capture latent topics.
6. **Optional N-Grams**: If further contextual understanding is needed. 