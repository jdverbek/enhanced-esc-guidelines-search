"""
Enhanced ESC Guidelines Search System
Main entry point for the application - Render.com compatible
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the simplified application
from app import app

# For Render.com deployment compatibility
application = app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Enhanced ESC Guidelines Search System on {host}:{port}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        workers=1,  # Single worker for Render's free tier
        access_log=True,
        log_level="info"
    )
