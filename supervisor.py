from dataclasses import dataclass, field
from typing import List, Dict, Any
import json
from datetime import datetime

from agents import (
    generate_hypothesis, 
    reflect_hypothesis, 
    ranking_hypothesis, 
    proximity_analysis, 
    meta_review,
    format_and_enhance_output,
    prepare_frontend_research_data,  
    AGENT_STATES
)

@dataclass
class ResearchCycle:
    goal: str
    iterations: int = 3
    current_iteration: int = 1
    research_results: List[Dict[str, Any]] = field(default_factory=list)
    active_agent: str = None
    progress_log: List[Dict[str, Any]] = field(default_factory=list)
    progress_callback: Any = None

    def track_agent_progress(self, agent_name: str, details: Dict[str, Any] = None):
        """
        Log agent progress with symbolic tracking
        """
        progress_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "details": details or AGENT_STATES.get(agent_name, {}),
            "iteration": self.current_iteration
        }
        self.progress_log.append(progress_entry)
        
        # Optional: Emit progress via WebSocket or logging
        self._emit_progress(progress_entry)

    def _emit_progress(self, progress_entry):
        """
        Emit progress to frontend via callback
        """
        if self.progress_callback:
            # Simplified progress message for frontend
            simple_progress = {
                "status": f"{progress_entry['details'].get('description', 'Processing')} - Iteration {progress_entry['iteration']}",
                "agent": progress_entry['agent'],
                "iteration": progress_entry['iteration']
            }
            self.progress_callback(simple_progress)
        print(f"Progress: {json.dumps(progress_entry, indent=2)}")

    def run_research_cycle(self) -> Dict[str, Any]:
        """
        Execute full research cycle with enhanced tracking and formatting
        """
        # Reset research results and progress log
        self.research_results = []
        self.progress_log = []
        self.current_iteration = 1

        try:
            while self.current_iteration <= self.iterations:
                print(f"🔬 Starting Iteration {self.current_iteration}")
                
                # Hypothesis Generation
                self.active_agent = "generator"
                self.track_agent_progress(self.active_agent)
                hypothesis = generate_hypothesis(self.goal)

                # Reflection
                self.active_agent = "reflector"
                self.track_agent_progress(self.active_agent)
                reflection = reflect_hypothesis(hypothesis)

                # Ranking
                self.active_agent = "ranker"
                self.track_agent_progress(self.active_agent)
                ranking = ranking_hypothesis(hypothesis, reflection)

                # Proximity Analysis
                self.active_agent = "proximity_analyzer"
                self.track_agent_progress(self.active_agent)
                proximity_result = proximity_analysis(hypothesis)

                # Meta Review
                self.active_agent = "meta_reviewer"
                self.track_agent_progress(self.active_agent)
                meta_review_result = meta_review(hypothesis)

                # Novel Synthesis with new flexible format
                novel_synthesis = format_and_enhance_output(
                    [
                        {
                            "hypothesis": hypothesis,
                            "reflection": reflection,
                            "ranking": ranking,
                            "proximity_analysis": proximity_result,
                            "meta_review": meta_review_result
                        }
                    ],
                    original_goal=self.goal
                )

                # Compile Research Result
                research_result = {
                    "iterations": [{
                        "iteration": self.current_iteration,
                        "hypothesis": hypothesis,
                        "reflection": reflection,
                        "ranking": ranking,
                        "goal": self.goal
                    }],
                    "novel_synthesis": novel_synthesis
                }

                self.research_results.append(research_result)
                self.current_iteration += 1

                # Optional: Break if we've reached desired state
                if self._should_terminate_research():
                    break

        except Exception as e:
            print(f"Research cycle error: {e}")
            return {"error": str(e)}

        return self.research_results[0] if self.research_results else {}

    def _should_terminate_research(self):
        """
        Determine if research cycle should terminate early
        
        Can be customized with more complex logic in future
        """
        return self.current_iteration > self.iterations

def initiate_research(research_goal: str, iterations: int = 1, progress_callback=None) -> Dict[str, Any]:
    """
    Initiate a new research cycle
    
    Args:
        research_goal (str): The scientific question or objective
        iterations (int, optional): Number of research iterations. Defaults to 1.
        progress_callback (callable, optional): Function to track progress. Defaults to None.
    
    Returns:
        Dict containing research results and metadata
    """
    print(f"🚀 Initiating Research Cycle: {research_goal}")
    print(f"   Iterations: {iterations}")
    
    # Create ResearchCycle instance with optional progress callback
    research_cycle = ResearchCycle(
        goal=research_goal, 
        iterations=iterations,
        progress_callback=progress_callback
    )
    
    # Execute research cycle and return results
    return research_cycle.run_research_cycle()

if __name__ == "__main__":
    research_goal = "Understand the mechanism of antimicrobial resistance in bacteria"
    results = initiate_research(research_goal)
    print(json.dumps(results, indent=2))
