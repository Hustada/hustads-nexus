from agents import generate_hypothesis, reflect_hypothesis, evolve_hypothesis, ranking_hypothesis, proximity_analysis, meta_review
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class HypothesisAnalysis:
    hypothesis: str
    reflection: Optional[str] = None
    ranking: Optional[str] = None
    proximity_analysis: Optional[str] = None
    meta_review: Optional[str] = None
    iteration: int = 0

class Supervisor:
    def __init__(self):
        self.generator = generate_hypothesis
        self.reflector = reflect_hypothesis
        self.evolver = evolve_hypothesis
        self.ranker = ranking_hypothesis
        self.proximity_analyzer = proximity_analysis
        self.meta_reviewer = meta_review
    
    def analyze_hypothesis(self, hypothesis: str, iteration: int = 0) -> HypothesisAnalysis:
        """Run a complete analysis of a hypothesis using all agents."""
        reflection = self.reflector(hypothesis)
        ranking = self.ranker(hypothesis)
        proximity = self.proximity_analyzer(hypothesis)
        meta = self.meta_reviewer(hypothesis)
        
        return HypothesisAnalysis(
            hypothesis=hypothesis,
            reflection=reflection,
            ranking=ranking,
            proximity_analysis=proximity,
            meta_review=meta,
            iteration=iteration
        )
    
    def run_research_cycle(self, research_goal: str, iterations: int = 1) -> List[HypothesisAnalysis]:
        """Run a complete research cycle and return analysis from all agents."""
        # Generate initial hypothesis
        current_hypothesis = self.generator(research_goal)
        results = []
        
        # Initial analysis
        analysis = self.analyze_hypothesis(current_hypothesis, 0)
        results.append(analysis)
        
        # Iterative refinement
        for i in range(iterations):
            # Combine all feedback for evolution
            feedback = f"Reflection: {analysis.reflection}\nRanking: {analysis.ranking}\nProximity: {analysis.proximity_analysis}\nMeta Review: {analysis.meta_review}"
            
            # Evolve hypothesis with feedback
            current_hypothesis = self.evolver(current_hypothesis + "\n\nFeedback:\n" + feedback)
            
            # Analyze new hypothesis
            analysis = self.analyze_hypothesis(current_hypothesis, i + 1)
            results.append(analysis)
        
        return results

def run_research_cycle(goal: str) -> List[HypothesisAnalysis]:
    """Main entry point for running a research cycle."""
    supervisor = Supervisor()
    return supervisor.run_research_cycle(goal)

if __name__ == "__main__":
    research_goal = "Understand the mechanism of antimicrobial resistance in bacteria"
    results = run_research_cycle(research_goal)
    for analysis in results:
        print(f"\nIteration {analysis.iteration}:\n" + "=" * 50)
        print(f"Hypothesis: {analysis.hypothesis}\n")
        print(f"Reflection: {analysis.reflection}\n")
        print(f"Ranking: {analysis.ranking}\n")
        print(f"Proximity Analysis: {analysis.proximity_analysis}\n")
        print(f"Meta Review: {analysis.meta_review}\n")
