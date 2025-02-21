import os
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
import re
from dotenv import load_dotenv

# Load environment variables from the project's .env file
load_dotenv()

class WebResearchAgent:
    def __init__(self, max_sources: int = 3):
        """
        Initialize Web Research Agent with configurable parameters
        
        Args:
            max_sources (int): Maximum number of sources to retrieve
        """
        self.max_sources = max_sources
        
        # Try multiple possible key names
        serpapi_key_options = [
            os.getenv('SERPAPI_API_KEY'),
            os.getenv('SERP_API_KEY'),
            os.getenv('SERPAPI_KEY')
        ]
        
        self.serpapi_key = next((key for key in serpapi_key_options if key), None)
        
        if not self.serpapi_key:
            print("⚠️ Warning: No SerpAPI key found. Web searches will be limited.")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
    
    def web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search using SerpAPI
        
        Args:
            query (str): Search query
        
        Returns:
            List of web search results
        """
        if not self.serpapi_key:
            print("❌ Cannot perform web search: No API key available")
            return []
        
        try:
            params = {
                'engine': 'google',
                'q': query,
                'api_key': self.serpapi_key,
                'num': self.max_sources
            }
            
            response = requests.get('https://serpapi.com/search', params=params)
            
            if response.status_code == 200:
                results_data = response.json()
                organic_results = results_data.get('organic_results', [])
                
                return [
                    {
                        "title": result.get('title', 'No Title'),
                        "link": result.get('link', ''),
                        "snippet": result.get('snippet', 'No description')
                    } for result in organic_results[:self.max_sources]
                ]
            
            print(f"Web search failed: {response.status_code}")
            return []
        
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def scientific_paper_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for scientific papers using arXiv public API
        
        Args:
            query (str): Search query
        
        Returns:
            List of scientific paper results
        """
        try:
            base_url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": query,
                "start": 0,
                "max_results": self.max_sources
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                results = []
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:self.max_sources]:
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text
                    summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                    link = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]')
                    
                    results.append({
                        "title": title,
                        "link": link.get('href') if link is not None else '',
                        "summary": summary[:200] + '...' if summary else 'No summary'
                    })
                
                return results
            return []
        
        except Exception as e:
            print(f"Scientific paper search error: {e}")
            return []
    
    def research_hypothesis(self, hypothesis: str) -> Dict[str, Any]:
        """
        Comprehensive research for a given hypothesis
        
        Args:
            hypothesis (str): Scientific hypothesis to research
        
        Returns:
            Comprehensive research findings
        """
        web_results = self.web_search(hypothesis)
        scientific_papers = self.scientific_paper_search(hypothesis)
        
        return {
            "hypothesis": hypothesis,
            "web_results": web_results,
            "scientific_papers": scientific_papers
        }

def research_hypothesis(hypothesis: str) -> Dict[str, Any]:
    """
    Standalone function for easy integration with existing agents
    
    Args:
        hypothesis (str): Scientific hypothesis to research
    
    Returns:
        Research findings
    """
    agent = WebResearchAgent()
    return agent.research_hypothesis(hypothesis)

# Example usage
if __name__ == "__main__":
    test_hypothesis = "Quantum entanglement in biological systems"
    results = research_hypothesis(test_hypothesis)
    print(json.dumps(results, indent=2))
