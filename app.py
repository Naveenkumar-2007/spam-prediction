"""
SpamShield AI - Premium Spam Detection Platform
Enterprise-grade spam detection powered by advanced AI
"""

from flask import Flask, render_template, request, jsonify
from src.pipeline.predict_pipeline import predict, customdata
import logging
import traceback
import secrets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['JSON_SORT_KEYS'] = False

# Initialize predictor
predictor = predict()

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_spam():
    """
    Handle spam prediction request
    
    Returns:
        JSON response with prediction and confidence
    """
    try:
        # Get message from request
        if request.is_json:
            data = request.get_json()
            message_text = data.get('message', '')
        else:
            message_text = request.form.get('message', '')
        
        # Validate input
        if not message_text or message_text.strip() == '':
            return jsonify({
                'error': True,
                'message': 'Please enter a message to analyze'
            }), 400
        
        logging.info(f"📨 Received prediction request for message: {message_text[:50]}...")
        
        # Create custom data object
        custom_data = customdata(message_text)
        
        # Convert to DataFrame
        data_df = custom_data.data_frame()
        
        # Get prediction
        prediction, confidence = predictor.get_predict(data_df)
        
        # Prepare response
        response = {
            'error': False,
            'prediction': prediction,
            'confidence': round(confidence * 100, 2),
            'message': message_text,
            'is_spam': prediction == 'Spam'
        }
        
        logging.info(f"✅ Prediction: {prediction} ({confidence*100:.2f}% confidence)")
        
        return jsonify(response)
        
    except ValueError as ve:
        logging.error(f"Validation error: {str(ve)}")
        return jsonify({
            'error': True,
            'message': str(ve)
        }), 400
        
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'error': True,
            'message': 'An error occurred during prediction. Please try again.'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Try to load model
        predictor.load_model()
        return jsonify({
            'status': 'healthy',
            'model_loaded': predictor.model is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/features')
def features():
    """Render features page"""
    return render_template('features.html')

@app.route('/privacy')
def privacy():
    """Render privacy policy page"""
    return render_template('privacy.html')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logging.error(f"Internal error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("�️  SPAMSHIELD AI - PREMIUM SPAM DETECTION PLATFORM")
    print("=" * 80)
    print("🤖 AI Model: Advanced LSTM Neural Network")
    print("🔒 Privacy: Your data is never stored or shared")
    print("⚡ Performance: Real-time detection in milliseconds")
    print("=" * 80)
    print("\n🌐 Server running at: http://127.0.0.1:5000")
    print("💼 Premium Edition - Professional Grade Protection")
    print("\n📝 Press CTRL+C to stop the server\n")
    
    # Run Flask app (use_reloader=False fixes Windows compatibility issue)
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
