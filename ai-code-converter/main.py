from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.api import router as api_router

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Python-to-Quantum API",
        description="Convert Python code to quantum circuits using AI",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(api_router)
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Python-to-Quantum API",
            "endpoints": {
                "/api/translate": "POST - Translate Python to quantum code",
                "/api/execute": "POST - Execute quantum circuit",
                "/api/extract-logic": "POST - Extract logic function",
                "/api/health": "GET - Health check"
            }
        }
    
    return app

app = create_app()