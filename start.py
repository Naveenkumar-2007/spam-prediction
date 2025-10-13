#!/usr/bin/env python3
"""
Startup script for Render deployment with better error handling
"""
import os
import sys
import logging

# Configure logging for deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required files and dependencies are available"""
    logger.info("🔍 Checking deployment environment...")
    
    # Check Python version
    python_version = sys.version
    logger.info(f"Python version: {python_version}")
    
    # Check required files
    required_files = [
        "artifacts/best_model.h5",
        "artifacts/preprocessing.pkl",
        "templates/home.html",
        "templates/h.html",
        "src/pipeline/predict_pipeline.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            logger.info(f"✅ Found: {file_path}")
    
    if missing_files:
        logger.error(f"❌ Missing files: {missing_files}")
        return False
    
    # Check dependencies
    try:
        import tensorflow as tf
        import pandas as pd
        import numpy as np
        import flask
        
        logger.info(f"✅ TensorFlow: {tf.__version__}")
        logger.info(f"✅ Pandas: {pd.__version__}")
        logger.info(f"✅ NumPy: {np.__version__}")
        logger.info(f"✅ Flask: {flask.__version__}")
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False
    
    logger.info("✅ Environment check passed!")
    return True

if __name__ == "__main__":
    logger.info("🚀 Starting Spam Detection App...")
    
    if check_environment():
        logger.info("✅ Environment OK, starting Flask app...")
        from app import app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.error("❌ Environment check failed!")
        sys.exit(1)