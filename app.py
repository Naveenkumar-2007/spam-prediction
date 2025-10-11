from flask import Flask, request, render_template
import pandas as pd
from src.pipeline.predict_pipeline import predict, customdata

application = Flask(__name__)
app = application

@app.route('/')
def index():
    """Home page"""
    return render_template('h.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)