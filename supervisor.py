from agents import generate_hypothesis, reflect_hypothesis, evolve_hypothesis, ranking_hypothesis, proximity_analysis, meta_review

def summarize_text(text, max_len=150):
    """Summarize the text by returning the first and last part if it exceeds max_len."""
    if len(text) <= max_len:
        return text
    half = max_len // 2
    return text[:half] + ' ... ' + text[-half:]

class Supervisor:
    def __init__(self):
        # Initialize agents from the imported functions.
        self.generator = generate_hypothesis
        self.reflector = reflect_hypothesis
        self.evolver = evolve_hypothesis
        self.ranker = ranking_hypothesis
        self.proximity_analyzer = proximity_analysis
        self.meta_reviewer = meta_review

    def run_research_cycle(self, research_goal, iterations=5, verbose=False):
        # Generate the initial hypothesis using the research goal.
        hypothesis = self.generator(research_goal)
        history = [hypothesis]
        if verbose:
            print("Initial hypothesis:", hypothesis)
        else:
            print("Initial hypothesis (summarized):", summarize_text(hypothesis))

        # Iterative refinement loop.
        for i in range(iterations):
            # Reflect on the current hypothesis.
            reflection = self.reflector(hypothesis)
            # Evolve hypothesis using the reflection feedback.
            evolved = self.evolver(hypothesis + " " + reflection)

            # Additional analysis using ranking, proximity, and meta-review.
            ranking = self.ranker(evolved)
            proximity = self.proximity_analyzer(evolved)
            meta = self.meta_reviewer(evolved)

            # Combine all feedback to inform further evolution.
            feedback = f"{reflection} | {ranking} | {proximity} | {meta}"
            # Further update the hypothesis by evolving it with the combined feedback.
            hypothesis = self.evolver(evolved + " " + feedback)
            history.append(hypothesis)
            if verbose:
                print(f"Iteration {i+1}:", hypothesis)
            else:
                print(f"Iteration {i+1} (summarized):", summarize_text(hypothesis))

        # Select the best hypothesis using a simple scoring function (here, based on length).
        final_hypothesis = max(history, key=lambda h: self.score(h))
        return final_hypothesis

    def score(self, hypothesis):
        # Dummy scoring function: using length as a proxy for detail.
        # In practice, this should be replaced with a robust evaluation metric.
        return len(hypothesis)

# Example usage:
if __name__ == "__main__":
    supervisor = Supervisor()
    research_goal = "Understand the mechanism of antimicrobial resistance in bacteria"
    final_output = supervisor.run_research_cycle(research_goal, iterations=3, verbose=False)
    print("Final Hypothesis:", summarize_text(final_output))
