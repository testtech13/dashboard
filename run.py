#!/usr/bin/env python3
"""
Dashboard Application Runner
Run this script to start the dashboard web interface
"""

import uvicorn
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app import app

if __name__ == "__main__":
    print("Starting Dashboard Web Interface...")
    print("Access the web interface at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
