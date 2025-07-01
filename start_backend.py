#!/usr/bin/env python3
"""
Startup script for the Cave backend
"""
import sys
import os
import uvicorn

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Cave Backend Server...")
    print("📝 Make sure you have:")
    print("   - OpenAI API key in .env file")
    print("   - Database initialized (run: make db-init)")
    print("   - All dependencies installed (run: make install)")
    print()
    
    # Start the server
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 