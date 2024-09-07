## L3 Data Visualization Results

For the third L3 preprocessing there are not much results to display since the majority of features were analyzed and extracted in the previous preprocessings. 

In this process we did the following (based on our results found during L1 and L2): 
- One-hot encode the Region parameter
- Combine the languages that are less than 2% present and then do one-hot encoding to the review language
- Convert to categorical the hotel name (giving it an ID)
- Removing the latitude and the longitude columns for their lack of usage 


Once this is performed we should tackle the `review_text_translated` feature. 
- Our goal is to extract meaningful and useful information for a later ML model out of the review text. 
- For that we decided to use some NLP techniques (a Word Cloud and Sentiment analysis was already done in L1 visualization where we already extracted results)

Which NLP techniques could we use?? 

1. **TF-IDF (Term Frequency-Inverse Document Frequency):**
   - **Why:** TF-IDF is a well-established method that helps identify the importance of words in a document relative to the entire dataset. It balances the frequency of words with their distinctiveness across the dataset, which is crucial when dealing with a large number of reviews.
   - **How:** Convert your text data into a TF-IDF matrix, where each review is represented as a vector. This technique can help you capture the importance of specific words that might correlate strongly with ratings (e.g., "excellent" might correlate with higher ratings).

2. **Word Embeddings (e.g., Word2Vec, GloVe):**
   - **Why:** Word embeddings capture the semantic meaning of words in a continuous vector space, where words with similar meanings are close to each other. This is particularly useful for capturing nuances in review text.
   - **How:** You can use pre-trained embeddings or train your own on the review dataset. Each review can be represented by averaging the word vectors (mean embedding) or using more sophisticated approaches like weighted averaging based on TF-IDF scores.

3. **N-grams (Bi-grams, Tri-grams):**
   - **Why:** While individual words are informative, certain combinations of words (like "not good," "highly recommend") carry significant meaning. N-grams can help capture these phrases.
   - **How:** Extend your TF-IDF or BoW models to include bi-grams or tri-grams. This can be especially useful if your reviews contain many such meaningful phrases.

4. **Sentiment Analysis:**
   - **Why:** Sentiment polarity (positive, negative) and intensity can be directly related to the ratings. A strongly positive review is likely to have a higher rating, and vice versa.
   - **How:** Apply a sentiment analysis model (e.g., VADER, TextBlob, or even a custom sentiment model) to extract sentiment scores. These scores can be used as additional features alongside TF-IDF or embeddings.

5. **Text Length and Readability Scores:**
   - **Why:** The length of the review and its readability might correlate with the detail and thoroughness of the review, which in turn might influence the rating.
   - **How:** Compute features such as the number of words, sentences, and Flesch-Kincaid readability scores for each review. These features can be useful in combination with text-based features.

6. **Topic Modeling (LDA - Latent Dirichlet Allocation):**
   - **Why:** LDA can uncover hidden topics within reviews, which might correlate with different ratings. For example, reviews discussing "cleanliness" might have different ratings than those discussing "location."
   - **How:** Use LDA to assign topic probabilities to each review. These topic distributions can serve as features, helping the model understand which aspects of a review contribute to the rating.

Once we decide which NLP techniques to explore, we should visualize them and see which one is the most likely to be fruitful in the training phase. 



### COURSE OF ACTION

- [X] Take out NLP entirely from L3 preprocessing. (1h)
- [X] Do a visualization dashboard with all the NLP techniques and decide which one is the one we should select. (3h)
- [X] Create a `data_preprocessing_nlp.py` where all the necessary transformations before the model will be performed (also chosen NLP techniques). (2h)
- [ ] Re-write L1, L2 sections with modifications made (2h)
- [ ] Write L3 preprocessing section (1h)
- [ ] Write NLP section (2h)
- [ ] Write NLP results (3h)
- [ ] Select my model label and evaluation metrics. (4h)
- [ ] Create a basic ML model that uses my preprocessed data and the selected evaluation metrics.
- [ ] Analyze the results and create a way to evaluate the ML models created
- [ ] Fine tune the model and add a configuration file with multiple models
- [ ] Train multiple models and evaluate them (select best fitted model and create a performance dashboard)


### ADDITIONAL INFORMATION

```python
def add_word_embeddings(l2_data):
    """
    Add word embeddings using Word2Vec.
    """
    # Tokenize text for word embeddings
    l2_data['tokenized_review'] = l2_data['review_text_translated'].apply(lambda x: x.split())

    # Train Word2Vec model on the tokenized reviews
    model = Word2Vec(sentences=l2_data['tokenized_review'], vector_size=100, window=5, min_count=1, workers=4)

    def get_average_embedding(tokens):
        vectors = [model.wv[word] for word in tokens if word in model.wv]
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(model.vector_size)
    
    # Apply the embedding to each review
    l2_data['embedding'] = l2_data['tokenized_review'].apply(get_average_embedding)

    # Split the embedding into separate columns
    embedding_df = pd.DataFrame(l2_data['embedding'].tolist(), index=l2_data.index)
    embedding_df.columns = [f'embedding_{i}' for i in range(embedding_df.shape[1])]

    # Concatenate the embeddings with the original data
    l2_data = pd.concat([l2_data, embedding_df], axis=1)
    l2_data = l2_data.drop(['tokenized_review', 'embedding'], axis=1)
    
    return l2_data
```