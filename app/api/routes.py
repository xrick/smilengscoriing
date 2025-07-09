import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse

from ..models.types import (
    GraderRequest, 
    GraderResponse,
    OverallFeedbackRequest,
    OverallFeedbackResponse,
    SpeechCredentials
)
from ..services import AzureSpeechService, OpenAIGraderService
from ..utils.config import get_settings


logger = logging.getLogger(__name__)
router = APIRouter()


# Initialize services
settings = get_settings()
azure_speech_service = AzureSpeechService(
    subscription_key=settings.azure_speech_key,
    region=settings.azure_speech_region
)
openai_grader_service = OpenAIGraderService(api_key=settings.openai_api_key)


@router.post("/grader/score-answer", response_model=GraderResponse)
async def score_answer(request: GraderRequest) -> GraderResponse:
    """
    Score a student's answer using OpenAI content assessment
    """
    try:
        logger.info(f"Scoring answer: {request.answer[:100]}...")
        
        result = await openai_grader_service.score_answer(
            answer=request.answer,
            question=request.question
        )
        
        logger.info(f"Answer scored successfully with grade: {result.grade}")
        return result
        
    except Exception as e:
        logger.error(f"Error scoring answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grader/overall-feedback", response_model=OverallFeedbackResponse)
async def generate_overall_feedback(request: OverallFeedbackRequest) -> OverallFeedbackResponse:
    """
    Generate comprehensive overall feedback for a practice session
    """
    try:
        logger.info(f"Generating overall feedback for {len(request.questions)} questions")
        
        result = await openai_grader_service.generate_overall_feedback(
            questions=request.questions,
            responses=request.responses,
            individual_feedbacks=request.individual_feedbacks,
            scores=request.scores
        )
        
        logger.info("Overall feedback generated successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error generating overall feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/speech/credentials", response_model=SpeechCredentials)
async def get_speech_credentials() -> SpeechCredentials:
    """
    Get Azure Speech Service credentials for client-side use
    """
    try:
        credentials = azure_speech_service.get_credentials()
        logger.info("Speech credentials provided successfully")
        return credentials
        
    except Exception as e:
        logger.error(f"Error getting speech credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speech/assess-pronunciation")
async def assess_pronunciation(
    audio: UploadFile = File(...),
    reference_text: str = Form(...),
    language: str = Form(default="en-US")
) -> Dict[str, Any]:
    """
    Assess pronunciation using Azure Speech Services
    """
    try:
        logger.info(f"Assessing pronunciation for text: {reference_text}")
        
        # Read audio data
        audio_data = await audio.read()
        
        # Perform pronunciation assessment
        result = await azure_speech_service.assess_pronunciation(
            audio_data=audio_data,
            reference_text=reference_text,
            language=language
        )
        
        logger.info(f"Pronunciation assessed successfully with total score: {result.total}")
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error assessing pronunciation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "english-speaking-practice"}


@router.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint
    """
    return {"message": "English Speaking Practice API", "version": "1.0.0"}