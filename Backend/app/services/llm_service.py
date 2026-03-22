import requests
import json
import os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_TAGS_URL = os.environ.get("OLLAMA_TAGS_URL", "http://localhost:11434/api/tags")

def get_default_model():
    try:
        res = requests.get(OLLAMA_TAGS_URL, timeout=5)
        if res.status_code == 200:
            models = res.json().get("models", [])
            if models:
                return models[0]["name"]
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
    return "llama3"

# Automatically selects the first available local model or defaults to llama3
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", get_default_model())

def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return ""

def generate_questions(resume_text: str, num_questions: int = 5):
    prompt = f"""
    You are an expert technical interviewer. Based on the following resume, generate {num_questions} 
    relevant interview questions to assess the candidate's skills and experience.
    Return STRICTLY a JSON object with a single key "questions" mapping to an array of strings.
    Format: {{"questions": ["Q1", "Q2", "Q3"]}}
    
    Resume content:
    {resume_text[:3000]}
    """
    
    response_text = call_ollama(prompt)
    if response_text:
        try:
            cleaned = response_text.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned)
            if isinstance(data, dict) and "questions" in data:
                return data["questions"][:num_questions]
            elif isinstance(data, list):
                return data[:num_questions]
            elif isinstance(data, dict):
                # Fallback if it used another key
                for val in data.values():
                    if isinstance(val, list):
                        return val[:num_questions]
        except Exception as e:
            print(f"Failed to parse Ollama generation: {e}")
    
    # Fallback if Ollama is unreachable
    return [
       "Tell me about your most recent project.",
       "What motivated you to apply for this role?",
       "Can you describe a time you had a conflict at work?",
       "How do you stay updated with technology?",
       "Do you have any questions for us?"
    ]

def evaluate_answer(question: str, answer: str):
    prompt = f"""
    You are an AI interviewer evaluating a candidate's answer.
    Question: {question}
    Candidate's Answer: {answer}
    
    Rate the answer out of 100 for three categories: confidence, communication, and technical knowledge.
    Provide a short, 1-2 sentence feedback string.
    Return strictly a JSON object, no markdown format blocks. 
    Format required:
    {{
        "confidence": 85,
        "communication": 90,
        "technical": 80,
        "feedback": "Good response with clear points."
    }}
    """
    
    response_text = call_ollama(prompt)
    if response_text:
        try:
            cleaned = response_text.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned)
            return data
        except Exception as e:
            print(f"Failed to parse Ollama evaluation: {e}")
    
    return {
        "confidence": 70,
        "communication": 70,
        "technical": 70,
        "feedback": "Ollama fallback. Please ensure Ollama is running and accessible."
    }
