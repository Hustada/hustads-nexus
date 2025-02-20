from agents import generate_hypothesis, reflect_hypothesis, evolve_hypothesis, ranking_hypothesis, proximity_analysis, meta_review

class Supervisor:
    def __init__(self):
        # Initialize agents
        self.generator = generate_hypothesis
        self.reflector = reflect_hypothesis
        self.evolver = evolve_hypothesis
        self.ranker = ranking_hypothesis
        self.proximity_analyzer = proximity_analysis
        self.meta_reviewer = meta_review

    def run_research_cycle(self, research_goal, iterations=5):
        # Step 1: Generate initial hypothesis
        hypothesis = self.generator(research_goal)
        history = [hypothesis]
        print("Initial hypothesis:", hypothesis)

        # Iterative refinement loop
        for i in range(iterations):
            # Step 2: Reflect on the current hypothesis
            reflection = self.reflector(hypothesis)
            # Step 3: Evolve hypothesis based on reflection
            evolved = self.evolver(hypothesis + " " + reflection)
            
            # Additional analysis steps using other agents
            ranking = self.ranker(evolved)
            proximity = self.proximity_analyzer(evolved)
            meta = self.meta_reviewer(evolved)
            
            # Combine feedback
            feedback = f"{reflection} | {ranking} | {proximity} | {meta}"
            # Update hypothesis by evolving it further with the feedback
            hypothesis = self.evolver(evolved + " " + feedback)
            history.append(hypothesis)
            print(f"Iteration {i+1}:", hypothesis)

        # Final selection: choose the best hypothesis based on a scoring function
        final_hypothesis = max(history, key=lambda h: self.score(h))
        return final_hypothesis

    def score(self, hypothesis):
        # Dummy scoring function: use length as a proxy for detail
        return len(hypothesis)

# Example usage:
if __name__ == "__main__":
    supervisor = Supervisor()
    research_goal = "Understand the mechanism of antimicrobial resistance in bacteria"
    final_output = supervisor.run_research_cycle(research_goal)
    print("Final Hypothesis:", final_output)
