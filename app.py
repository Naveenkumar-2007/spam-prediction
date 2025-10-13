from flask import Flask, request, render_template
import pandas as pd
import os
import traceback

application = Flask(__name__)
app = application

# Add debugging for imports with fallback system
try:
    from prediction_fallback import predict, customdata, USING_ML_MODEL
    IMPORTS_OK = True
    IMPORT_ERROR = None
    print("✅ Successfully imported prediction modules")
    if USING_ML_MODEL:
        print("✅ Using full ML model")
    else:
        print("⚠️ Using fallback keyword-based detection")
except Exception as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)
    print(f"❌ Import Error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    traceback.print_exc()

@app.route('/')
def index():
    """Home page"""
    return render_template('h.html')

@app.route('/debug')
def debug():
    """Debug endpoint to check imports and environment"""
    debug_info = {
        'imports_ok': IMPORTS_OK,
        'import_error': IMPORT_ERROR,
        'working_directory': os.getcwd(),
        'python_path': os.environ.get('PYTHONPATH', 'Not set'),
        'files_in_directory': os.listdir('.') if os.path.exists('.') else 'Directory not found'
    }
    return f"<pre>{debug_info}</pre>"

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

@app.route('/predict', methods=['GET','POST'])
def predict_spam():
    """
    SMS/Email Spam Detection route with error handling
    """
    try:
        if not IMPORTS_OK:
            return render_template('home.html', 
                                 results=f"⚠️ Import Error: {IMPORT_ERROR}", 
                                 confidence=None)
        
        if request.method == "GET":
            return render_template('home.html', results=None, confidence=None)
        
        else:
            # Get message from form
            message_text = request.form.get('email_text')
            
            if not message_text:
                return render_template('home.html', 
                                     results="⚠️ Please enter message text", 
                                     confidence=None)
            
            # Create prediction object
            data = customdata(message_text=message_text)
            data_df = data.data_frame()
            
            print("\n" + "="*70)
            print("📧 Message Input:")
            print(message_text[:200])
            print("="*70)
            
            # Get prediction
            predict_pipeline = predict()
            prediction, confidence = predict_pipeline.get_predict(data_df)
            
            # Format results
            if prediction == "Spam":
                final_result = "🚨 SPAM DETECTED!"
                result_class = "spam"
            else:
                final_result = "✅ Legitimate Message"
                result_class = "legitimate"
            
            confidence_percent = confidence * 100
            
            print(f"\n🎯 Prediction: {final_result} ({confidence_percent:.1f}% confident)\n")
            
            return render_template('home.html', 
                                 results=final_result, 
                                 confidence=confidence,
                                 result_class=result_class,
                                 email_preview=message_text[:200])
                                 
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        return render_template('home.html', 
                             results="⚠️ Server Error - Check logs", 
                             confidence=None)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)