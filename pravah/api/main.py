from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from pravah.engine.causal_engine import process_report
from pravah.database.queries import update_review_status

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="PRAVAH API", description="Causal Risk Intelligence Engine API")

class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    causal_nodes: Dict[str, Any]
    sif_potential: str
    sif_score: float
    lsr_mapped: str
    confidence: float
    evidence: List[str]

class FeedbackRequest(BaseModel):
    report_id: str
    reviewer_name: str
    action: str
    notes: Optional[str] = ""

class HealthResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyzes a report text and returns causal nodes, SIF metrics, and LSR mapping.
    """
    try:
        logger.info("Received analysis request for a report.")
        result = process_report(request.text)
        return AnalyzeResponse(**result)
    except Exception as e:
        logger.error(f"Error processing report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing the report")

@app.post("/submit-feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submits expert feedback for a given report, updating its status.
    """
    try:
        logger.info(f"Submitting feedback for report_id: {request.report_id}")
        success = update_review_status(
            report_id=request.report_id,
            new_status=request.action,
            reviewer_name=request.reviewer_name,
            notes=request.notes
        )
        if success:
            return {"status": "success", "message": "Feedback submitted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to submit feedback")
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while submitting feedback")
