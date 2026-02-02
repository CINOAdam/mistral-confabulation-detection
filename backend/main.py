"""FastAPI application for Mistral activation capture."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app: FastAPI = FastAPI(
    title="Mistral Reproducibility API",
    description="Activation capture and analysis for Mistral-22B",
    version="0.1.0"
)

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to needed methods
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model": settings.model_name,
        "device": settings.device,
        "sae_release": settings.sae_release
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True
    )
