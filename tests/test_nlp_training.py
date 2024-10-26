# coverage run -m pytest -q tests/test_nlp_training.py
# coverage report --show-missing --include=nlp_training.py --omit=/tests/


import pytest
import pandas as pd
import argparse
from unittest.mock import patch


from src.nlp_training import parse_args, apply_tfidf, apply_lda, apply_ngrams, apply_nlp_techniques, apply_sentiment_analysis, apply_text_length_readability, apply_word2vec_embeddings

def test_parse_args():
    # Mock the command line arguments
    test_args = ["--techniques", "tfidf,sentiment,lda"]
    
    with patch('sys.argv', ["test_script.py"] + test_args):
        args = parse_args()
        assert args.techniques == "tfidf,sentiment,lda"

def test_apply_tfidf():
    # Mock dataframe with a 'review_text_translated' column
    df = pd.DataFrame({
        'review_text_translated': [
            "This is a great place to stay", 
            "I had a terrible experience", 
            "Absolutely loved the service and the rooms"
        ]
    })

    # Apply TF-IDF
    df_tfidf = apply_tfidf(df, n_features=5)

    # Verify the resulting dataframe shape (should have additional columns)
    assert df_tfidf.shape[1] > df.shape[1]  # Check that new columns were added
    assert 'review_text_translated' in df_tfidf.columns  # Original column should still be there
    assert len(df_tfidf.columns) > len(df.columns)  # Additional TF-IDF columns should be present


def test_apply_word2vec_embeddings():
    # Sample data with review text
    df = pd.DataFrame({
        'review_text_translated': [
            "This hotel is fantastic and the service is excellent",
            "The room was dirty and the staff were rude",
            "I enjoyed my stay; the location was perfect"
        ]
    })

    # Apply Word2Vec embeddings
    df_with_embeddings = apply_word2vec_embeddings(df, n_components=3, vector_size=10)  # Use fewer components for simplicity

    # Check that new embedding columns are added
    assert df_with_embeddings.shape[1] > df.shape[1]
    
    # Check that embedding columns start with "word2vec_" and there are exactly `n_components` new columns
    embedding_columns = [col for col in df_with_embeddings.columns if col.startswith("word2vec_")]
    assert len(embedding_columns) == 3  # n_components = 3
    
    # Ensure embedding columns have numeric values
    assert df_with_embeddings[embedding_columns].applymap(lambda x: isinstance(x, (float, int))).all().all()


def test_apply_sentiment_analysis():
    # Sample data with review text
    df = pd.DataFrame({
        'review_text_translated': [
            "This was a fantastic experience!",
            "Terrible service and very rude staff.",
            "Average stay, nothing special."
        ]
    })

    # Apply sentiment analysis
    df_with_sentiment = apply_sentiment_analysis(df)

    # Check that a new sentiment_polarity column is added
    assert 'sentiment_polarity' in df_with_sentiment.columns
    
    # Check that the sentiment_polarity column has values between -1 and 1
    assert df_with_sentiment['sentiment_polarity'].between(-1, 1).all()
    
    # Ensure sentiment values make sense given the sample data
    assert df_with_sentiment['sentiment_polarity'][0] > 0  # Positive review
    assert df_with_sentiment['sentiment_polarity'][1] < 0  # Negative review
    assert df_with_sentiment['sentiment_polarity'][2] == pytest.approx(0, abs=0.2)  # Neutral review


def test_apply_ngrams():
    # Sample data with review text
    df = pd.DataFrame({
        'review_text_translated': [
            "This hotel is fantastic and the service is excellent",
            "The room was dirty and the staff were rude",
            "I enjoyed my stay; the location was perfect"
        ]
    })

    # Apply bigrams with a maximum of 5 features
    df_with_ngrams = apply_ngrams(df, n_features=5)

    # Check that new n-gram columns are added
    assert df_with_ngrams.shape[1] > df.shape[1]  # New columns should be added
    assert 'review_text_translated' in df_with_ngrams.columns  # Original column should still be there

    # Check that the new columns are indeed bigrams
    ngram_columns = df_with_ngrams.columns.difference(df.columns)
    for col in ngram_columns:
        assert len(col.split()) == 2  # Each bigram should contain two words

    # Check that the n-gram features contain numeric values (counts)
    assert df_with_ngrams[ngram_columns].applymap(lambda x: isinstance(x, (int, float))).all().all()


def test_apply_lda():
    # Sample data with review text
    df = pd.DataFrame({
        'review_text_translated': [
            "The hotel was beautiful and had a fantastic view",
            "The food was excellent and the staff were friendly",
            "I had a terrible experience with the room cleanliness",
            "The location was great but the service was slow",
            "Amazing room and wonderful amenities, would visit again"
        ]
    })

    # Apply LDA with a specified number of topics
    num_topics = 3
    df_with_lda = apply_lda(df, num_topics=num_topics)

    # Check that new topic columns are added
    assert df_with_lda.shape[1] > df.shape[1]  # New columns should be added
    assert 'review_text_translated' in df_with_lda.columns  # Original column should still be there

    # Check that the correct number of topic columns were added
    topic_columns = [col for col in df_with_lda.columns if col.startswith("topic_")]
    assert len(topic_columns) == num_topics  # There should be exactly `num_topics` topic columns

    # Check that topic columns contain numeric values representing topic probabilities
    assert df_with_lda[topic_columns].applymap(lambda x: isinstance(x, (float, int))).all().all()

    # Ensure that topic probabilities are within the range [0, 1] (as they represent probabilities)
    assert df_with_lda[topic_columns].applymap(lambda x: 0 <= x <= 1).all().all()

    # Confirm that topic probabilities for each row sum to approximately 1 (since it's a probability distribution)
    assert df_with_lda[topic_columns].sum(axis=1).apply(lambda x: pytest.approx(x, 0.1) == 1.0).all()

def test_apply_text_length_readability():
    # Sample data with review text
    df = pd.DataFrame({
        'review_text_translated': [
            "This is a fantastic place to stay!",
            "Awful experience, would not recommend.",
            "Decent location, reasonable prices."
        ]
    })

    # Apply text length readability function
    df_with_length = apply_text_length_readability(df)

    # Check that the 'review_length' column is added
    assert 'review_length' in df_with_length.columns

    # Verify that the 'review_length' column contains the correct character counts
    expected_lengths = df['review_text_translated'].apply(len).tolist()
    actual_lengths = df_with_length['review_length'].tolist()
    assert actual_lengths == expected_lengths


def test_apply_nlp_techniques():
    # THIS IS TESTED WITH THE GA
    pass


def test_main():
    # THIS IS ALREADY TESTED WITH THE GA
    pass