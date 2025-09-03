import os
import requests
import google.generativeai as genai
from huggingface_hub import InferenceClient
from typing import Dict, Any, Optional

class AIClient:
    def __init__(self):
        """Initialize all AI providers with API keys from environment"""
        self.providers = self._initialize_providers()
        
    def _initialize_providers(self) -> Dict[str, Dict]:
        """Initialize all AI providers with their configurations"""
        providers = {
            "deepseek": {
                "name": "DeepSeek",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "api_url": "https://api.deepseek.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                    "Content-Type": "application/json"
                },
                "enabled": bool(os.getenv("DEEPSEEK_API_KEY"))
            },
            "openai": {
                "name": "OpenAI",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "api_url": "https://api.openai.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                },
                "enabled": bool(os.getenv("OPENAI_API_KEY"))
            },
            "anthropic": {
                "name": "Anthropic",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "api_url": "https://api.anthropic.com/v1/messages",
                "headers": {
                    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                "enabled": bool(os.getenv("ANTHROPIC_API_KEY"))
            },
            "gemini": {
                "name": "Google Gemini",
                "api_key": os.getenv("GEMINI_API_KEY"),
                "enabled": bool(os.getenv("GEMINI_API_KEY"))
            },
            "huggingface": {
                "name": "Hugging Face",
                "api_key": os.getenv("HUGGINGFACE_API_KEY"),
                "api_url": "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
                "enabled": bool(os.getenv("HUGGINGFACE_API_KEY"))
            }
        }
        
        # Configure Gemini if enabled
        if providers["gemini"]["enabled"]:
            genai.configure(api_key=providers["gemini"]["api_key"])
            
        return providers
    
    def get_available_providers(self) -> list:
        """Return list of available AI providers"""
        return [name for name, config in self.providers.items() if config["enabled"]]
    
    def query(self, provider: str, query: str, context: str = "") -> str:
        """
        Query a specific AI provider
        
        Args:
            provider: The AI provider to use
            query: The user's query
            context: Previous conversation context
            
        Returns:
            The AI response
        """
        if provider not in self.get_available_providers():
            return f"Provider '{provider}' is not available."
        
        if provider == "deepseek":
            return self._query_deepseek(query, context)
        elif provider == "openai":
            return self._query_openai(query, context)
        elif provider == "anthropic":
            return self._query_anthropic(query, context)
        elif provider == "gemini":
            return self._query_gemini(query, context)
        elif provider == "huggingface":
            return self._query_huggingface(query, context)
        else:
            return f"Unknown provider: {provider}"
    
    def _query_deepseek(self, query: str, context: str) -> str:
        """Query DeepSeek API"""
        messages = [
            {"role": "system", "content": "You are a helpful research assistant. Provide detailed, accurate information with sources when possible."},
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Context from previous conversation: {context}"})
            
        messages.append({"role": "user", "content": query})
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.providers["deepseek"]["api_url"],
                headers=self.providers["deepseek"]["headers"],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling DeepSeek API: {str(e)}"
    
    def _query_openai(self, query: str, context: str) -> str:
        """Query OpenAI API"""
        messages = [
            {"role": "system", "content": "You are a helpful research assistant. Provide detailed, accurate information with sources when possible."},
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Context from previous conversation: {context}"})
            
        messages.append({"role": "user", "content": query})
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.providers["openai"]["api_url"],
                headers=self.providers["openai"]["headers"],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    def _query_anthropic(self, query: str, context: str) -> str:
        """Query Anthropic API"""
        system_message = "You are a helpful research assistant. Provide detailed, accurate information with sources when possible."
        if context:
            system_message += f"\n\nContext from previous conversation: {context}"
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "temperature": 0.7,
            "system": system_message,
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        
        try:
            response = requests.post(
                self.providers["anthropic"]["api_url"],
                headers=self.providers["anthropic"]["headers"],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except Exception as e:
            return f"Error calling Anthropic API: {str(e)}"
    
    def _query_gemini(self, query: str, context: str) -> str:
        """Query Google Gemini API"""
        try:

              
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = "You are a helpful research assistant. Provide detailed, accurate information with sources when possible."
            if context:
                prompt += f"\n\nContext from previous conversation: {context}"
                
            prompt += f"\n\nUser query: {query}"
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    def _query_huggingface(self, query: str, context: str) -> str:
        """Query Hugging Face API"""
        try:
            client = InferenceClient(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                token=self.providers["huggingface"]["api_key"]
            )
            
            prompt = "<s>[INST] You are a helpful research assistant. Provide detailed, accurate information with sources when possible."
            if context:
                prompt += f"\n\nContext from previous conversation: {context}"
                
            prompt += f"\n\nUser query: {query} [/INST]"
            
            response = client.text_generation(
                prompt,
                max_new_tokens=2000,
                temperature=0.7
            )
            
            return response
        except Exception as e:
            return f"Error calling Hugging Face API: {str(e)}"