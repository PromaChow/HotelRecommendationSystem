import pandas as pd
import boto3
import os
import argparse
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from gensim.models import Word2Vec
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models.ldamodel import LdaModel
from gensim.corpora import Dictionary
from collections import Counter


# Function to parse input arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Apply selected NLP techniques")
    parser.add_argument('--techniques', type=str, default="w2v,sentiment,lda,length",
                        help="Comma-separated list of NLP techniques to apply")
    args = parser.parse_args()
    return args


def get_latest_parquet_file_path(s3_bucket, input_prefix):
    """
    List objects in the S3 bucket, find the latest Parquet file based on the LastModified timestamp.
    """
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=input_prefix)
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in the specified S3 bucket: {s3_bucket} with prefix: {input_prefix}")

        # Filter for Parquet files and sort by LastModified date
        parquet_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.parquet')]
        if not parquet_files:
            raise FileNotFoundError(f"No Parquet files found in the specified S3 bucket: {s3_bucket} with prefix: {input_prefix}")
        
        latest_file = max(parquet_files, key=lambda x: x['LastModified'])
        return f"s3://{s3_bucket}/{latest_file['Key']}"
    
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found. Please configure your credentials.")


def load_data(parquet_file_path):
    """
    Load the Parquet data from S3 into a Pandas DataFrame.
    """
    l3_data = pd.read_parquet(parquet_file_path)
    return l3_data


def save_to_s3(df, s3_bucket, output_prefix, current_datetime):
    """
    Save the DataFrame as a single Parquet file to S3 using boto3.
    """
    # Define the local temporary file path
    local_temp_path = f"/tmp/l3_data_{current_datetime}.parquet"

    # Save the DataFrame to a local Parquet file
    df.to_parquet(local_temp_path, engine='pyarrow', index=False)

    # Define the S3 output file name and path
    output_file_name = f"l3_data_{current_datetime}.parquet"
    final_output_path = f"{output_prefix}{output_file_name}"

    # Upload the local Parquet file to S3
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.upload_file(local_temp_path, s3_bucket, final_output_path)

    # Remove the local temporary file
    os.remove(local_temp_path)


# Function to apply TF-IDF
def apply_tfidf(df, n_features=20):
    tfidf_vectorizer = TfidfVectorizer(max_features=n_features)
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['review_text_translated'])
    tfidf_features = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())
    return pd.concat([df, tfidf_features], axis=1)

# Function to apply Word2Vec embeddings to the dataset
def apply_word2vec_embeddings(df, n_components=10, vector_size=100, window=5, min_count=1, workers=4):
    # Step 1: Prepare the text data for training the Word2Vec model
    sentences = df['review_text_translated'].apply(lambda x: x.split()).tolist()  # Tokenizing each review into words
    
    # Step 2: Train a Word2Vec model on the tokenized reviews
    word2vec_model = Word2Vec(sentences, vector_size=vector_size, window=window, min_count=min_count, workers=workers)
    
    # Step 3: Function to compute the mean word2vec embedding for each review
    def get_word2vec_embedding(text):
        words = text.split()  # Tokenize the text into words
        word_vectors = [word2vec_model.wv[word] for word in words if word in word2vec_model.wv]
        
        if len(word_vectors) > 0:
            # Compute the mean embedding for the review
            return np.mean(word_vectors, axis=0)
        else:
            # Return a zero vector if no words in the review are found in the model
            return np.zeros(vector_size)
    
    # Step 4: Apply the embedding function to each review
    embeddings = df['review_text_translated'].apply(get_word2vec_embedding)
    embeddings_df = pd.DataFrame(embeddings.tolist(), index=df.index)
    
    # Step 5: Perform dimensionality reduction with PCA (optional)
    pca = PCA(n_components=n_components)
    reduced_embeddings = pca.fit_transform(embeddings_df)
    reduced_df = pd.DataFrame(reduced_embeddings, columns=[f'word2vec_{i}' for i in range(n_components)])
    
    # Step 6: Return the original dataframe with the new Word2Vec embedding features
    return pd.concat([df, reduced_df], axis=1)

