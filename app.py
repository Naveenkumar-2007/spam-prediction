from flask import Flask, request, render_template, jsonify
import pandas as pd
import logging
import traceback
import os
import sys

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set TensorFlow logging level
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    from src.pipeline.predict_pipeline import predict, customdata
    logger.info("✅ Successfully imported prediction pipeline")
except ImportError as e:
    logger.error(f"❌ Failed to import prediction pipeline: {e}")
    # Create dummy classes for testing
    class predict:
        def get_predict(self, data):
            return "Legitimate", 0.5
    
    class customdata:
        def __init__(self, message_text):
            self.message_text = message_text
        def data_frame(self):
            import pandas as pd
            return pd.DataFrame({"text": [self.message_text]})

application = Flask(__name__)
app = application

# Add error handling for 500 errors
@app.errorhandler(500)
def handle_500(error):
    logger.error(f"Internal Server Error: {error}")
    return render_template('home.html', 
                         results="❌ Internal Server Error. Please try again.", 
                         confidence=None), 500

@app.errorhandler(Exception)
def handle_exception(error):
    # Don't log 404 errors as server errors
    if hasattr(error, 'code') and error.code == 404:
        return str(error), 404
        
    logger.error(f"Unhandled exception: {error}")
    logger.error(traceback.format_exc())
    return render_template('home.html', 
                         results="❌ An error occurred. Please try again.", 
                         confidence=None), 500

@app.route('/')
def index():
    """Home page"""
    return render_template('h.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to prevent 404 errors"""
    from flask import Response
    return Response(status=204)  # No content

@app.route('/health')
def health_check():
    """Health check endpoint for deployment debugging"""
    try:
        import tensorflow as tf
        import pandas as pd
        import numpy as np
        
        health_status = {
            "status": "healthy",
            "tensorflow_version": tf.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "model_file_exists": os.path.exists("artifacts/best_model.h5"),
            "preprocessing_file_exists": os.path.exists("artifacts/preprocessing.pkl")
        }
        
        # Test model loading
        try:
            test_pipeline = predict()
            test_pipeline.load_model()
            health_status["model_loading"] = "success"
        except Exception as e:
            health_status["model_loading"] = f"failed: {str(e)}"
            health_status["status"] = "unhealthy"
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/predict', methods=['GET','POST'])
def predict_spam():
    """
    SMS/Email Spam Detection route
    
    Connection Flow:
    1. Receives: Message text from HTML form
    2. Creates: customdata object
    3. Calls: predict.get_predict() with TensorFlow LSTM
    4. Returns: Spam/Legitimate prediction
    """
    try:
        if request.method == "GET":
            return render_template('home.html', results=None, confidence=None)
        
        else:
            # Get message from form
            message_text = request.form.get('email_text')
            
            if not message_text or message_text.strip() == "":
                logger.warning("Empty message text received")
                return render_template('home.html', 
                                     results="⚠️ Please enter message text", 
                                     confidence=None)
            
            # Log the input
            logger.info(f"📧 Processing message: {message_text[:100]}...")
            
            # Create prediction object
            data = customdata(message_text=message_text.strip())
            data_df = data.data_frame()
            
            print("\n" + "="*70)
            print("📧 Message Input:")
            print(message_text[:200])
            print("="*70)
            
            # Get prediction
            predict_pipeline = predict()
            prediction, confidence = predict_pipeline.get_predict(data_df)
            
            # Validate prediction results
            if prediction not in ["Spam", "Legitimate"]:
                raise ValueError(f"Invalid prediction result: {prediction}")
            
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                raise ValueError(f"Invalid confidence value: {confidence}")
            
            # Format results
            if prediction == "Spam":
                final_result = "🚨 SPAM DETECTED!"
                result_class = "spam"
            else:
                final_result = "✅ Legitimate Message"
                result_class = "legitimate"
            
            confidence_percent = confidence * 100
            
            logger.info(f"✅ Prediction successful: {final_result} ({confidence_percent:.1f}% confident)")
            print(f"\n🎯 Prediction: {final_result} ({confidence_percent:.1f}% confident)\n")
            
            return render_template('home.html', 
                                 results=final_result, 
                                 confidence=confidence,
                                 result_class=result_class,
                                 email_preview=message_text[:200])
                                 
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in predict_spam: {error_msg}")
        logger.error(traceback.format_exc())
        
        # More specific error messages for debugging
        if "No module named" in error_msg:
            user_error = "❌ Missing dependencies. Please check server configuration."
        elif "Model file not found" in error_msg:
            user_error = "❌ Model files not found. Please check deployment."
        elif "Memory" in error_msg or "ResourceExhausted" in error_msg:
            user_error = "❌ Server memory limit exceeded. Please try again."
        elif "tensorflow" in error_msg.lower():
            user_error = "❌ TensorFlow loading error. Please try again in a moment."
        else:
            user_error = f"❌ Error: {error_msg[:100]}..." if len(error_msg) > 100 else f"❌ Error: {error_msg}"
        
        return render_template('home.html', 
                             results=user_error, 
                             confidence=None)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)