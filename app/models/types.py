from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class QuestionType(str, Enum):
    QUESTION_ANSWERING = "question-answering"
    IMAGE_DESCRIPTION = "image-description"


class Question(BaseModel):
    id: str
    text: str
    type: QuestionType
    difficulty: str = "intermediate"


class ImageQuestion(Question):
    image_url: str
    type: QuestionType = QuestionType.IMAGE_DESCRIPTION


class SpeechAssessment(BaseModel):
    """Speech assessment scores from Azure Speech Services"""
    accuracy: float = Field(ge=0, le=100, description="Pronunciation accuracy (0-100)")
    fluency: float = Field(ge=0, le=100, description="Speech fluency (0-100)")
    prosody: float = Field(ge=0, le=100, description="Prosody score (0-100)")
    total: float = Field(ge=0, le=5, description="Total speech score (0-5)")
    detail_result: Optional[Dict[str, Any]] = Field(None, description="Raw Azure result")


class ContentAssessment(BaseModel):
    """Content assessment scores from OpenAI"""
    vocabulary: float = Field(ge=0, le=100, description="Vocabulary usage (0-100)")
    grammar: float = Field(ge=0, le=100, description="Grammar accuracy (0-100)")
    relevance: float = Field(ge=0, le=100, description="Content relevance (0-100)")
    total: float = Field(ge=0, le=5, description="Total content score (0-5)")


class AssessmentResult(BaseModel):
    """Complete assessment result"""
    speech: SpeechAssessment
    content: ContentAssessment
    overall_score: float = Field(ge=0, le=100, description="Overall score (0-100)")
    feedback: str = Field(description="Detailed feedback text")


class GraderRequest(BaseModel):
    """Request for content grading"""
    answer: str = Field(description="Student's answer text")
    question: Optional[Dict[str, Any]] = Field(None, description="Question context")


class GraderResponse(BaseModel):
    """Response from content grading service"""
    vocabulary: float = Field(ge=0, le=100)
    grammar: float = Field(ge=0, le=100)
    relevance: float = Field(ge=0, le=100)
    grade: float = Field(ge=0, le=5)
    feedback: str


class OverallFeedbackRequest(BaseModel):
    """Request for overall feedback generation"""
    questions: List[str] = Field(description="List of question texts")
    responses: List[str] = Field(description="List of student responses")
    individual_feedbacks: List[str] = Field(description="Individual feedback for each response")
    scores: Dict[str, Dict[str, float]] = Field(description="Average scores for speech and content")


class OverallFeedbackResponse(BaseModel):
    """Response from overall feedback generation"""
    feedback: str = Field(description="Overall feedback text")


class Message(BaseModel):
    """Chat message with assessment data"""
    name: str
    content: str
    self: bool = False
    audio: Optional[str] = None
    avatar: Optional[str] = None
    score: Optional[float] = None
    result: Optional[AssessmentResult] = None
    ignore: bool = False
    hidden: bool = False


class SpeechCredentials(BaseModel):
    """Azure Speech Service credentials"""
    subscription_key: str
    region: str
    token: Optional[str] = None