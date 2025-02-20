from agents import generate_hypothesis, reflect_hypothesis, evolve_hypothesis

def process_goal(goal):
    """Process a research goal by simulating the AI co-scientist pipeline."""
    # Generate an initial hypothesis
    hypothesis = generate_hypothesis(goal)
    # Reflect on the hypothesis
    hypothesis = reflect_hypothesis(hypothesis)
    # Evolve (refine) the hypothesis
    hypothesis = evolve_hypothesis(hypothesis)
    return hypothesis
