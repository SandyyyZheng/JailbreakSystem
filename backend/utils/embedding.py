"""
Embedding utilities for semantic similarity computation
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class SentenceEmbedding:
    """
    Wrapper for sentence-transformers models to compute embeddings and similarities
    """
    
    def __init__(self, model_name="all-mpnet-base-v2"):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence-transformers model
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.word_cache = {}  # Cache for word embeddings
            self.sentence_cache = {}  # Cache for sentence embeddings
        except Exception as e:
            print(f"Warning: Failed to load embedding model: {e}")
            print("Falling back to random embeddings for demonstration")
            self.model = None
    
    def get_embeddings(self, text):
        """
        Get embeddings for a text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        # Check cache first
        if text in self.sentence_cache:
            return self.sentence_cache[text]
            
        try:
            if self.model:
                embedding = self.model.encode(text, convert_to_numpy=True)
                embedding = embedding / np.linalg.norm(embedding)  # Normalize
                self.sentence_cache[text] = embedding
                return embedding
            else:
                # Fallback to random embeddings for demonstration
                embedding = np.random.rand(768)
                embedding = embedding / np.linalg.norm(embedding)  # Normalize
                self.sentence_cache[text] = embedding
                return embedding
        except Exception as e:
            print(f"Error computing embeddings: {e}")
            # Return random fallback
            embedding = np.random.rand(768)
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
    
    def get_single_embedding(self, word):
        """
        Get embedding for a single word
        
        Args:
            word: Input word
            
        Returns:
            Embedding vector
        """
        # Check cache first
        if word in self.word_cache:
            return self.word_cache[word]
            
        try:
            if self.model:
                embedding = self.model.encode(word, convert_to_numpy=True)
                embedding = embedding / np.linalg.norm(embedding)  # Normalize
                self.word_cache[word] = embedding
                return embedding
            else:
                # Fallback to random embeddings
                embedding = np.random.rand(768)
                embedding = embedding / np.linalg.norm(embedding)
                self.word_cache[word] = embedding
                return embedding
        except Exception as e:
            print(f"Error computing word embedding: {e}")
            return None
    
    def compute_similarity(self, text1, text2):
        """
        Compute semantic similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        embedding1 = self.get_embeddings(text1)
        embedding2 = self.get_embeddings(text2)
        
        # Reshape for sklearn's cosine_similarity
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        # Ensure result is between 0 and 1
        return max(0, min(1, similarity)) 