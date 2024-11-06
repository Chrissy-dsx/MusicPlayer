import jieba
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(text1, text2):
    # initialize bag of words model
    vectorizer = CountVectorizer()

    # calculate bag of words representation of input text
    X = vectorizer.fit_transform([text1, text2])

    # calculate cosine similarity
    similarity = cosine_similarity(X[0], X[1])
    return similarity[0][0]