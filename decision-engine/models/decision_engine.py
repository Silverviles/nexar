from datetime import datetime
from typing import Optional

# If you're using SQLAlchemy for database
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DecisionLog(Base):
    """Database model for logging decisions"""
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Input features
    problem_type = Column(String(50))
    problem_size = Column(Integer)
    qubits_required = Column(Integer)
    circuit_depth = Column(Integer)
    gate_count = Column(Integer)
    cx_gate_ratio = Column(Float)
    superposition_score = Column(Float)
    entanglement_score = Column(Float)
    time_complexity = Column(String(50))
    memory_requirement_mb = Column(Float)
    
    # Prediction results
    recommended_hardware = Column(String(20))
    confidence = Column(Float)
    quantum_probability = Column(Float)
    classical_probability = Column(Float)
    rationale = Column(String(500))
    
    # Execution results (populated after actual execution)
    actual_hardware_used = Column(String(20), nullable=True)
    actual_execution_time_ms = Column(Float, nullable=True)
    actual_cost_usd = Column(Float, nullable=True)
    prediction_correct = Column(Boolean, nullable=True)
    
    # Metadata
    model_version = Column(String(50))
    metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<DecisionLog(id={self.id}, hardware={self.recommended_hardware}, confidence={self.confidence})>"