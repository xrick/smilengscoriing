import streamlit as st
import requests
import json
from typing import Dict, Any, Optional
import time
import base64
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="英檢口說練習 | Cool English",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000/api"

# Session state initialization
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None
if "practice_history" not in st.session_state:
    st.session_state.practice_history = []


def call_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API call to backend"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {str(e)}")
        st.error(f"API call failed: {str(e)}")
        return {"error": str(e)}


def get_sample_questions() -> Dict[str, list]:
    """Get sample questions for practice"""
    return {
        "question-answering": [
            {
                "id": "qa1",
                "text": "What is your favorite hobby and why do you enjoy it?",
                "type": "question-answering",
                "difficulty": "intermediate"
            },
            {
                "id": "qa2", 
                "text": "Describe a memorable trip you have taken. Where did you go and what made it special?",
                "type": "question-answering",
                "difficulty": "intermediate"
            },
            {
                "id": "qa3",
                "text": "What are the advantages and disadvantages of social media?",
                "type": "question-answering",
                "difficulty": "advanced"
            }
        ],
        "image-description": [
            {
                "id": "img1",
                "text": "Describe what you see in this image in detail.",
                "type": "image-description",
                "difficulty": "intermediate",
                "image_url": "https://example.com/sample1.jpg"
            },
            {
                "id": "img2",
                "text": "Look at this picture and describe the scene, including the people, objects, and activities.",
                "type": "image-description", 
                "difficulty": "intermediate",
                "image_url": "https://example.com/sample2.jpg"
            }
        ]
    }


def display_question(question: Dict[str, Any]):
    """Display the current question"""
    st.subheader("📝 Question")
    
    # Display question text
    st.write(f"**{question['text']}**")
    
    # Display image if it's an image description question
    if question.get("image_url"):
        st.info("🖼️ Image Description Task")
        st.write("*Note: In a real implementation, the image would be displayed here.*")
    
    # Display difficulty level
    difficulty_color = {
        "beginner": "🟢",
        "intermediate": "🟡", 
        "advanced": "🔴"
    }
    st.write(f"Difficulty: {difficulty_color.get(question['difficulty'], '⚪')} {question['difficulty'].title()}")


def display_assessment_result(result: Dict[str, Any]):
    """Display assessment results"""
    st.subheader("📊 Assessment Result")
    
    # Overall score
    overall_score = result.get("overall_score", 0)
    st.metric("Overall Score", f"{overall_score}/100")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Content Assessment**")
        content = result.get("content", {})
        st.write(f"• Vocabulary: {content.get('vocabulary', 0)}/100")
        st.write(f"• Grammar: {content.get('grammar', 0)}/100")
        st.write(f"• Relevance: {content.get('relevance', 0)}/100")
        st.write(f"• Total: {content.get('total', 0)}/5")
    
    with col2:
        st.write("**Speech Assessment**")
        speech = result.get("speech", {})
        st.write(f"• Accuracy: {speech.get('accuracy', 0)}/100")
        st.write(f"• Fluency: {speech.get('fluency', 0)}/100")
        st.write(f"• Prosody: {speech.get('prosody', 0)}/100")
        st.write(f"• Total: {speech.get('total', 0)}/5")
    
    # Feedback
    if result.get("feedback"):
        st.write("**Feedback**")
        st.write(result["feedback"])


def main():
    """Main application"""
    st.title("🎤 英檢口說練習 by Cool English")
    st.markdown("透過 AI 輔助練習，即時獲得發音與表達評分，全面提升英語口說能力！")
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Choose Practice Mode",
        ["Home", "Question Answering", "Image Description", "Practice History"]
    )
    
    if page == "Home":
        display_home_page()
    elif page == "Question Answering":
        display_practice_page("question-answering")
    elif page == "Image Description":
        display_practice_page("image-description")
    elif page == "Practice History":
        display_history_page()


