import logging
import json
from typing import Optional, Dict, Any
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer
from azure.cognitiveservices.speech.audio import AudioConfig

from ..models.types import SpeechAssessment, SpeechCredentials


logger = logging.getLogger(__name__)


class AzureSpeechService:
    """Azure Speech Services integration for pronunciation assessment"""
    
    def __init__(self, subscription_key: str, region: str):
        self.subscription_key = subscription_key
        self.region = region
        self.speech_config = SpeechConfig(subscription=subscription_key, region=region)
        
    def get_credentials(self) -> SpeechCredentials:
        """Get Azure Speech Service credentials for client-side use"""
        return SpeechCredentials(
            subscription_key=self.subscription_key,
            region=self.region
        )
    
    async def assess_pronunciation(
        self, 
        audio_data: bytes, 
        reference_text: str,
        language: str = "en-US"
    ) -> SpeechAssessment:
        """
        Assess pronunciation using Azure Speech Services
        
        Args:
            audio_data: Raw audio data in WAV format
            reference_text: Expected text to compare against
            language: Language code for assessment
            
        Returns:
            SpeechAssessment with scores and detailed results
        """
        try:
            # Configure speech recognition
            self.speech_config.speech_recognition_language = language
            
            # Set up pronunciation assessment config
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_prosody_assessment=True
            )
            
            # Create audio config from bytes
            audio_config = AudioConfig(stream=speechsdk.AudioInputStream(audio_data))
            
            # Create speech recognizer
            recognizer = SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Apply pronunciation assessment config
            pronunciation_config.apply_to(recognizer)
            
            # Perform recognition
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # Parse pronunciation assessment result
                pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
                
                # Convert to our assessment format
                speech_assessment = SpeechAssessment(
                    accuracy=pronunciation_result.accuracy_score,
                    fluency=pronunciation_result.fluency_score,
                    prosody=pronunciation_result.prosody_score,
                    total=self._calculate_total_score(
                        pronunciation_result.accuracy_score,
                        pronunciation_result.fluency_score,
                        pronunciation_result.prosody_score
                    ),
                    detail_result=self._parse_detailed_result(result.properties)
                )
                
                logger.info(f"Pronunciation assessment completed successfully")
                return speech_assessment
                
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized from audio")
                return self._create_default_assessment("No speech recognized")
                
            else:
                logger.error(f"Speech recognition failed: {result.reason}")
                return self._create_default_assessment("Recognition failed")
                
        except Exception as e:
            logger.error(f"Error in pronunciation assessment: {str(e)}")
            return self._create_default_assessment("Assessment error")
    
    def _calculate_total_score(self, accuracy: float, fluency: float, prosody: float) -> float:
        """Calculate total score on 0-5 scale from individual scores"""
        # Weighted average: accuracy 40%, fluency 30%, prosody 30%
        weighted_score = (accuracy * 0.4 + fluency * 0.3 + prosody * 0.3)
        # Convert from 0-100 to 0-5 scale
        return round(weighted_score / 20, 1)
    
    def _parse_detailed_result(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Parse detailed pronunciation assessment result"""
        try:
            # Get the detailed result JSON
            detailed_result = properties.get(
                speechsdk.PropertyId.SpeechServiceResponse_JsonResult
            )
            if detailed_result:
                return json.loads(detailed_result)
            return {}
        except Exception as e:
            logger.warning(f"Could not parse detailed result: {str(e)}")
            return {}
    
    def _create_default_assessment(self, error_message: str) -> SpeechAssessment:
        """Create a default assessment when recognition fails"""
        return SpeechAssessment(
            accuracy=0.0,
            fluency=0.0,
            prosody=0.0,
            total=0.0,
            detail_result={"error": error_message}
        )