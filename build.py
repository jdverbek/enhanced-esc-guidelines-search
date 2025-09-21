#!/usr/bin/env python3
"""
Build script for Render.com deployment
Enhanced ESC Guidelines Search System
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    """Main build process"""
    print("🚀 Starting Enhanced ESC Guidelines Search System build process...")
    
    # Create necessary directories
    print("📁 Creating necessary directories...")
    os.makedirs("ESC_Guidelines", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create a sample guideline file if none exist
    guidelines_dir = "ESC_Guidelines"
    if not os.listdir(guidelines_dir):
        print("📄 Creating sample guideline placeholder...")
        with open(os.path.join(guidelines_dir, "README.txt"), "w") as f:
            f.write("""
ESC Guidelines Directory

This directory should contain your ESC guideline PDF files.
The system will automatically process any PDF files placed here.

For testing purposes, you can add sample PDF files or the system
will run with limited functionality until guidelines are added.

Supported formats: PDF
Recommended: ESC cardiovascular guidelines
""")
    
    # Verify Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("⚠️  Warning: Python 3.8+ recommended for optimal performance")
    
    # Check if we're in a deployment environment
    if os.environ.get("RENDER"):
        print("🌐 Render deployment environment detected")
        
        # Set environment variables for production
        os.environ["PYTHONPATH"] = "/opt/render/project/src"
        os.environ["CORS_ORIGINS"] = "*"
        
    print("✅ Build process completed successfully!")
    print("🎯 System is ready for deployment")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
