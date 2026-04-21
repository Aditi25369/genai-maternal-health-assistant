from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import chat, risk, reminders, dashboard
import os

app = FastAPI(
    title="Amma AI",
    description="Multilingual maternal health companion powered by Gemini AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(risk.router, prefix="/api", tags=["Risk"])
app.include_router(reminders.router, prefix="/api", tags=["Reminders"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/health")
def health_check():
    return {"status": "Amma AI is running", "version": "1.0.0"}