import os
import requests
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResearchAssistant:
    def __init__(self, default_provider: str = "deepseek"):
        """
        Initialize the Research Assistant with a default AI provider
        
        Args:
            default_provider (str): Default AI provider to use ("deepseek", "openai", or "anthropic")
        """
        self.providers = {
            "deepseek": {
                "name": "DeepSeek",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "api_url": "https://api.deepseek.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                    "Content-Type": "application/json"
                }
            },
            "openai": {
                "name": "OpenAI",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "api_url": "https://api.openai.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                }
            },
            "anthropic": {
                "name": "Anthropic",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "api_url": "https://api.anthropic.com/v1/messages",
                "headers": {
                    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
            }
        }
        
        self.default_provider = default_provider
        self.available_providers = self._check_available_providers()
        
        if not self.available_providers:
            raise ValueError("No AI providers configured. Please check your API keys.")
    
    def _check_available_providers(self) -> List[str]:
        """Check which providers have valid API keys"""
        available = []
        for provider, config in self.providers.items():
            if config["api_key"] and config["api_key"] != "your_api_key_here":
                available.append(provider)
        return available
    
    def _call_deepseek(self, query: str) -> str:
        """Call the DeepSeek API with the given query"""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful research assistant. Provide detailed, accurate information with sources when possible."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.providers["deepseek"]["api_url"],
                headers=self.providers["deepseek"]["headers"],
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling DeepSeek API: {str(e)}"
    
    def _call_openai(self, query: str) -> str:
        """Call the OpenAI API with the given query"""
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful research assistant. Provide detailed, accurate information with sources when possible."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.providers["openai"]["api_url"],
                headers=self.providers["openai"]["headers"],
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    def _call_anthropic(self, query: str) -> str:
        """Call the Anthropic API with the given query"""
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "temperature": 0.7,
            "system": "You are a helpful research assistant. Provide detailed, accurate information with sources when possible.",
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        
        try:
            response = requests.post(
                self.providers["anthropic"]["api_url"],
                headers=self.providers["anthropic"]["headers"],
                json=payload
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except Exception as e:
            return f"Error calling Anthropic API: {str(e)}"
    
    def research(self, query: str, provider: Optional[str] = None) -> str:
        """
        Perform research on a given query using the specified AI provider
        
        Args:
            query (str): The research question or topic
            provider (str, optional): The AI provider to use. Defaults to the initialized default.
        
        Returns:
            str: The research response from the AI provider
        """
        if not provider:
            provider = self.default_provider
        
        if provider not in self.available_providers:
            return f"Provider '{provider}' is not available. Available providers: {', '.join(self.available_providers)}"
        
        print(f"Researching with {self.providers[provider]['name']}...")
        
        if provider == "deepseek":
            return self._call_deepseek(query)
        elif provider == "openai":
            return self._call_openai(query)
        elif provider == "anthropic":
            return self._call_anthropic(query)
        else:
            return f"Unknown provider: {provider}"
    
    def list_providers(self) -> List[str]:
        """List all available AI providers"""
        return self.available_providers

def main():
    """Main function to run the research assistant"""
    # Initialize the research assistant with DeepSeek as default
    assistant = ResearchAssistant(default_provider="deepseek")
    
    print("=" * 50)
    print("Personal Research Assistant")
    print("=" * 50)
    print(f"Available AI providers: {', '.join(assistant.list_providers())}")
    print("Type 'quit' to exit")
    print("Type 'switch' to change AI provider")
    print("=" * 50)
    
    current_provider = assistant.default_provider
    
    while True:
        query = input("\nWhat would you like to research? ")
        
        if query.lower() == 'quit':
            print("Goodbye!")
            break
        elif query.lower() == 'switch':
            print(f"Available providers: {', '.join(assistant.list_providers())}")
            new_provider = input("Which provider would you like to use? ").lower()
            if new_provider in assistant.list_providers():
                current_provider = new_provider
                print(f"Switched to {new_provider}")
            else:
                print(f"Provider '{new_provider}' not available.")
            continue
        
        # Perform research
        response = assistant.research(query, provider=current_provider)
        
        # Display results
        print("\n" + "=" * 50)
        print(f"Research Results ({assistant.providers[current_provider]['name']}):")
        print("=" * 50)
        print(response)
        print("=" * 50)

if __name__ == "__main__":
    main()