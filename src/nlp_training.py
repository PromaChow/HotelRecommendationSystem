###############################################################
#                       NOT OPTIMIZED YET
###############################################################

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import torch
from transformers import BertTokenizer, BertModel
from sklearn.decomposition import TruncatedSVD
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models.ldamodel import LdaModel
from gensim.corpora import Dictionary

# Load dataset
df = pd.read_parquet('path_to_l3_data')

# Function to apply TF-IDF
def apply_tfidf(df, n_features=100):
    tfidf_vectorizer = TfidfVectorizer(max_features=n_features)
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['review_text_translated'])
    tfidf_features = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())
    return pd.concat([df, tfidf_features], axis=1)

# Function to apply Word Embeddings with BERT
def apply_bert_embeddings(df, n_components=10):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    
    def get_bert_embedding(text):
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    embeddings = df['review_text_translated'].apply(get_bert_embedding)
    embeddings_df = pd.DataFrame(embeddings.tolist())
    
    # Dimensionality reduction
    pca = PCA(n_components=n_components)
    reduced_embeddings = pca.fit_transform(embeddings_df)
    reduced_df = pd.DataFrame(reduced_embeddings, columns=[f'bert_{i}' for i in range(n_components)])
    return pd.concat([df, reduced_df], axis=1)

# Function to apply Sentiment Analysis
def apply_sentiment_analysis(df):
    df['sentiment_polarity'] = df['review_text_translated'].apply(lambda text: TextBlob(text).sentiment.polarity)
    return df

# Function to apply N-grams (Bigrams example)
def apply_ngrams(df, n_features=100):
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
    
    return pd.concat([df, topic_df], axis=1)

# Function to apply Text Length and Readability
def apply_text_length_readability(df):
    df['review_length'] = df['review_text_translated'].apply(len)
    return df

# Wrapper function to select NLP techniques
def apply_nlp_techniques(df, techniques):
    if 'tfidf' in techniques:
        df = apply_tfidf(df)
    if 'bert' in techniques:
        df = apply_bert_embeddings(df)
    if 'sentiment' in techniques:
        df = apply_sentiment_analysis(df)
    if 'ngrams' in techniques:
        df = apply_ngrams(df)
    if 'lda' in techniques:
        df = apply_lda(df)
    if 'length' in techniques:
        df = apply_text_length_readability(df)
    return df

# Example usage: Apply selected NLP techniques
selected_techniques = ['tfidf', 'sentiment', 'lda']
df_with_nlp = apply_nlp_techniques(df, selected_techniques)

# Save the new DataFrame with NLP features
df_with_nlp.to_parquet('path_to_save_transformed_data.parquet')