def display_home_page():
    """Display home page"""
    st.header("🎯 Practice Modes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🗣️ Question Answering")
        st.write("Practice answering English questions to improve your speaking skills.")
        st.write("**Features:**")
        st.write("• Various question types and difficulty levels")
        st.write("• Real-time pronunciation assessment")
        st.write("• Content quality evaluation")
        st.write("• Personalized feedback")
        
        if st.button("Start Question Practice", key="qa_start"):
            st.session_state.current_question = None
            st.sidebar.selectbox("Choose Practice Mode", ["Question Answering"], key="nav_qa")
            st.rerun()
    
    with col2:
        st.subheader("🖼️ Image Description")
        st.write("Practice describing images to enhance your descriptive skills.")
        st.write("**Features:**")
        st.write("• Various image types and scenarios")
        st.write("• Detailed description evaluation")
        st.write("• Vocabulary and grammar assessment")
        st.write("• Structured feedback")
        
        if st.button("Start Image Practice", key="img_start"):
            st.session_state.current_question = None
            st.sidebar.selectbox("Choose Practice Mode", ["Image Description"], key="nav_img")
            st.rerun()


def display_practice_page(practice_type: str):
    """Display practice page for specific type"""
    st.header(f"🎯 {practice_type.replace('-', ' ').title()} Practice")
    
    # Get sample questions
    questions = get_sample_questions()[practice_type]
    
    # Question selection
    st.subheader("Select a Question")
    question_options = [f"Q{i+1}: {q['text'][:50]}..." for i, q in enumerate(questions)]
    selected_idx = st.selectbox(
        "Choose a question:",
        range(len(questions)),
        format_func=lambda x: question_options[x]
    )
    
    current_question = questions[selected_idx]
    
    # Display question
    display_question(current_question)
    
    # Audio recording section
    st.subheader("🎤 Record Your Answer")
    
    # Text input for answer (since we can't record audio in Streamlit easily)
    user_answer = st.text_area(
        "Type your answer here (in a real app, this would be voice recording):",
        height=100,
        placeholder="Start typing your answer..."
    )
    
    # Submit button
    if st.button("Submit Answer", disabled=not user_answer.strip()):
        if user_answer.strip():
            # Show loading spinner
            with st.spinner("Assessing your answer..."):
                # Simulate API call for grading
                result = score_answer(user_answer, current_question)
                
                if result and "error" not in result:
                    # Display results
                    display_assessment_result(result)
                    
                    # Add to history
                    st.session_state.practice_history.append({
                        "question": current_question["text"],
                        "answer": user_answer,
                        "result": result,
                        "timestamp": time.time()
                    })
                    
                    st.success("✅ Assessment completed!")
                else:
                    st.error("❌ Failed to assess your answer. Please try again.")


def display_history_page():
    """Display practice history"""
    st.header("📈 Practice History")
    
    if not st.session_state.practice_history:
        st.info("No practice history yet. Start practicing to see your progress!")
        return
    
    # Display history items
    for i, item in enumerate(reversed(st.session_state.practice_history)):
        with st.expander(f"Practice {len(st.session_state.practice_history) - i}: {item['question'][:50]}..."):
            st.write(f"**Question:** {item['question']}")
            st.write(f"**Your Answer:** {item['answer']}")
            st.write(f"**Timestamp:** {time.ctime(item['timestamp'])}")
            
            if item.get("result"):
                display_assessment_result(item["result"])
    
    # Clear history button
    if st.button("Clear History"):
        st.session_state.practice_history = []
        st.rerun()


def score_answer(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Score answer using API"""
    try:
        # Prepare request data
        request_data = {
            "answer": answer,
            "question": {
                "text": question["text"],
                "image": question.get("image_url")
            }
        }
        
        # Call API
        result = call_api("grader/score-answer", method="POST", data=request_data)
        
        if "error" in result:
            return result
        
        # Transform API response to match expected format
        return {
            "content": {
                "vocabulary": result.get("vocabulary", 0),
                "grammar": result.get("grammar", 0),
                "relevance": result.get("relevance", 0),
                "total": result.get("grade", 0)
            },
            "speech": {
                "accuracy": 85,  # Mock values since we don't have actual audio
                "fluency": 80,
                "prosody": 78,
                "total": 4.0
            },
            "overall_score": (result.get("grade", 0) * 10 + 80) / 2,  # Combine content and speech
            "feedback": result.get("feedback", "No feedback available")
        }
        
    except Exception as e:
        logger.error(f"Error scoring answer: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    main()