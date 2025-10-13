import os
import sys
import logging
from flask import Flask, request, render_template, jsonify
import pandas as pd

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Set environment variables for TensorFlow
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
os.environ.setdefault('TF_ENABLE_ONEDNN_OPTS', '0')

app = Flask(__name__)

# Global variables for model caching
model_cache = {
    'model': None,
    'tokenizer': None,
    'max_length': None,
    'loading': False,
    'error': None
}

def load_model_safely():
    """Safely load model with comprehensive error handling"""
    global model_cache
    
    if model_cache['loading']:
        return False, "Model is currently loading, please wait..."
    
    if model_cache['model'] is not None:
        return True, "Model already loaded"
    
    if model_cache['error']:
        return False, f"Previous loading error: {model_cache['error']}"
    
    model_cache['loading'] = True
    
    try:
        logger.info("🔄 Starting model loading process...")
        
        # Check if files exist
        model_path = "artifacts/best_model.h5"
        preprocessing_path = "artifacts/preprocessing.pkl"
        
        if not os.path.exists(model_path):
            error_msg = f"Model file not found: {model_path}"
            logger.error(f"❌ {error_msg}")
            model_cache['error'] = error_msg
            model_cache['loading'] = False
            return False, error_msg
            
        if not os.path.exists(preprocessing_path):
            error_msg = f"Preprocessing file not found: {preprocessing_path}"
            logger.error(f"❌ {error_msg}")
            model_cache['error'] = error_msg
            model_cache['loading'] = False
            return False, error_msg
        
        logger.info(f"✅ Found model file: {model_path} ({os.path.getsize(model_path)} bytes)")
        logger.info(f"✅ Found preprocessing file: {preprocessing_path} ({os.path.getsize(preprocessing_path)} bytes)")
        
        # Import TensorFlow with error handling
        try:
            import tensorflow as tf
            tf.get_logger().setLevel('ERROR')
            logger.info(f"✅ TensorFlow imported: {tf.__version__}")
        except ImportError as e:
            error_msg = f"TensorFlow import failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            model_cache['error'] = error_msg
            model_cache['loading'] = False
            return False, error_msg
        
        # Load the model
        try:
            logger.info("🔄 Loading TensorFlow model...")
            from tensorflow.keras.models import load_model
            model = load_model(model_path, compile=False)
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            model_cache['model'] = model
            logger.info("✅ Model loaded and compiled successfully")
        except Exception as e:
            error_msg = f"Model loading failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            model_cache['error'] = error_msg
            model_cache['loading'] = False
            return False, error_msg
        
        # Load preprocessing objects
        try:
            logger.info("🔄 Loading preprocessing objects...")
            import joblib
            preprocessing_obj = joblib.load(preprocessing_path)
            
            required_keys = ['tokenizer', 'max_length', 'vocab_size']
            for key in required_keys:
                if key not in preprocessing_obj:
                    raise KeyError(f"Missing key in preprocessing: {key}")
            
            model_cache['tokenizer'] = preprocessing_obj['tokenizer']
            model_cache['max_length'] = preprocessing_obj['max_length']
            
            logger.info(f"✅ Preprocessing loaded (vocab size: {preprocessing_obj['vocab_size']})")
        except Exception as e:
            error_msg = f"Preprocessing loading failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            model_cache['error'] = error_msg
            model_cache['loading'] = False
            return False, error_msg
        
        model_cache['loading'] = False
        logger.info("🎉 Model loading completed successfully!")
        return True, "Model loaded successfully"
        
    except Exception as e:
        error_msg = f"Unexpected error during model loading: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"Full traceback: {str(e.__class__.__name__)}: {str(e)}")
        model_cache['error'] = error_msg
        model_cache['loading'] = False
        return False, error_msg

