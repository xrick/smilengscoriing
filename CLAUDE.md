# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an English speaking practice application called "smilengscoriing" that uses AI to assess English pronunciation and content quality. The application consists of:

- **Backend API** (FastAPI): Handles OpenAI content grading and Azure Speech Services integration
- **Frontend** (Streamlit): Web interface for practicing English speaking skills

## Architecture

The codebase follows a clean architecture pattern:

```
app/
├── api/routes.py          # FastAPI route handlers
├── models/types.py        # Pydantic models and types
├── services/
│   ├── azure_speech.py    # Azure Speech Services integration
│   └── openai_grader.py   # OpenAI content assessment
├── utils/config.py        # Configuration management
└── main.py               # FastAPI application setup

frontend/
└── streamlit_app.py      # Streamlit web interface
```

## Key Services

### Ollama Grader Service (`app/services/openai_grader.py`)
- Handles content assessment using Ollama with phi4 model
- Evaluates vocabulary, grammar, and relevance (0-100 scale)
- Provides detailed feedback to students
- Supports both text and image-based questions

### Azure Speech Service (`app/services/azure_speech.py`)
- Integrates with Azure Cognitive Services Speech
- Provides pronunciation assessment (accuracy, fluency, prosody)
- Returns detailed phoneme-level analysis
- Supports client-side credential provisioning

## Development Commands

### Running the Application

```bash
# Start the API server
python run_api.py
# or
python -m app.main

# Start the Streamlit frontend
python run_frontend.py
# or
streamlit run frontend/streamlit_app.py
```

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# For development with additional tools
pip install -e ".[dev]"
```

### Testing and Code Quality

```bash
# Run tests
pytest

# Code formatting
black . --line-length 100

# Type checking
mypy app/

# Linting
flake8 app/
```

## Environment Configuration

The application requires these environment variables:

```bash
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
OLLAMA_URL=http://localhost:11434
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

Create a `.env` file in the project root with these values.

## API Endpoints

- `POST /api/grader/score-answer` - Score student answers using Ollama
- `POST /api/grader/overall-feedback` - Generate comprehensive session feedback
- `GET /api/speech/credentials` - Get Azure Speech Service credentials
- `POST /api/speech/assess-pronunciation` - Assess pronunciation with audio upload
- `GET /api/health` - Health check endpoint

## Data Models

Key models defined in `app/models/types.py`:

- `GraderRequest/Response` - Content assessment requests/responses
- `SpeechAssessment` - Speech evaluation results
- `ContentAssessment` - Content evaluation results
- `AssessmentResult` - Combined assessment results
- `Question/ImageQuestion` - Question types for practice

## Common Development Patterns

### Adding New Assessment Features
1. Define new Pydantic models in `app/models/types.py`
2. Add service logic in appropriate service class
3. Create API endpoints in `app/api/routes.py`
4. Update frontend interface in `frontend/streamlit_app.py`

### Error Handling
- Services use try/catch with logging and fallback responses
- API endpoints return appropriate HTTP status codes
- Frontend shows user-friendly error messages

## Ollama Setup

Before running the application, ensure Ollama is installed and running with the phi4 model:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the phi4 model
ollama pull phi4

# Start Ollama server (runs on localhost:11434 by default)
ollama serve
```

The application will connect to Ollama at `http://localhost:11434` by default. You can configure this via the `OLLAMA_URL` environment variable.

## Testing Approach

The project uses pytest for testing with async support. When running tests:
- Use `pytest` for all tests
- Use `pytest-asyncio` for async test functions
- Mock external API calls (Ollama, Azure) in tests