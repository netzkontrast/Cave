#!/usr/bin/env python3
"""
Run the Cave backend server
"""
import uvicorn
from backend.main import app

def main():
    """Main entry point for the Cave application."""
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 