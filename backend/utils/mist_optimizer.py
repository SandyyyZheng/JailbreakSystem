"""
MIST Optimization Algorithm for Jailbreak Prompts
A simplified version focused on optimizing prompts with semantic similarity as the primary stopping criterion.
"""

import random
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
# 移除对llm_api的导入
# from .llm_api import test_jailbreak, call_llm_api
from .embedding import SentenceEmbedding
from .utils import tokenize_and_tag, is_replaceable, get_synonym_set

class MISTOptimizer:
    """
    MIST Optimizer
    
    This class implements an optimizer that modifies prompts by replacing words
    with their synonyms to maintain semantic meaning while evading filters.
    """
    
    def __init__(self, similarity_threshold=0.90, max_queries=50, model_name="gpt-4o-mini"):
        """
        Initialize the MIST optimizer
        
        Args:
            similarity_threshold (float): Minimum semantic similarity threshold
            max_queries (int): Maximum number of queries to make
            model_name (str): The model to use for testing jailbreak success
        """
        self.similarity_threshold = similarity_threshold
        self.max_queries = max_queries
        self.model_name = model_name
        
        # Initialize sentence transformer model for semantic similarity
        print("Loading sentence transformer model...")
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully")
    
    def compute_similarity(self, text1, text2):
        """Calculate semantic similarity between two texts using cosine similarity"""
        # Encode texts to vectors
        embedding1 = self.sentence_transformer.encode(text1, convert_to_tensor=True)
        embedding2 = self.sentence_transformer.encode(text2, convert_to_tensor=True)
        
        # Convert to numpy if they are tensors
        if hasattr(embedding1, 'cpu'):
            embedding1 = embedding1.cpu().numpy()
        if hasattr(embedding2, 'cpu'):
            embedding2 = embedding2.cpu().numpy()
        
        # Reshape if needed
        if len(embedding1.shape) == 1:
            embedding1 = embedding1.reshape(1, -1)
        if len(embedding2.shape) == 1:
            embedding2 = embedding2.reshape(1, -1)
        
        # Compute cosine similarity
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        return similarity
    
    def test_jailbreak_success(self, prompt):
        """
        模拟test jailbreak，不调用实际的LLM API
        仅返回一个占位响应和随机成功状态
        
        Args:
            prompt: 测试提示
            
        Returns:
            Tuple of (jailbreak_success, response_text)
        """
        # 简单地返回一个模拟响应
        mock_response = "This is a simulated response for MIST optimization."
        # 不使用success作为优化条件，所以随机返回即可
        mock_success = True  
        return mock_success, mock_response
    
    def optimize_jailbreak_prompt(self, original_prompt):
        """
        Main optimization function for jailbreak prompts.
        
        Args:
            original_prompt: Original jailbreak prompt
            
        Returns:
            Optimized jailbreak prompt and metadata
        """
        # Reset query count
        self.query_count = 0
        
        # Initialize adversarial prompt
        print("Initializing adversarial prompt...")
        initial_tokens = self.initialize_adversarial_prompt(original_prompt)
        initial_prompt = ' '.join(initial_tokens)
        
        # Get initial similarity
        initial_similarity = self.compute_similarity(original_prompt, initial_prompt)
        print(f"Initial similarity: {initial_similarity:.4f}")
        
        # 检查初始相似度，如果未达到阈值则增加查询计数
        if initial_similarity < self.similarity_threshold:
            self.query_count += 1
            print(f"Initial attempt, similarity: {initial_similarity:.4f}, query count: {self.query_count}")
        
        # 模拟响应（仅用于返回结果）
        mock_response = "This is a simulated response for MIST optimization."
        
        # If initial similarity is already above threshold, return early
        if initial_similarity >= self.similarity_threshold:
            print(f"Initial similarity already meets threshold: {initial_similarity:.4f}")
            return {
                'original_prompt': original_prompt,
                'optimized_prompt': initial_prompt,
                'similarity': initial_similarity,
                'query_count': self.query_count,
                'response': mock_response
            }
        
        print("Starting optimization...")
        
        # Phase 1: Substitute original words back
        print("Phase 1: Substituting original words back...")
        phase1_tokens = self.substitute_original_words_back(initial_tokens, original_prompt)
        phase1_prompt = ' '.join(phase1_tokens)
        
        # Get Phase 1 similarity
        phase1_similarity = self.compute_similarity(original_prompt, phase1_prompt)
        print(f"Similarity after Phase 1: {phase1_similarity:.4f}")
        
        # Check if we've already reached the similarity threshold
        if phase1_similarity >= self.similarity_threshold:
            return {
                'original_prompt': original_prompt,
                'optimized_prompt': phase1_prompt,
                'similarity': phase1_similarity,
                'query_count': self.query_count,
                'response': mock_response
            }
        
        # Phase 2: Optimize remaining words
        print("Phase 2: Optimizing remaining substituted words...")
        final_tokens = self.optimize_remaining_words(phase1_tokens, original_prompt)
        final_prompt = ' '.join(final_tokens)
        
        # Get final similarity
        final_similarity = self.compute_similarity(original_prompt, final_prompt)
        print(f"Final similarity: {final_similarity:.4f}")
        
        # 检查最终相似度，如果仍未达到阈值则增加最后一次查询计数
        if final_similarity < self.similarity_threshold:
            self.query_count += 1
            print(f"Final attempt, similarity: {final_similarity:.4f}, query count: {self.query_count}")
        
        # Return final result
        return {
            'original_prompt': original_prompt,
            'optimized_prompt': final_prompt,
            'similarity': final_similarity,
            'query_count': self.query_count,
            'response': mock_response
        }
    
    def create_variation(self, prompt):
        """Create a variation of the prompt by replacing words with synonyms"""
        # Tokenize and tag parts of speech
        tagged_words = tokenize_and_tag(prompt)
        
        # Make a copy of the tagged words
        new_tagged_words = tagged_words.copy()
        
        # Choose a random number of words to replace (between 1 and 20% of replaceable words)
        replaceable_words = [(i, word, pos) for i, (word, pos) in enumerate(tagged_words) if is_replaceable(word, pos)]
        if not replaceable_words:
            return prompt
            
        num_to_replace = max(1, min(int(len(replaceable_words) * 0.2), 5))
        words_to_replace = random.sample(replaceable_words, min(num_to_replace, len(replaceable_words)))
        
        # Replace selected words with synonyms
        for idx, word, pos in words_to_replace:
            synonyms = get_synonym_set(word, pos)
            if synonyms:
                # Choose a random synonym
                new_word = random.choice(list(synonyms))
                new_tagged_words[idx] = (new_word, pos)
        
        # Reconstruct the prompt
        new_prompt = ' '.join([word for word, _ in new_tagged_words])
        
        # Fix spacing around punctuation
        new_prompt = new_prompt.replace(' .', '.').replace(' ,', ',').replace(' !', '!').replace(' ?', '?')
        new_prompt = new_prompt.replace(' ;', ';').replace(' :', ':').replace(' )', ')').replace('( ', '(')
        
        return new_prompt
    
    def _get_replacement_word(self, word, pos):
        """
        Get replacement word using synonyms
        
        Args:
            word: Original word
            pos: Part-of-speech tag
            
        Returns:
            Replacement word
        """
        # Get synonyms for the word
        synonyms = get_synonym_set(word, pos)
        
        # If synonyms available, randomly choose one
        if synonyms:
            return random.choice(synonyms)
            
        # If no synonyms, return the original word
        return word
    
    def initialize_adversarial_prompt(self, original_prompt):
        """
        Generate an initial adversarial jailbreak prompt by randomly replacing words.
        
        Args:
            original_prompt: Original jailbreak prompt
            
        Returns:
            Initial adversarial prompt as a list of tokens
        """
        tagged_words = tokenize_and_tag(original_prompt)
        initial_prompt = []
        
        # Keep track of replacements for later optimization
        self.replaced_words = {}
        
        for i, (word, pos) in enumerate(tagged_words):
            if is_replaceable(word, pos):
                replacement = self._get_replacement_word(word, pos)
                # Only add to replaced_words if actually replaced
                if replacement != word:
                    initial_prompt.append(replacement)
                    self.replaced_words[len(initial_prompt)-1] = {
                        'original': word,
                        'replacement': replacement,
                        'pos': pos,
                        'synonyms': get_synonym_set(word, pos) or [word]  # Ensure non-empty synonym list
                    }
                else:
                    initial_prompt.append(word)
            else:
                initial_prompt.append(word)
                
        # Check similarity
        initial_similarity = self.compute_similarity(original_prompt, ' '.join(initial_prompt))
        
        # If similarity is already above threshold, return the original prompt
        if initial_similarity >= self.similarity_threshold:
            return original_prompt.split()
            
        return initial_prompt
    
    def query_target_model(self, prompt):
        """
        模拟查询目标模型，不调用实际API
        
        Args:
            prompt: 要测试的提示
            
        Returns:
            Tuple of (jailbreak_success, response_text)
        """
        # 返回模拟响应
        mock_response = "This is a simulated response for MIST optimization."
        # 始终返回成功，因为我们不使用success作为条件
        mock_success = True
        return mock_success, mock_response
    
    def substitute_original_words_back(self, adv_prompt_tokens, original_prompt):
        """
        Phase 1: Substitute original words back to improve similarity.
        
        Args:
            adv_prompt_tokens: Current adversarial prompt tokens
            original_prompt: Original prompt for similarity comparison
            
        Returns:
            Optimized tokens after substitution phase
        """
        optimized_tokens = adv_prompt_tokens.copy()
        
        # Sort replaced words by index for systematic processing
        sorted_indices = sorted(self.replaced_words.keys())
        
        for i, idx in enumerate(sorted_indices):
            # Skip if already substituted back or index out of range
            if idx >= len(optimized_tokens) or optimized_tokens[idx] == self.replaced_words[idx]['original']:
                continue
                
            # Create a candidate prompt with original word substituted back
            candidate_tokens = optimized_tokens.copy()
            candidate_tokens[idx] = self.replaced_words[idx]['original']
            candidate_prompt = ' '.join(candidate_tokens)
            
            # Calculate similarity to original prompt
            similarity = self.compute_similarity(original_prompt, candidate_prompt)
            
            # 增加查询计数，每次迭代（未达到阈值）都算作一次查询
            if similarity < self.similarity_threshold:
                self.query_count += 1
                print(f"Substitution {i+1}, similarity: {similarity:.4f}, query count: {self.query_count}")
            
            # Simply keep the substitution, regardless of jailbreak success
            optimized_tokens = candidate_tokens
            # Remove from replaced_words tracking since we've reverted it
            self.replaced_words.pop(idx)
            
            # Check if we've reached the similarity threshold
            if similarity >= self.similarity_threshold:
                return optimized_tokens
                
        return optimized_tokens
    
    def optimize_remaining_words(self, adv_prompt_tokens, original_prompt, max_iterations=20):
        """
        Phase 2: Optimize remaining substituted words using synonym sets and direction estimation.
        
        Args:
            adv_prompt_tokens: Current adversarial prompt tokens
            original_prompt: Original prompt for similarity comparison
            max_iterations: Maximum optimization iterations
            
        Returns:
            Final optimized tokens
        """
        optimized_tokens = adv_prompt_tokens.copy()
        
        # Remaining indices of replaced words
        remaining_indices = list(self.replaced_words.keys())
        
        if not remaining_indices:
            return optimized_tokens
            
        # Calculate word vector distances to determine optimization order
        distances = {}
        for idx in remaining_indices:
            if idx >= len(optimized_tokens):
                continue
                
            original_word = self.replaced_words[idx]['original']
            current_word = optimized_tokens[idx]
            
            # Calculate cosine distance (1 - cosine similarity)
            original_emb = self.sentence_transformer.encode(original_word, convert_to_tensor=True)
            current_emb = self.sentence_transformer.encode(current_word, convert_to_tensor=True)
            
            if original_emb is not None and current_emb is not None:
                distance = 1 - cosine_similarity(original_emb, current_emb)[0][0]
                distances[idx] = distance
            
        for iteration in range(max_iterations):
            # Check if we've reached the similarity threshold
            current_prompt = ' '.join(optimized_tokens)
            similarity = self.compute_similarity(original_prompt, current_prompt)
            
            # 增加查询计数，每次迭代（未达到阈值）都算作一次查询
            if similarity < self.similarity_threshold:
                self.query_count += 1
                print(f"Iteration {iteration+1}, similarity: {similarity:.4f}, query count: {self.query_count}")
            
            if similarity >= self.similarity_threshold:
                return optimized_tokens
                
            if not remaining_indices:
                break
                
            # Sample index based on probability (higher probability for words with smaller distance)
            valid_indices = [idx for idx in remaining_indices if idx in distances]
            
            if not valid_indices:
                break
                
            # Normalize distances to probabilities (lower distance = higher probability)
            probs = [max(0.01, 1 - distances.get(idx, 0.5)) for idx in valid_indices]
            probs_sum = sum(probs)
            probs = [p / probs_sum for p in probs]
            
            # Sample word index to optimize
            target_idx = np.random.choice(valid_indices, p=probs)
            
            # Current word info
            current_word = optimized_tokens[target_idx]
            original_word = self.replaced_words[target_idx]['original']
            synonyms = self.replaced_words[target_idx]['synonyms']
            
            # Try each synonym and select the one that maximizes similarity to original prompt
            best_synonym = None
            best_similarity = -1
            
            for word in synonyms:
                candidate_tokens = optimized_tokens.copy()
                candidate_tokens[target_idx] = word
                candidate_prompt = ' '.join(candidate_tokens)
                
                # Calculate similarity to original prompt
                sim = self.compute_similarity(original_prompt, candidate_prompt)
                if sim > best_similarity:
                    best_similarity = sim
                    best_synonym = word
            
            if best_synonym:
                # Apply the update
                optimized_tokens[target_idx] = best_synonym
                
                # Check if we've reached the similarity threshold
                if best_similarity >= self.similarity_threshold:
                    return optimized_tokens
            
            # Remove from optimization list regardless of outcome
            remaining_indices.remove(target_idx)
            
        return optimized_tokens 