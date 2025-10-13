#!/usr/bin/env python3
"""
Startup script for Render deployment
Downloads required NLTK data and starts the app
"""
import os
import sys

def setup_nltk():
    """Download required NLTK data"""
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully")
    except Exception as e:
        print(f"⚠️ NLTK setup warning: {e}")

def main():
    """Main startup function"""
    print("🚀 Starting spam prediction app...")
    
    # Setup NLTK data
    setup_nltk()
    
    # Import and run the app
    from app import app
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()