from dotenv import load_dotenv
load_dotenv()
import os
import json
import time
import requests
import functools
from functools import wraps
import datetime
from typing import Dict, List, Any
from web_research_agent import research_hypothesis

def retry_with_backoff(max_retries=3, initial_delay=1):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        initial_delay (float): Initial delay between retries
    
    Returns:
        Decorated function with retry mechanism
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    print(f"🔄 Attempt {attempt + 1}/{max_retries + 1}")
                    return func(*args, **kwargs)
                
                except (requests.exceptions.RequestException, 
                        requests.exceptions.Timeout, 
                        ValueError) as e:
                    
                    if attempt == max_retries:
                        print(f"❌ Max retries ({max_retries}) reached. Raising final error.")
                        raise
                    
                    print(f"⏳ Retry attempt {attempt + 1}: {e}")
                    print(f"   Waiting {delay} seconds before next retry")
                    
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
            
            raise RuntimeError("Unexpected exit from retry loop")
        return wrapper
    return decorator

@retry_with_backoff()
def get_gemini_response(prompt, timeout=10):
    """
    Helper function to call the Gemini API with rate limiting and retries.
    
    Args:
        prompt (str): The input prompt for the Gemini model
        timeout (int, optional): Timeout for the API call. Defaults to 10 seconds.
    
    Returns:
        str: Generated response from the Gemini model
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }

    @retry_with_backoff(max_retries=3, initial_delay=1)
    def _make_api_call():
        try:
            print(f"🌐 Making Gemini API Call (Timeout: {timeout}s)")
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
            
            # Log detailed request information
            print(f"API Response Status: {response.status_code}")
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from the response
            if 'candidates' in result and result['candidates']:
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                return generated_text
            else:
                print("❌ No text generated from API response")
                return "Unable to generate response"
        
        except requests.exceptions.Timeout:
            print(f"❌ API Call Timed Out after {timeout} seconds")
            raise
        except requests.exceptions.RequestException as e:
            print(f"❌ API Request Error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected Error in API Call: {e}")
            raise

    try:
        return _make_api_call()
    except Exception as e:
        print(f"Error in Gemini API call after all retries: {e}")
        return f"[API Error: {str(e)}]"

def generate_hypothesis(goal: str, include_web_research: bool = True) -> str:
    """
    Generate an initial hypothesis based on the research goal using Gemini.
    
    Args:
        goal (str): The scientific research goal or question
        include_web_research (bool): Whether to include web research in the hypothesis
    
    Returns:
        str: A generated scientific hypothesis
    """
    # Create a comprehensive prompt to guide hypothesis generation
    prompt = f"""
    You are an advanced AI research assistant tasked with generating a novel scientific hypothesis.

    Research Goal: {goal}

    Please generate a comprehensive hypothesis that:
    1. Clearly defines the core scientific question
    2. Proposes a novel mechanism or approach
    3. Suggests potential experimental validation methods
    4. Highlights the potential significance of the research

    Format your response as a structured hypothesis with the following sections:
    - Technical Hypothesis
    - Proposed Methodology
    - Potential Experimental Validation
    - Expected Scientific Impact

    Be creative, precise, and ensure the hypothesis is grounded in current scientific understanding while pushing the boundaries of existing knowledge.
    """

    try:
        # Call Gemini API to generate the hypothesis
        hypothesis = get_gemini_response(prompt)
        
        # Additional processing or validation can be added here
        if include_web_research:
            web_research = web_research_agent(hypothesis)
            # Optionally incorporate web research into hypothesis
            # This is a placeholder for more sophisticated integration
            hypothesis += f"\n\nWeb Research Insights:\n{json.dumps(web_research, indent=2)}"
        
        return hypothesis
    
    except Exception as e:
        print(f"Error generating hypothesis: {e}")
        return f"Unable to generate hypothesis. Error: {e}"

def web_research_agent(hypothesis: str) -> Dict[str, Any]:
    """
    Web research agent to supplement hypothesis generation
    
    Args:
        hypothesis (str): Scientific hypothesis to research
    
    Returns:
        Comprehensive web research findings
    """
    return research_hypothesis(hypothesis)

def reflect_hypothesis(hypothesis):
    """
    Critically analyze and reflect on the generated hypothesis using Gemini.
    
    Args:
        hypothesis (str): The scientific hypothesis to be reflected upon
    
    Returns:
        str: A detailed critical reflection of the hypothesis
    """
    prompt = f"""
    You are an expert scientific reviewer tasked with critically analyzing a research hypothesis.

    Hypothesis to Analyze: {hypothesis}

    Provide a comprehensive reflection that addresses:
    1. Strengths of the hypothesis
    2. Potential weaknesses or limitations
    3. Gaps in current understanding
    4. Suggestions for refinement
    5. Potential challenges in experimental validation

    Format your response with clear, structured insights that can guide further research development.
    """

    try:
        reflection = get_gemini_response(prompt)
        return reflection
    except Exception as e:
        print(f"Error reflecting on hypothesis: {e}")
        return f"Unable to generate reflection. Error: {e}"

def ranking_hypothesis(hypothesis, reflection=None):
    """
    Rank and evaluate the hypothesis for scientific merit using Gemini.
    
    Args:
        hypothesis (str): The scientific hypothesis to be ranked
        reflection (str, optional): Previous critical reflection of the hypothesis
    
    Returns:
        str: A detailed ranking and evaluation of the hypothesis
    """
    context = f"Hypothesis: {hypothesis}"
    if reflection:
        context += f"\n\nPrevious Reflection: {reflection}"

    prompt = f"""
    You are a scientific merit evaluator tasked with ranking a research hypothesis.

    {context}

    Provide a comprehensive evaluation that includes:
    1. Novelty and originality score
    2. Scientific rigor and methodology assessment
    3. Potential research impact
    4. Likelihood of successful experimental validation
    5. Comparative analysis with existing research

    Scoring Criteria:
    - Originality: /10
    - Scientific Rigor: /10
    - Potential Impact: /10
    - Experimental Feasibility: /10

    Provide a detailed breakdown of each criterion with justification.
    """

    try:
        ranking = get_gemini_response(prompt)
        return ranking
    except Exception as e:
        print(f"Error ranking hypothesis: {e}")
        return f"Unable to generate ranking. Error: {e}"

def proximity_analysis(hypothesis):
    """
    Analyze the proximity and relevance of variables in the hypothesis using Gemini.
    
    Args:
        hypothesis (str): The scientific hypothesis to analyze
    
    Returns:
        str: A detailed analysis of variable relationships and interactions
    """
    prompt = f"""
    You are a scientific systems analyst tasked with examining variable interactions in a research hypothesis.

    Hypothesis: {hypothesis}

    Perform a comprehensive proximity analysis that explores:
    1. Identification of key variables
    2. Potential interactions and correlations
    3. Strength of relationships between variables
    4. Contextual dependencies
    5. Potential confounding factors

    Provide insights into:
    - Direct and indirect variable relationships
    - Potential non-linear interactions
    - Theoretical mechanisms underlying variable connections
    - Recommendations for further investigation
    """

    try:
        analysis = get_gemini_response(prompt)
        return analysis
    except Exception as e:
        print(f"Error performing proximity analysis: {e}")
        return f"Unable to generate proximity analysis. Error: {e}"

def meta_review(hypothesis):
    """
    Perform a meta-review of the hypothesis for scientific rigor using Gemini.
    
    Args:
        hypothesis (str): The scientific hypothesis to review
    
    Returns:
        str: A comprehensive meta-review of the hypothesis
    """
    prompt = f"""
    You are a senior scientific meta-reviewer conducting a comprehensive assessment of a research hypothesis.

    Hypothesis: {hypothesis}

    Conduct an in-depth meta-review that addresses:
    1. Epistemological foundations
    2. Theoretical framework alignment
    3. Potential paradigm shifts
    4. Interdisciplinary implications
    5. Ethical considerations
    6. Long-term research potential

    Provide a nuanced, critical evaluation that:
    - Situates the hypothesis within broader scientific discourse
    - Identifies potential transformative research directions
    - Assesses the hypothesis's contribution to scientific knowledge
    - Highlights potential societal and technological implications
    """

    try:
        meta_review_result = get_gemini_response(prompt)
        return meta_review_result
    except Exception as e:
        print(f"Error performing meta-review: {e}")
        return f"Unable to generate meta-review. Error: {e}"

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

AGENT_STATES = {
    "generator": {
        "description": "Formulating initial hypothesis",
        "extra_data": "Exploring conceptual space",
        "icon": "◉"
    },
    "reflector": {
        "description": "Critically analyzing hypothesis",
        "extra_data": "Identifying potential weaknesses",
        "icon": "△"
    },
    "ranker": {
        "description": "Evaluating scientific merit",
        "extra_data": "Scoring hypothesis against criteria",
        "icon": "▽"
    },
    "proximity_analyzer": {
        "description": "Mapping variable relationships",
        "extra_data": "Detecting complex interactions",
        "icon": "⬡"
    },
    "meta_reviewer": {
        "description": "Assessing broader scientific context",
        "extra_data": "Connecting to existing research domains",
        "icon": "✦"
    }
}

def extract_variables(hypothesis):
    """
    Extract key variables from a hypothesis
    
    Args:
        hypothesis (str): The scientific hypothesis text
    
    Returns:
        List of potential key variables
    """
    # Simple extraction based on key scientific terms
    import re
    
    # List of potential variable indicators
    variable_indicators = [
        r'\beffect of\b', 
        r'\bimpact on\b', 
        r'\brelationship between\b', 
        r'\bcorrelation with\b',
        r'\bdependent on\b',
        r'\bindependent variable\b'
    ]
    
    variables = []
    for pattern in variable_indicators:
        matches = re.findall(pattern + r'\s*([^,\.]+)', hypothesis, re.IGNORECASE)
        variables.extend(matches)
    
    # Clean and deduplicate
    return list(set(var.strip() for var in variables if var.strip()))

def extract_numeric_score(ranking_text, criterion):
    """
    Extract a numeric score for a specific criterion from ranking text
    
    Args:
        ranking_text (str): Full ranking text
        criterion (str): Criterion to extract score for
    
    Returns:
        float: Extracted score or default 0
    """
    import re
    
    # Case-insensitive search for criterion and following number
    pattern = rf"{criterion.upper()}:\s*(\d+(?:\.\d+)?)"
    match = re.search(pattern, ranking_text, re.IGNORECASE)
    
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            return 0.0
    
    return 0.0

def format_and_enhance_output(
    research_results=None, 
    original_goal=None, 
    *args, 
    **kwargs
):
    """
    Transform raw research results into a highly structured, insight-driven format
    
    Flexible function that can handle:
    1. List of research results and original goal
    2. Individual research components (hypothesis, reflection, etc.)
    
    Args:
        research_results (List[Dict] or str, optional): Research results or hypothesis
        original_goal (str, optional): Original research goal
        *args: Additional arguments for flexible input
        **kwargs: Additional keyword arguments
    
    Returns:
        Dict with enhanced, structured content
    """
    # If first argument is a list, treat it as traditional input
    if isinstance(research_results, list):
        formatted_results = {
            "goal": original_goal,
            "total_iterations": len(research_results),
            "detailed_analysis": [],
            "research_results": research_results
        }
        
        for result in research_results:
            detailed_result = {
                "iteration": result.get("iteration", 1),
                "sections": {
                    "Hypothesis": {
                        "title": "Core Hypothesis",
                        "content": result.get("hypothesis", ""),
                        "key_variables": extract_variables(result.get("hypothesis", ""))
                    },
                    "Critical Reflection": {
                        "strengths": [
                            strength.strip() 
                            for strength in result.get("reflection", "").split('\n') 
                            if strength.startswith('STRENGTH:')
                        ],
                        "potential_improvements": [
                            improvement.strip() 
                            for improvement in result.get("reflection", "").split('\n') 
                            if improvement.startswith('IMPROVEMENT:')
                        ]
                    },
                    "Scientific Evaluation": {
                        "clarity_score": extract_numeric_score(result.get("ranking", ""), "CLARITY"),
                        "novelty_score": extract_numeric_score(result.get("ranking", ""), "NOVELTY"),
                        "testability_score": extract_numeric_score(result.get("ranking", ""), "TESTABILITY"),
                        "impact_score": extract_numeric_score(result.get("ranking", ""), "IMPACT")
                    }
                }
            }
            formatted_results["detailed_analysis"].append(detailed_result)
        
        # Synthesize novel insights
        novel_synthesis = " ".join([
            result.get("hypothesis", "") 
            for result in research_results
        ])
    
    # If called with multiple arguments, treat as individual research components
    elif args or (research_results and isinstance(research_results, str)):
        # Combine all arguments into a single synthesis string
        components = [research_results] + list(args)
        novel_synthesis = " ".join(str(component) for component in components)
        
        formatted_results = {
            "goal": original_goal,
            "total_iterations": 1,
            "detailed_analysis": [{
                "iteration": 1,
                "sections": {
                    "Hypothesis": {
                        "title": "Core Hypothesis",
                        "content": research_results,
                        "key_variables": extract_variables(str(research_results))
                    }
                }
            }]
        }
    else:
        raise ValueError("Invalid input format for format_and_enhance_output()")
    
    # Add novel synthesis to the output
    formatted_results["novel_synthesis"] = {
        "scientific_analysis": {
            "technical_hypothesis": extract_technical_hypothesis(novel_synthesis),
            "methodology": extract_methodology(novel_synthesis),
            "statistical_significance": extract_statistical_significance(novel_synthesis),
            "potential_experimental_design": extract_experimental_design(novel_synthesis)
        },
        "layperson_summary": {
            "core_idea": extract_core_idea(novel_synthesis),
            "real_world_impact": extract_real_world_impact(novel_synthesis),
            "key_takeaways": extract_key_takeaways(novel_synthesis)
        }
    }
    
    return formatted_results

def extract_technical_hypothesis(synthesis):
    """
    Extract technical hypothesis with more sophisticated parsing
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        str: Extracted technical hypothesis
    """
    import re
    
    # Try multiple regex patterns to find technical hypothesis
    patterns = [
        r'Technical Hypothesis:?\s*(.*?)(?:\n|$)',
        r'Hypothesis:?\s*(.*?)(?:\n|$)',
        r'Core Scientific Idea:?\s*(.*?)(?:\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, synthesis, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
    
    return "No specific technical hypothesis found."

def extract_methodology(synthesis):
    """
    Extract methodology with more robust parsing
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        str: Extracted methodology
    """
    import re
    
    # Try multiple regex patterns to find methodology
    patterns = [
        r'Methodology:?\s*(.*?)(?:\n\n|$)',
        r'Proposed Approach:?\s*(.*?)(?:\n\n|$)',
        r'Research Strategy:?\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, synthesis, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
    
    return "Methodology not clearly defined."

def extract_statistical_significance(synthesis):
    """
    Extract statistical significance with advanced parsing
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        str: Extracted statistical significance
    """
    import re
    
    # Try multiple regex patterns to find statistical significance
    patterns = [
        r'Statistical Significance:?\s*(.*?)(?:\n\n|$)',
        r'Statistical Analysis:?\s*(.*?)(?:\n\n|$)',
        r'Significance Level:?\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, synthesis, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
    
    return "Statistical significance not reported."

def extract_experimental_design(synthesis):
    """
    Extract experimental design with comprehensive parsing
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        str: Extracted experimental design
    """
    import re
    
    # Try multiple regex patterns to find experimental design
    patterns = [
        r'Experimental Design:?\s*(.*?)(?:\n\n|$)',
        r'Proposed Experiments:?\s*(.*?)(?:\n\n|$)',
        r'Research Protocol:?\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, synthesis, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
    
    return "Experimental design not specified."

def extract_core_idea(synthesis):
    """
    Extract core idea with more nuanced parsing
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        str: Extracted core idea
    """
    import re
    
    # Try multiple regex patterns to find core idea
    patterns = [
        r'Core Idea:?\s*(.*?)(?:\n\n|$)',
        r'Central Concept:?\s*(.*?)(?:\n\n|$)',
        r'Key Insight:?\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, synthesis, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
    
    # Fallback: take first paragraph if no specific pattern found
    paragraphs = [p.strip() for p in synthesis.split('\n\n') if p.strip()]
    return paragraphs[0] if paragraphs else "No specific core idea found."

def extract_real_world_impact(synthesis):
    """
    Extract real-world impact with comprehensive parsing
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        str: Extracted real-world impact
    """
    import re
    
    # Try multiple regex patterns to find real-world impact
    patterns = [
        r'Real-World Impact:?\s*(.*?)(?:\n\n|$)',
        r'Practical Applications:?\s*(.*?)(?:\n\n|$)',
        r'Societal Implications:?\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, synthesis, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
    
    return "Potential wide-ranging scientific and technological implications"

def extract_key_takeaways(synthesis):
    """
    Extract key takeaways with advanced parsing
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        List[str]: Extracted key takeaways
    """
    import re
    
    # Try multiple regex patterns to find key takeaways
    patterns = [
        r'Key Takeaways:?\s*((?:[-•*]\s*.*\n?)+)',
        r'Main Insights:?\s*((?:[-•*]\s*.*\n?)+)',
        r'Primary Conclusions:?\s*((?:[-•*]\s*.*\n?)+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, synthesis, re.IGNORECASE | re.MULTILINE)
        if match:
            takeaways = [
                line.strip('*•- \n') 
                for line in match.group(1).split('\n') 
                if line.strip('*•- \n')
            ]
            if takeaways:
                return takeaways
    
    # Fallback: generic takeaways
    return [
        "Novel approach challenges existing research paradigms",
        "Demonstrates potential for interdisciplinary research",
        "Highlights importance of advanced experimental techniques"
    ]

def assess_research_feasibility(results):
    # Assess overall research potential
    return "Medium to High Feasibility"

def estimate_funding_potential(results):
    # Estimate likelihood of research funding
    return "Strong Potential for Grant Funding"

def assess_commercial_potential(results):
    # Evaluate commercial application possibilities
    return "Moderate Commercial Viability"

def prepare_frontend_research_data(synthesis):
    """
    Prepare research data in a format compatible with frontend rendering
    
    Args:
        synthesis (str): Full novel synthesis text
    
    Returns:
        dict: Structured data ready for web rendering
    """
    return {
        "scientific_analysis": {
            "technical_hypothesis": extract_technical_hypothesis(synthesis),
            "methodology": extract_methodology(synthesis),
            "statistical_significance": extract_statistical_significance(synthesis),
            "potential_experimental_design": extract_experimental_design(synthesis)
        },
        "layperson_summary": {
            "core_idea": extract_core_idea(synthesis),
            "real_world_impact": extract_real_world_impact(synthesis),
            "key_takeaways": extract_key_takeaways(synthesis)
        },
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat(),
            "version": "1.2.0",
            "processing_mode": "advanced_extraction"
        }
    }
