import os
import sys
import json
from dotenv import load_dotenv

# Ensure the project root is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_research_agent import WebResearchAgent

def test_serpapi_connection():
    """
    Comprehensive test of web research agent functionality
    """
    print("🔍 Starting Web Research Agent Test")
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"🔍 Attempting to load .env from: {env_path}")
    
    # Try explicit loading
    load_dotenv(env_path)
    
    # Print all environment variables for debugging
    print("\n🔍 Current Environment Variables:")
    for key, value in os.environ.items():
        if 'SERPAPI' in key:
            print(f"{key}: {value}")
    
    # Explicit environment variable retrieval
    print("\n🔍 Explicit Environment Variable Retrieval:")
    print(f"os.getenv('SERPAPI_API_KEY'): {os.getenv('SERPAPI_API_KEY')}")
    print(f"os.getenv('SERP_API_KEY'): {os.getenv('SERP_API_KEY')}")
    print(f"os.getenv('SERPAPI_KEY'): {os.getenv('SERPAPI_KEY')}")
    
    # Check SerpAPI Key
    serpapi_key_options = [
        os.getenv('SERPAPI_API_KEY'),
        os.getenv('SERP_API_KEY'),
        os.getenv('SERPAPI_KEY')
    ]
    serpapi_key = next((key for key in serpapi_key_options if key), None)
    
    if not serpapi_key:
        print("❌ ERROR: No SerpAPI key found in environment variables")
        return False
    
    print(f"✅ SerpAPI Key detected: {serpapi_key[:5]}...{serpapi_key[-5:]}")
    
    # Initialize Web Research Agent
    agent = WebResearchAgent(max_sources=3)
    
    # Test Web Search
    test_queries = [
        "Quantum entanglement in biological systems",
        "Latest developments in AI research",
        "Climate change mitigation strategies"
    ]
    
    for query in test_queries:
        print(f"\n🔬 Testing web search for query: '{query}'")
        try:
            results = agent.web_search(query)
            
            if not results:
                print(f"❌ No results found for query: {query}")
                continue
            
            print(f"✅ Found {len(results)} web search results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     Link: {result['link']}")
                print(f"     Snippet: {result['snippet'][:100]}...")
        
        except Exception as e:
            print(f"❌ Error in web search: {e}")
            return False
    
    # Test Scientific Paper Search
    print("\n🔬 Testing scientific paper search")
    try:
        papers = agent.scientific_paper_search("Quantum Computing")
        
        if not papers:
            print("❌ No scientific papers found")
            return False
        
        print(f"✅ Found {len(papers)} scientific papers:")
        for i, paper in enumerate(papers, 1):
            print(f"  {i}. {paper['title']}")
            print(f"     Link: {paper['link']}")
            print(f"     Summary: {paper['summary']}")
    
    except Exception as e:
        print(f"❌ Error in scientific paper search: {e}")
        return False
    
    print("\n🎉 Web Research Agent Test Completed Successfully!")
    return True

def main():
    success = test_serpapi_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
