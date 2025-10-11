import os
import re
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import logging

logging.basicConfig(level=logging.INFO)

class predict:
    """
    SMS/Email Spam Prediction Pipeline (TensorFlow)
    
    Connection Flow:
    1. Loads: best_model.h5, preprocessing.pkl (from model_trainer.py)
    2. Receives: SMS/Email text from user (via app.py)
    3. Preprocesses: Cleans, tokenizes, pads sequence
    4. Predicts: Uses TensorFlow LSTM model
    5. Returns: "Spam" or "Legitimate" with confidence
    6. Used by: app.py for web interface
    """
    
    def __init__(self):
        self.model_path = "artifacts/best_model.h5"
        self.preprocessing_path = "artifacts/preprocessing.pkl"
        self.model = None
        self.tokenizer = None
        self.max_length = None
        
    def load_model(self):
        """Load TensorFlow model and preprocessing objects"""
        if self.model is None:
            # Load model
            self.model = load_model(self.model_path)
            logging.info(f"✅ Model loaded from: {self.model_path}")
            
            # Load preprocessing
            preprocessing_obj = joblib.load(self.preprocessing_path)
            self.tokenizer = preprocessing_obj['tokenizer']
            self.max_length = preprocessing_obj['max_length']
            logging.info(f"✅ Tokenizer loaded (vocab size: {preprocessing_obj['vocab_size']})")
    
    def clean_text(self, text):
        """Clean text"""
        text = str(text).lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def get_predict(self, message_text):
        """
        Predict if message is spam or legitimate
        
        Args:
            message_text (str or pd.DataFrame): Message content
            
        Returns:
            tuple: (prediction, confidence)
        """
        try:
            # Extract text if DataFrame
            if isinstance(message_text, pd.DataFrame):
                message_text = message_text['text'].iloc[0]
            
            logging.info(f"\n🔍 Analyzing message: {message_text[:100]}...")
            
            # Load model if not loaded
            self.load_model()
            
            # Preprocess text
            cleaned_text = self.clean_text(message_text)
            
            # Tokenize and pad
            sequence = self.tokenizer.texts_to_sequences([cleaned_text])
            padded_sequence = pad_sequences(
                sequence, 
                maxlen=self.max_length, 
                padding='post', 
                truncating='post'
            )
            
            # Predict
            prediction_proba = self.model.predict(padded_sequence, verbose=0)[0][0]
            
            # Convert to label
            if prediction_proba > 0.5:
                prediction = "Spam"
                confidence = prediction_proba
            else:
                prediction = "Legitimate"
                confidence = 1 - prediction_proba
            
            logging.info(f"✅ Prediction: {prediction}")
            logging.info(f"📊 Confidence: {confidence:.4f}")
            
            return prediction, float(confidence)
            
        except Exception as e:
            logging.error(f"❌ Error in prediction: {str(e)}")
            raise e

class customdata:
    """
    Custom data class for user input
    
    Connection Flow:
    1. Receives: Message text from app.py form
    2. Creates: DataFrame for prediction pipeline
    3. Used by: predict.get_predict()
    """
    
    def __init__(self, message_text):
        self.message_text = message_text
        
    def data_frame(self):
        """Convert input to DataFrame"""
        return pd.DataFrame({"text": [self.message_text]})