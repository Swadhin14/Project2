from fastapi import APIRouter

router = APIRouter()

@router.get("/session/test")
def session_test():
    return {"message": "Session route working"}