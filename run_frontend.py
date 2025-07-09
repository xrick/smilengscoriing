#!/usr/bin/env python3
"""
Run the Streamlit frontend application
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # Change to the frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
    # Run Streamlit app
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        os.path.join(frontend_dir, "streamlit_app.py"),
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])