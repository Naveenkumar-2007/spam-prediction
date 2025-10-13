import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)

class customdata:
    def __init__(self, message_text):
        self.message_text = message_text
    
    def data_frame(self):
        return pd.DataFrame({'message': [self.message_text]})

class predict_fallback:
    """Fallback prediction system using keyword-based detection"""
    
    def __init__(self):
        # Common spam keywords
        self.spam_keywords = [
            'free', 'win', 'winner', 'prize', 'urgent', 'act now', 'limited time',
            'click here', 'call now', 'offer', '$', 'money', 'cash', 'loan',
            'credit', 'debt', 'congratulations', 'selected', 'guaranteed',
            'no obligation', 'risk free', 'save', 'discount', 'deal'
        ]
    
    def get_predict(self, data_df):
        """Simple keyword-based prediction"""
        try:
            message = str(data_df['message'].iloc[0]).lower()
            
            # Count spam keywords
            spam_score = 0
            for keyword in self.spam_keywords:
                if keyword in message:
                    spam_score += 1
            
            # Simple scoring
            if spam_score >= 3:
                return "Spam", min(0.6 + (spam_score * 0.1), 0.95)
            elif spam_score >= 1:
                return "Spam", 0.6
            else:
                return "Legitimate", 0.8
                
        except Exception as e:
            logging.error(f"Fallback prediction error: {e}")
            return "Legitimate", 0.5  # Default to legitimate if error

# Try to import the real prediction system, fallback to simple one
try:
    from src.pipeline.predict_pipeline import predict as real_predict, customdata as real_customdata
    predict = real_predict
    customdata = real_customdata
    USING_ML_MODEL = True
    print("✅ Using ML model for predictions")
except Exception as e:
    predict = predict_fallback  
    USING_ML_MODEL = False
    print(f"⚠️ Using fallback prediction system: {e}")