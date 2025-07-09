import logging
from typing import Optional, Dict, Any, List
import requests
import json

from ..models.types import (
    ContentAssessment, 
    GraderRequest, 
    GraderResponse,
    OverallFeedbackRequest,
    OverallFeedbackResponse
)


logger = logging.getLogger(__name__)


class OllamaGraderService:
    """Ollama-based content grading service using phi4 model"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "phi4"
        
    async def score_answer(
        self, 
        answer: str, 
        question: Optional[Dict[str, Any]] = None
    ) -> GraderResponse:
        """
        Score a student's answer using OpenAI
        
        Args:
            answer: The student's answer text
            question: Optional question context with text and possibly image
            
        Returns:
            GraderResponse with scores and feedback
        """
        try:
            # Build the prompt based on question type
            if question and question.get("image"):
                prompt = self._build_image_assessment_prompt(answer, question)
            else:
                prompt = self._build_text_assessment_prompt(answer, question)
            
            # Call Ollama API
            response = await self._call_ollama(
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse the response
            result = self._parse_grading_response(response)
            
            logger.info(f"Successfully scored answer with overall grade: {result.grade}")
            return result
            
        except Exception as e:
            logger.error(f"Error scoring answer: {str(e)}")
            return self._create_default_response(str(e))
    
    async def generate_overall_feedback(
        self, 
        questions: List[str],
        responses: List[str],
        individual_feedbacks: List[str],
        scores: Dict[str, Dict[str, float]]
    ) -> OverallFeedbackResponse:
        """
        Generate comprehensive overall feedback
        
        Args:
            questions: List of question texts
            responses: List of student responses
            individual_feedbacks: List of individual feedback for each response
            scores: Average scores for speech and content
            
        Returns:
            OverallFeedbackResponse with comprehensive feedback
        """
        try:
            prompt = self._build_overall_feedback_prompt(
                questions, responses, individual_feedbacks, scores
            )
            
            response = await self._call_ollama(
                messages=[
                    {"role": "system", "content": self._get_overall_feedback_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            feedback = response.strip()
            
            logger.info("Successfully generated overall feedback")
            return OverallFeedbackResponse(feedback=feedback)
            
        except Exception as e:
            logger.error(f"Error generating overall feedback: {str(e)}")
            return OverallFeedbackResponse(
                feedback="Sorry, we encountered an error generating your overall feedback. Please try again."
            )
    
    async def _call_ollama(
        self,
        messages: List[Dict[str, str]], 
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> str:
        """Make API call to Ollama"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise Exception(f"Ollama API error: {str(e)}")
        except KeyError as e:
            logger.error(f"Unexpected Ollama response format: {str(e)}")
            raise Exception(f"Invalid Ollama response format: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama call: {str(e)}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for answer grading"""
        return """You are an expert English language instructor specializing in GEPT (General English Proficiency Test) assessment. 
        
Your task is to evaluate student responses based on three criteria:
1. Vocabulary (0-100): Variety, appropriateness, and sophistication of word choice
2. Grammar (0-100): Accuracy of sentence structure, tenses, and language rules
3. Relevance (0-100): How well the response addresses the question or task

Provide scores and constructive feedback that helps students improve their English speaking skills.

IMPORTANT: You must respond with valid JSON only. Do not include any other text outside the JSON structure.

Response format:
{
  "vocabulary": <score 0-100>,
  "grammar": <score 0-100>, 
  "relevance": <score 0-100>,
  "grade": <overall score 0-5>,
  "feedback": "<detailed feedback in English>"
}"""
    
    def _get_overall_feedback_system_prompt(self) -> str:
        """Get system prompt for overall feedback generation"""
        return """You are an expert English language instructor providing comprehensive feedback on a student's English speaking practice session.

Your task is to:
1. Analyze the student's overall performance across multiple questions
2. Identify strengths and areas for improvement
3. Provide specific, actionable suggestions for improvement
4. Maintain an encouraging and supportive tone
5. Reference specific examples from their responses when possible

Focus on both speech quality (pronunciation, fluency, prosody) and content quality (vocabulary, grammar, relevance)."""
    
    def _build_text_assessment_prompt(self, answer: str, question: Optional[Dict[str, Any]]) -> str:
        """Build prompt for text-based question assessment"""
        if question and question.get("text"):
            return f"""Please assess the following student response:

Question: {question["text"]}

Student's Answer: {answer}

Please evaluate based on vocabulary usage, grammar accuracy, and relevance to the question."""
        else:
            return f"""Please assess the following student response:

Student's Answer: {answer}

Please evaluate based on vocabulary usage, grammar accuracy, and overall quality."""
    
    def _build_image_assessment_prompt(self, answer: str, question: Dict[str, Any]) -> str:
        """Build prompt for image-based question assessment"""
        return f"""Please assess the following student response for an image description task:

Question: {question.get("text", "Describe what you see in the image")}

Student's Answer: {answer}

Note: This is an image description task. Please evaluate:
- Vocabulary: Variety and appropriateness of descriptive words
- Grammar: Sentence structure and accuracy
- Relevance: How well the response describes visual elements (even though you cannot see the image)"""
    
    def _build_overall_feedback_prompt(
        self, 
        questions: List[str], 
        responses: List[str], 
        individual_feedbacks: List[str],
        scores: Dict[str, Dict[str, float]]
    ) -> str:
        """Build prompt for overall feedback generation"""
        session_data = []
        for i, (q, r, f) in enumerate(zip(questions, responses, individual_feedbacks)):
            session_data.append(f"Question {i+1}: {q}")
            session_data.append(f"Response {i+1}: {r}")
            session_data.append(f"Individual Feedback {i+1}: {f}")
            session_data.append("")
        
        return f"""Please provide comprehensive overall feedback for this English speaking practice session:

{chr(10).join(session_data)}

Overall Scores:
Speech Quality:
- Accuracy: {scores.get('speech', {}).get('accuracy', 0)}/100
- Fluency: {scores.get('speech', {}).get('fluency', 0)}/100  
- Prosody: {scores.get('speech', {}).get('prosody', 0)}/100

Content Quality:
- Vocabulary: {scores.get('content', {}).get('vocabulary', 0)}/100
- Grammar: {scores.get('content', {}).get('grammar', 0)}/100
- Relevance: {scores.get('content', {}).get('relevance', 0)}/100

Please provide encouraging, specific, and actionable feedback to help the student improve their English speaking skills."""
    
    def _parse_grading_response(self, response_text: str) -> GraderResponse:
        """Parse OpenAI response into GraderResponse"""
        try:
            import json
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                data = json.loads(response_text)
                return GraderResponse(
                    vocabulary=float(data.get('vocabulary', 0)),
                    grammar=float(data.get('grammar', 0)),
                    relevance=float(data.get('relevance', 0)),
                    grade=float(data.get('grade', 0)),
                    feedback=data.get('feedback', 'No feedback provided')
                )
            else:
                # Fallback: try to extract scores from text
                return self._extract_scores_from_text(response_text)
                
        except Exception as e:
            logger.warning(f"Could not parse grading response: {str(e)}")
            return self._create_default_response("Could not parse assessment")
    
    def _extract_scores_from_text(self, text: str) -> GraderResponse:
        """Extract scores from unstructured text response"""
        # Simple extraction - in production, this would be more sophisticated
        vocabulary = 70.0  # Default scores
        grammar = 70.0
        relevance = 70.0
        grade = 3.5
        
        return GraderResponse(
            vocabulary=vocabulary,
            grammar=grammar,
            relevance=relevance,
            grade=grade,
            feedback=text
        )
    
    def _create_default_response(self, error_message: str) -> GraderResponse:
        """Create default response when grading fails"""
        return GraderResponse(
            vocabulary=0.0,
            grammar=0.0,
            relevance=0.0,
            grade=0.0,
            feedback=f"Sorry, we encountered an error assessing your response: {error_message}"
        )