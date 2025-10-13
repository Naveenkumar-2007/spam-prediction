from flask import Flask, request, render_template, jsonify
import pandas as pd
import logging
import traceback
import os
from src.pipeline.predict_pipeline import predict, customdata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"Error in predict_spam: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('home.html', 
                             results="❌ Error processing your request. Please try again.", 
                             confidence=None)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)