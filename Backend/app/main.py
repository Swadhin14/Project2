from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import threading
from contextlib import asynccontextmanager

from app.routes import upload, session, interview, dashboard
from app.services.vector_store import get_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start pre-loading the embedding model in a background thread so the server
    # starts instantly but the model is ready by the time the user uploads a resume.
    def preload_model():
        try:
            get_model()
        except Exception as e:
            print("Background model preload failed:", e)
            
    threading.Thread(target=preload_model, daemon=True).start()
    yield

app = FastAPI(title="Hirable AI Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

# Mount frontend directory to serve the vanilla frontend files under root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend1")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")