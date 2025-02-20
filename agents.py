from dotenv import load_dotenv
load_dotenv()
import os
import requests
import time
from functools import wraps

def retry_with_backoff(max_retries=3, initial_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if retry == max_retries - 1:  # Last retry
                        raise
                    if e.response is not None:
                        if e.response.status_code == 429:  # Too Many Requests
                            sleep_time = delay + (retry * 2)  # Exponential backoff
                            print(f"Rate limited. Waiting {sleep_time} seconds...")
                            time.sleep(sleep_time)
                            delay *= 2
                            continue
                    raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

@retry_with_backoff()
def get_gemini_response(prompt):
    """Helper function to call the Gemini API with rate limiting and retries."""
    gemini_key = os.getenv('GEMINI_API_KEY')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        # Add a small delay between requests to help avoid rate limiting
        time.sleep(0.5)
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        raw_response = response.json()
        
        result = raw_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not result:
            return "[No response generated. Please try again.]"        
        return result
    
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 429:
                error_msg = "Rate limit exceeded. Please wait a moment and try again."
            elif e.response.status_code == 403:
                error_msg = "API key error. Please check your Gemini API key."
        return f"[Error: {error_msg}]"

def generate_hypothesis(goal):
    """Generate an initial hypothesis based on the research goal using Gemini."""
    prompt = (
        f"Generate a scientific hypothesis for the following research goal: {goal}\n\n"
        "Requirements:\n"
        "1. State the hypothesis clearly and concisely\n"
        "2. Include specific, testable relationships between variables\n"
        "3. Ensure it is falsifiable\n"
        "4. Base it on existing scientific knowledge\n"
        "Format as: 'If [independent variable], then [dependent variable], because [mechanism].'\n"
    )
    return get_gemini_response(prompt)

def reflect_hypothesis(hypothesis):
    """Reflect on the hypothesis using Gemini."""
    prompt = (
        f"Critically reflect on this hypothesis: {hypothesis}\n\n"
        "Provide structured feedback on:\n"
        "1. STRENGTHS: What aspects of the hypothesis are well-formulated?\n"
        "2. WEAKNESSES: What are potential gaps or problems?\n"
        "3. ASSUMPTIONS: What underlying assumptions should be examined?\n"
        "4. IMPROVEMENTS: Specific suggestions for strengthening the hypothesis\n"
    )
    return get_gemini_response(prompt)

def evolve_hypothesis(hypothesis):
    """Refine and improve the hypothesis using Gemini."""
    prompt = (
        f"Evolve and improve this hypothesis: {hypothesis}\n\n"
        "Create an improved version that:\n"
        "1. Addresses any identified weaknesses\n"
        "2. Makes relationships more precise\n"
        "3. Clarifies mechanisms\n"
        "4. Maintains testability\n"
        "Format as: 'EVOLVED HYPOTHESIS: [your improved hypothesis]'\n"
    )
    return get_gemini_response(prompt)

def ranking_hypothesis(hypothesis):
    """Rank the hypothesis for clarity and novelty using Gemini."""
    prompt = (
        f"Evaluate this hypothesis: {hypothesis}\n\n"
        "Rate and explain each criterion (1-10 scale):\n"
        "1. CLARITY: How clear and unambiguous is it?\n"
        "2. TESTABILITY: How feasible is it to test?\n"
        "3. NOVELTY: How original is the idea?\n"
        "4. IMPACT: Potential scientific significance if true?\n"
        "Conclude with an OVERALL SCORE and brief justification.\n"
    )
    return get_gemini_response(prompt)

def proximity_analysis(hypothesis):
    """Analyze the proximity and relevance of all variables in the hypothesis using Gemini."""
    prompt = (
        f"Analyze the relationships between variables in this hypothesis: {hypothesis}\n\n"
        "Provide:\n"
        "1. VARIABLES: List all identified variables\n"
        "2. RELATIONSHIPS: Map connections between variables\n"
        "3. CONFOUNDERS: Potential confounding variables\n"
        "4. CONTROLS: Suggested control variables\n"
        "5. MEASUREMENT: How each variable could be measured\n"
    )
    return get_gemini_response(prompt)

def meta_review(hypothesis):
    """Perform a meta-review of the hypothesis for scientific rigor using Gemini."""
    prompt = (
        f"Conduct a meta-review of this hypothesis: {hypothesis}\n\n"
        "Evaluate:\n"
        "1. THEORETICAL FOUNDATION: Alignment with existing theories\n"
        "2. METHODOLOGY: Suggested experimental approaches\n"
        "3. IMPLICATIONS: Potential impact on the field\n"
        "4. FEASIBILITY: Resources and expertise needed\n"
        "5. ETHICS: Any ethical considerations\n"
    )
    return get_gemini_response(prompt)
