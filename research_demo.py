import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom agents
from web_research_agent import WebResearchAgent
from agents import generate_hypothesis, get_gemini_response  # Use Gemini response function

def advanced_research_workflow(initial_goal):
    """
    Comprehensive research workflow integrating hypothesis generation and web research
    
    Args:
        initial_goal (str): The research objective or domain of interest
    
    Returns:
        dict: Comprehensive research findings
    """
    print("🚀 Starting Advanced Research Workflow")
    print(f"🎯 Research Goal: {initial_goal}")
    
    # Step 1: Generate Initial Hypothesis
    print("\n📝 Generating Initial Hypothesis...")
    initial_hypothesis = generate_hypothesis(initial_goal)
    print(f"💡 Generated Hypothesis: {initial_hypothesis}")
    
    # Step 2: Web Research Enrichment
    print("\n🌐 Performing Web Research...")
    research_agent = WebResearchAgent(max_sources=3)
    research_results = research_agent.research_hypothesis(initial_hypothesis)
    
    # Step 3: Analyze and Synthesize Research
    print("\n🔬 Research Analysis:")
    print("\nWeb Search Results:")
    for result in research_results.get('web_results', []):
        print(f"- {result['title']}")
        print(f"  Link: {result['link']}")
    
    print("\nScientific Papers:")
    for paper in research_results.get('scientific_papers', []):
        print(f"- {paper['title']}")
        print(f"  Link: {paper['link']}")
    
    # Use Gemini for synthesis
    synthesis_prompt = f"""
    Synthesize the research findings for the hypothesis: {initial_hypothesis}
    
    Web Results:
    {json.dumps(research_results.get('web_results', []), indent=2)}
    
    Scientific Papers:
    {json.dumps(research_results.get('scientific_papers', []), indent=2)}
    
    Provide a concise summary of key insights, potential research directions, and any notable connections.
    """
    
    try:
        synthesis_response = get_gemini_response(synthesis_prompt)
        
        print("\n🧠 Research Synthesis:")
        print(synthesis_response)
    
    except Exception as e:
        print(f"❌ Synthesis Error: {e}")
    
    return research_results

def main():
    # Example research goals
    research_goals = [
        "Quantum entanglement in biological systems",
        "AI's potential in climate change mitigation",
        "Neuroplasticity and machine learning parallels"
    ]
    
    for goal in research_goals:
        print("\n" + "="*50)
        advanced_research_workflow(goal)
        print("="*50)

if __name__ == "__main__":
    main()
