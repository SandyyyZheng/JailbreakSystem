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


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI API"""
    
    env_var_name = "OPENAI_API_KEY"
    
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        super().__init__(api_key)
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
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
            print(f"Error calling OpenAI API: {e}")
            return f"Error: {str(e)}"


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic API"""
    
    env_var_name = "ANTHROPIC_API_KEY"
    
    def __init__(self, api_key=None, model="claude-2"):
        super().__init__(api_key)
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/complete"
    
    def generate_response(self, prompt, max_tokens=100, temperature=0.7):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        data = {
            "model": self.model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()["completion"]
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return f"Error: {str(e)}"


# Factory function to get the appropriate provider
def get_llm_provider(provider_name="openai", api_key=None, model=None):
    if provider_name.lower() == "openai":
        return OpenAIProvider(api_key=api_key, model=model or "gpt-3.5-turbo")
    elif provider_name.lower() == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model or "claude-2")
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


# Function to test a jailbreak prompt against an LLM
def test_jailbreak(jailbreak_prompt, provider_name="openai", api_key=None, model=None, max_tokens=200):
    """
    Test a jailbreak prompt against an LLM and return the response
    """
    try:
        provider = get_llm_provider(provider_name, api_key, model)
        response = provider.generate_response(jailbreak_prompt, max_tokens=max_tokens)
        return response
    except Exception as e:
        print(f"Error testing jailbreak: {e}")
        return f"Error: {str(e)}" 