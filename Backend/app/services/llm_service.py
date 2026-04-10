import requests
import json
import os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_TAGS_URL = os.environ.get("OLLAMA_TAGS_URL", "http://localhost:11434/api/tags")

_OLLAMA_MODEL = None

def get_ollama_model():
    global _OLLAMA_MODEL
    if _OLLAMA_MODEL is None:
        _OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL")
        if not _OLLAMA_MODEL:
            try:
                res = requests.get(OLLAMA_TAGS_URL, timeout=1)
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    if models:
                        _OLLAMA_MODEL = models[0]["name"]
            except Exception as e:
                pass
            if not _OLLAMA_MODEL:
                _OLLAMA_MODEL = "llama3"
    return _OLLAMA_MODEL

def call_ollama(prompt: str) -> str:
    payload = {
        "model": get_ollama_model(),
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

def generate_questions(context: str, num_questions: int = 5):
    prompt = f"""
    You are an expert technical interviewer. Based on the following extracted resume chunks, generate {num_questions} 
    relevant interview questions to assess the candidate's skills and experience.
    Return STRICTLY a JSON object with a single key "questions" mapping to an array of strings.
    Format: {{"questions": ["Q1", "Q2", "Q3"]}}
    
    Resume chunks context:
    {context}
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

def evaluate_answer(question: str, answer: str, context: str):
    prompt = f"""
    You are an expert AI interviewer critically evaluating a candidate's answer.
    
    Resume Context:
    {context}
    
    Question Asked: {question}
    Candidate's Answer: {answer}
    
    CRITICAL EVALUATION INSTRUCTIONS:
    1. Technical Accuracy (0-100): Is the answer factually correct? Does it comprehensively address the question asked? Be absolutely unforgiving. If the answer is vague, generic, irrelevant, or misses the core point, score strictly below 40.
    2. Communication (0-100): Is the answer well-structured, clear, and easy to understand? Are they explaining terms well?
    3. Confidence (0-100): Judging from the text, does the candidate sound assertive and authoritative, or hesitant and unsure?
    4. Feedback: Provide a concise (2-3 sentences), highly specific critique. Point out exactly what was good and what was missing or incorrect based on the question. Do not be overly polite; be direct, constructive, and strict.
    5. Ideal Answer: Provide a concise ideal answer to the question based on the candidate's context (if applicable) or general best practices.
    
    Return STRICTLY a JSON object, do not use markdown format blocks.
    Format required:
    {{
        "confidence": 85,
        "communication": 90,
        "technical": 80,
        "feedback": "Your explanation of React Hooks was solid, but you missed answering the second part of the question regarding state management.",
        "ideal_answer": "React Hooks allow state and lifecycle features in functional components. For state management across the app, Context API or Redux can be used."
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
        "feedback": "Evaluation failed. Please try again.",
        "ideal_answer": "N/A"
    }