def predict_message(message_text):
    """Make prediction with loaded model"""
    try:
        # Ensure model is loaded
        success, message = load_model_safely()
        if not success:
            return None, 0.0, message
        
        logger.info(f"🔍 Processing message: {message_text[:100]}...")
        
        # Clean text
        import re
        cleaned_text = str(message_text).lower()
        cleaned_text = re.sub(r'http\S+|www\S+|https\S+', '', cleaned_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r'\S+@\S+', '', cleaned_text)
        cleaned_text = re.sub(r'[^a-zA-Z\s]', '', cleaned_text)
        cleaned_text = ' '.join(cleaned_text.split())
        
        if len(cleaned_text.strip()) == 0:
            logger.warning("Text became empty after cleaning")
            cleaned_text = message_text
        
        # Tokenize and pad
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        
        sequence = model_cache['tokenizer'].texts_to_sequences([cleaned_text])
        if len(sequence) == 0 or len(sequence[0]) == 0:
            logger.warning("Tokenization produced empty sequence")
            return "Legitimate", 0.5, "Warning: Could not tokenize text properly"
        
        padded_sequence = pad_sequences(
            sequence, 
            maxlen=model_cache['max_length'], 
            padding='post', 
            truncating='post'
        )
        
        # Make prediction
        prediction_proba = model_cache['model'].predict(padded_sequence, verbose=0)[0][0]
        prediction_proba = float(max(0.0, min(1.0, prediction_proba)))
        
        if prediction_proba > 0.5:
            prediction = "Spam"
            confidence = prediction_proba
        else:
            prediction = "Legitimate"
            confidence = 1 - prediction_proba
        
        logger.info(f"✅ Prediction: {prediction} (confidence: {confidence:.4f})")
        return prediction, confidence, None
        
    except Exception as e:
        error_msg = f"Prediction failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return None, 0.0, error_msg

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('h.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

@app.route('/health')
def health_check():
    """Health check endpoint"""
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
            "preprocessing_file_exists": os.path.exists("artifacts/preprocessing.pkl"),
            "model_loaded": model_cache['model'] is not None,
            "model_loading": model_cache['loading'],
            "model_error": model_cache['error']
        }
        
        # Try to load model if not loaded
        if not model_cache['model'] and not model_cache['loading']:
            success, message = load_model_safely()
            health_status["model_load_test"] = "success" if success else f"failed: {message}"
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/predict', methods=['GET', 'POST'])
def predict_spam():
    """SMS/Email Spam Detection route"""
    try:
        if request.method == "GET":
            return render_template('home.html', results=None, confidence=None)
        
        # Get message from form
        message_text = request.form.get('email_text')
        
        if not message_text or message_text.strip() == "":
            logger.warning("Empty message received")
            return render_template('home.html', 
                                 results="⚠️ Please enter message text", 
                                 confidence=None)
        
        message_text = message_text.strip()
        logger.info(f"📧 Processing message: {message_text[:100]}...")
        
        # Make prediction
        prediction, confidence, error = predict_message(message_text)
        
        if error:
            logger.error(f"Prediction error: {error}")
            # Return specific error message
            if "not found" in error.lower():
                error_result = "❌ Model files not found. Deployment issue detected."
            elif "tensorflow" in error.lower():
                error_result = "❌ TensorFlow loading error. Please try again."
            elif "memory" in error.lower():
                error_result = "❌ Server memory limit exceeded. Please try again."
            elif "loading" in error.lower():
                error_result = "⏳ Model is loading, please wait and try again."
            else:
                error_result = f"❌ Error: {error}"
            
            return render_template('home.html', 
                                 results=error_result, 
                                 confidence=None)
        
        # Format results
        if prediction == "Spam":
            final_result = "🚨 SPAM DETECTED!"
            result_class = "spam"
        else:
            final_result = "✅ Legitimate Message"
            result_class = "legitimate"
        
        confidence_percent = confidence * 100
        logger.info(f"✅ Prediction successful: {final_result} ({confidence_percent:.1f}%)")
        
        return render_template('home.html', 
                             results=final_result, 
                             confidence=confidence,
                             result_class=result_class,
                             email_preview=message_text[:200])
                             
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Route error: {error_msg}")
        return render_template('home.html', 
                             results=f"❌ Unexpected error: {error_msg}", 
                             confidence=None)

@app.errorhandler(500)
def handle_500(error):
    logger.error(f"500 Error: {error}")
    return render_template('home.html', 
                         results="❌ Internal Server Error. Please check /health endpoint.", 
                         confidence=None), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting app on port {port}")
    
    # Try to preload model in development
    if debug_mode:
        logger.info("🔄 Preloading model for development...")
        success, message = load_model_safely()
        if success:
            logger.info("✅ Model preloaded successfully")
        else:
            logger.warning(f"⚠️ Model preload failed: {message}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)