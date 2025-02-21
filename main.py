import json
import time
from supervisor import initiate_research

def test_research_cycle(goal, iterations=1):
    """
    Test the research cycle with a given goal and print detailed results
    
    Args:
        goal (str): Research goal to investigate
        iterations (int, optional): Number of research iterations. Defaults to 1.
    """
    print(f"🔬 Starting Research Cycle for Goal: {goal}")
    print("=" * 50)

    try:
        # Initiate research cycle
        research_results = initiate_research(
            goal, 
            iterations=iterations,
            progress_callback=lambda msg: print(f"🔹 Progress: {json.dumps(msg, indent=2)}")
        )

        # Pretty print results
        print("\n🏁 Research Cycle Complete 🏁")
        print("=" * 50)
        
        # Print summary of results
        print(f"Goal: {research_results['goal']}")
        print(f"Total Iterations: {research_results['total_iterations']}")
        print("\nResults Summary:")
        
        # Safely handle results display
        results = research_results.get('results', {})
        if isinstance(results, dict):
            for key, value in results.items():
                print(f"\n{key.upper()}:")
                if isinstance(value, list):
                    for item in value:
                        print(json.dumps(item, indent=2))
                elif isinstance(value, dict):
                    print(json.dumps(value, indent=2))
                else:
                    print(str(value))
        else:
            print("No detailed results available.")

    except Exception as e:
        print(f"❌ Research Cycle Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Example research goals
    research_goals = [
        "Develop a novel approach to understanding quantum entanglement in biological systems",
        "Explore potential mechanisms for reversing neurological aging",
        "Investigate sustainable energy solutions using advanced materials science"
    ]

    # Test with only the first research goal
    test_research_cycle(research_goals[0])  # Run only the first goal