# Function to apply Sentiment Analysis
def apply_sentiment_analysis(df):
    df['sentiment_polarity'] = df['review_text_translated'].apply(lambda text: TextBlob(text).sentiment.polarity)
    return df

# Function to apply N-grams (Bigrams example)
def apply_ngrams(df, n_features=20):
    vectorizer = CountVectorizer(ngram_range=(2, 2), max_features=n_features)
    ngrams_matrix = vectorizer.fit_transform(df['review_text_translated'])
    ngrams_features = pd.DataFrame(ngrams_matrix.toarray(), columns=vectorizer.get_feature_names_out())
    return pd.concat([df, ngrams_features], axis=1)

# Function to apply LDA (Topic Modeling)
def apply_lda(df, num_topics=5):
    # Tokenize the text and create a dictionary
    reviews = df['review_text_translated'].apply(lambda x: x.split())
    dictionary = Dictionary(reviews)
    corpus = [dictionary.doc2bow(review) for review in reviews]
    
    # Fit LDA model
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)
    
    # Create topic distributions for each document
    def get_topics_for_review(review):
        bow = dictionary.doc2bow(review.split())
        topics = lda_model.get_document_topics(bow, minimum_probability=0.0)
        return [topic_prob[1] for topic_prob in topics]
    
    topic_distributions = df['review_text_translated'].apply(get_topics_for_review)
    topic_df = pd.DataFrame(topic_distributions.tolist(), columns=[f'topic_{i}' for i in range(num_topics)])
    
    # Assign meaningful names to the topics based on the most frequent words
    topic_keywords = []
    for idx, topic in lda_model.print_topics(num_topics=num_topics, num_words=5):
        # Extract the top 5 keywords from each topic
        words = [word.split('*')[1].replace('"', '').strip() for word in topic.split('+')]
        topic_keywords.append(words)
    
    # Create a dictionary to map topic index to a "meaningful name" based on keywords
    topic_names = []
    for idx, words in enumerate(topic_keywords):
        # For simplicity, let's assign the first dominant keyword as the topic name
        common_words = Counter(words)
        topic_names.append(f"topic_{idx}_{'_'.join(common_words.most_common(1)[0][0].split())}")
    
    # Rename the topic columns to meaningful names
    topic_df.columns = topic_names

    # Combine the original dataframe with the topic distributions dataframe
    return pd.concat([df, topic_df], axis=1)

# Function to apply Text Length and Readability
def apply_text_length_readability(df):
    df['review_length'] = df['review_text_translated'].apply(len)
    return df

# Wrapper function to select NLP techniques
def apply_nlp_techniques(df, techniques):
    if 'tfidf' in techniques:
        df = apply_tfidf(df)
    if 'w2v' in techniques:
        df = apply_word2vec_embeddings(df)
    if 'sentiment' in techniques:
        df = apply_sentiment_analysis(df)
    if 'ngrams' in techniques:
        df = apply_ngrams(df)
    if 'lda' in techniques:
        df = apply_lda(df)
    if 'length' in techniques:
        df = apply_text_length_readability(df)
    return df


def main():
    # Parse user input for NLP techniques
    args = parse_args()
    selected_techniques = args.techniques.split(',')

    # S3 bucket details
    s3_bucket = 'andorra-hotels-data-warehouse'
    input_prefix = 'l3_data/text/'
    output_prefix = 'model_training/nlp/'
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Get the Parquet file path from S3
    parquet_file_path = get_latest_parquet_file_path(s3_bucket, input_prefix)
    print(parquet_file_path)

    # Load dataset
    df = load_data(parquet_file_path)

    # Apply selected NLP techniques
    df_with_nlp = apply_nlp_techniques(df, selected_techniques)

    # Drop the review_text_translated column
    df_with_nlp.drop(columns=['review_text_translated'], inplace=True)

    # Save the new DataFrame with NLP features
    save_to_s3(df_with_nlp, s3_bucket, output_prefix, current_datetime)


if __name__ == "__main__":
    main()