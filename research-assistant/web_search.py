import os
import requests
import serpapi
from googleapiclient.discovery import build
from typing import Dict, List, Optional

class WebSearchClient:
    def __init__(self):
        """Initialize web search clients with API keys from environment"""
        self.serpapi_enabled = bool(os.getenv("SERPAPI_API_KEY"))
        self.google_pse_enabled = bool(os.getenv("GOOGLE_PSE_ID") and os.getenv("GOOGLE_API_KEY"))
        
    def search(self, query: str, engine: str = "auto") -> List[Dict]:
        """
        Perform web search using the specified engine
        
        Args:
            query: The search query
            engine: The search engine to use ("serpapi", "google_pse", or "auto")
            
        Returns:
            List of search results
        """
        if engine == "auto":
            # Try SerpAPI first, then Google PSE
            if self.serpapi_enabled:
                results = self._search_serpapi(query)
                if results:
                    return results
            
            if self.google_pse_enabled:
                results = self._search_google_pse(query)
                if results:
                    return results
                    
            return []
        elif engine == "serpapi" and self.serpapi_enabled:
            return self._search_serpapi(query)
        elif engine == "google_pse" and self.google_pse_enabled:
            return self._search_google_pse(query)
        else:
            return []
    
    def _search_serpapi(self, query: str) -> List[Dict]:
        """Search using SerpAPI"""
        try:
            params = {
                "q": query,
                "api_key": os.getenv("SERPAPI_API_KEY"),
                "engine": "google",
                "num": 5
            }
            
            search = serpapi.search(params)
            results = []
            
            for result in search.get("organic_results", []):
                results.append({
                    "title": result.get("title"),
                    "link": result.get("link"),
                    "snippet": result.get("snippet"),
                    "source": "SerpAPI"
                })
            
            return results
        except Exception as e:
            print(f"SerpAPI search error: {str(e)}")
            return []
    
    def _search_google_pse(self, query: str) -> List[Dict]:
        """Search using Google Programmable Search Engine"""
        try:
            service = build(
                "customsearch", "v1",
                developerKey=os.getenv("GOOGLE_API_KEY")
            )
            
            result = service.cse().list(
                q=query,
                cx=os.getenv("GOOGLE_PSE_ID"),
                num=5
            ).execute()
            
            results = []
            for item in result.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "source": "Google PSE"
                })
            
            return results
        except Exception as e:
            print(f"Google PSE search error: {str(e)}")
            return []
    
    def is_available(self) -> bool:
        """Check if any web search is available"""
        return self.serpapi_enabled or self.google_pse_enabled