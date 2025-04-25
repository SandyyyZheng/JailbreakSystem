import requests
import json
import os
from flask import current_app

# This is a placeholder for your actual LLM API integration
# You'll need to replace this with your actual API keys and endpoints

class LLMProvider:
    """Base class for LLM API providers"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get(self.env_var_name)
        if not self.api_key:
            raise ValueError(f"API key not provided and {self.env_var_name} environment variable not set")
    
    def generate_response(self, prompt, max_tokens=100, temperature=0.7):
        """Generate a response from the LLM"""
        raise NotImplementedError("Subclasses must implement this method")


class DeepBricksProvider(LLMProvider):
    """Provider for DeepBricks API which supports multiple models"""
    
    env_var_name = "LLM_API_KEY"
    
    def __init__(self, api_key=None, model="gpt-4o-mini"):
        super().__init__(api_key)
        self.model = model
        self.api_url = os.environ.get("LLM_API_URL", "https://api.deepbricks.ai/v1/chat/completions")
    
    def generate_response(self, prompt, max_tokens=100, temperature=0.7):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling DeepBricks API: {e}")
            return f"Error: {str(e)}"


# Get available models for DeepBricks
def get_available_models():
    """
    Return a list of available models for the user interface
    """
    return [
        "gpt-4o-mini", 
        "gpt-4o-2024-08-06", 
        "gpt-4-turbo", 
        "claude-3.5-sonnet"
    ]


# Function to test a jailbreak prompt against an LLM
def test_jailbreak(jailbreak_prompt, model=None, max_tokens=200, temperature=0.7):
    """
    Test a jailbreak prompt against an LLM and return the response
    
    Args:
        jailbreak_prompt (str): The jailbreak prompt to test
        model (str): The model to use (default uses the environment variable)
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Temperature for generation (higher = more random)
        
    Returns:
        str: The model's response
    """
    try:
        # Use the model from parameters or default to environment variable
        model_to_use = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")
        api_key = os.environ.get("LLM_API_KEY")
        
        provider = DeepBricksProvider(api_key=api_key, model=model_to_use)
        response = provider.generate_response(
            jailbreak_prompt, 
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response
    except Exception as e:
        print(f"Error testing jailbreak: {e}")
        return f"Error: {str(e)}" 