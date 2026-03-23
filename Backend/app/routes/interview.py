from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_questions, evaluate_answer
from app.services.vector_store import retrieve_relevant_chunks

router = APIRouter()

class GenerateRequest(BaseModel):
    filename: str

class EvaluateRequest(BaseModel):
    filename: str
    question: str
    answer: str

@router.post("/interview/generate")
def api_generate_questions(req: GenerateRequest):
    # Retrieve top chunks regarding skills and experience for questioning
    chunks = retrieve_relevant_chunks(req.filename, "technical skills work experience projects", top_k=5)
    context = "\n".join([c["text"] for c in chunks])
    
    questions = generate_questions(context)
    return {"questions": questions}

@router.post("/interview/evaluate")
def api_evaluate_answer(req: EvaluateRequest):
    # Retrieve top chunks relevant to the question and answer
    query = f"{req.question} {req.answer}"
    chunks = retrieve_relevant_chunks(req.filename, query, top_k=3)
    context = "\n".join([c["text"] for c in chunks])
    
    eval_data = evaluate_answer(req.question, req.answer, context)
    return eval_data