from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import router as api_router

app = FastAPI(
    title="Intelligent Candidate Discovery Platform",
    description="AI-powered API for parsing, ranking, and discovering candidates.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Intelligent Candidate Discovery Platform API"}
