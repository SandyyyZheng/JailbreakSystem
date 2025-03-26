import os
import openai
from anthropic import Anthropic

class LLMService:
    def __init__(self):
        # Initialize API keys from environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Initialize clients
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        if self.anthropic_api_key:
            self.anthropic = Anthropic(api_key=self.anthropic_api_key)
    
    async def call_openai(self, prompt, model="gpt-4"):
        """
        Call OpenAI API
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise
    
    async def call_anthropic(self, prompt, model="claude-3-opus-20240229"):
        """
        Call Anthropic API
        """
        try:
            response = await self.anthropic.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            raise
    
    async def get_response(self, prompt, provider="openai", model=None):
        """
        Get response from specified LLM provider
        """
        if provider == "openai":
            return await self.call_openai(prompt, model or "gpt-4")
        elif provider == "anthropic":
            return await self.call_anthropic(prompt, model or "claude-3-opus-20240229")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

# Create a singleton instance
llm_service = LLMService() 