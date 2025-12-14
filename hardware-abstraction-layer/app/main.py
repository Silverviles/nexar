from fastapi import FastAPI
from app.api.routes import router
from app.services.factory import quantum_service

app = FastAPI(
    title="Hardware Abstraction Layer for Quantum Computing",
    version="1.0.0",
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/quantum/providers")
def list_quantum_providers():
    return {"providers": quantum_service.list_providers()}
