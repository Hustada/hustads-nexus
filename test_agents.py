import os
from agents import get_gemini_response

if __name__ == '__main__':
    prompt = "Test prompt for Google AI"
    result = get_gemini_response(prompt)
    print("Response:", result)
