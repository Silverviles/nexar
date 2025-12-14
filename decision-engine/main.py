from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

# Add the parent directory to the Python path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try relative imports first (when used as a module)
    from .config import get_settings
    from .routes import decision_engine
except ImportError:
    # Fall back to absolute imports (when run as a script)
    from config import get_settings
    from routes import decision_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Decision Engine for Quantum-Classical Code Router",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(decision_engine.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📊 Model path: {settings.MODEL_PATH}")
    logger.info(f"📏 Scaler path: {settings.SCALER_PATH}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("👋 Shutting down Decision Engine")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Quantum-Classical Decision Engine API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/decision-engine/health"
    }

@app.get("/health")
async def health():
    """General health check"""
    return {"status": "healthy", "service": "Decision Engine"}