"""
Utility functions for MIST jailbreak optimizer
"""

import nltk
import random
from nltk.corpus import wordnet as wn

# Download necessary NLTK resources
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')
    nltk.download('wordnet')

def tokenize_and_tag(text):
    """
    Tokenize text and tag parts of speech
    
    Args:
        text: Input text
        
    Returns:
        List of (word, pos_tag) tuples
    """
    try:
        # Tokenize
        tokens = nltk.word_tokenize(text)
        # Tag parts of speech
        tagged = nltk.pos_tag(tokens)
        return tagged
    except Exception as e:
        print(f"Error tokenizing and tagging: {e}")
        # Return a simple fallback
        return [(word, 'NN') for word in text.split()]

def is_replaceable(word, pos):
    """
    Check if a word is replaceable based on its part of speech
    
    Args:
        word: Word to check
        pos: Part of speech tag
        
    Returns:
        Boolean indicating if word is replaceable
    """
    # Skip very short words
    if len(word) <= 3:
        return False
        
    # Skip special tokens and punctuation
    if not word.isalpha():
        return False
        
    # Replaceable parts of speech: nouns, verbs, adjectives, adverbs
    replaceable_pos = ['NN', 'NNS', 'NNP', 'NNPS',  # nouns
                       'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # verbs
                       'JJ', 'JJR', 'JJS',  # adjectives
                       'RB', 'RBR', 'RBS']  # adverbs
                       
    return pos in replaceable_pos

def get_wordnet_pos(treebank_tag):
    """
    Convert Penn Treebank POS tags to WordNet POS tags
    
    Args:
        treebank_tag: Penn Treebank POS tag
        
    Returns:
        WordNet POS tag or None
    """
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('N'):
        return wn.NOUN
    elif treebank_tag.startswith('R'):
        return wn.ADV
    else:
        return None

def get_synonym_set(word, pos=None, max_synonyms=10):
    """
    Get set of synonyms for a word
    
    Args:
        word: Input word
        pos: Part of speech tag (optional)
        max_synonyms: Maximum number of synonyms to return
        
    Returns:
        List of synonyms
    """
    synonyms = set()
    
    try:
        # Convert to WordNet POS tag if provided
        wordnet_pos = get_wordnet_pos(pos) if pos else None
        
        # Get synsets
        if wordnet_pos:
            synsets = wn.synsets(word, pos=wordnet_pos)
        else:
            synsets = wn.synsets(word)
            
        # Get lemma names (synonyms)
        for synset in synsets:
            for lemma in synset.lemmas():
                synonym = lemma.name().replace('_', ' ')
                # Only add if different from original word
                if synonym.lower() != word.lower():
                    synonyms.add(synonym)
                    
        # Limit number of synonyms
        synonyms_list = list(synonyms)
        if len(synonyms_list) > max_synonyms:
            synonyms_list = random.sample(synonyms_list, max_synonyms)
            
        return synonyms_list
    except Exception as e:
        print(f"Error getting synonyms: {e}")
        return [] 