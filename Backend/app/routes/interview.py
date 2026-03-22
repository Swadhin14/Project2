from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_questions, evaluate_answer

router = APIRouter()

class GenerateRequest(BaseModel):
    resume_text: str

class EvaluateRequest(BaseModel):
    question: str
    answer: str

@router.post("/interview/generate")
def api_generate_questions(req: GenerateRequest):
    questions = generate_questions(req.resume_text)
    return {"questions": questions}

@router.post("/interview/evaluate")
def api_evaluate_answer(req: EvaluateRequest):
    eval_data = evaluate_answer(req.question, req.answer)
    return eval_data