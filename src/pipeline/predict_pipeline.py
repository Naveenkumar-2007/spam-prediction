import os
import re
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import logging
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

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
            try:
                # Check if model file exists
                if not os.path.exists(self.model_path):
                    raise FileNotFoundError(f"Model file not found: {self.model_path}")
                
                if not os.path.exists(self.preprocessing_path):
                    raise FileNotFoundError(f"Preprocessing file not found: {self.preprocessing_path}")
                
                # Load model
                self.model = load_model(self.model_path)
                logging.info(f"✅ Model loaded from: {self.model_path}")
                
                # Load preprocessing
                preprocessing_obj = joblib.load(self.preprocessing_path)
                
                # Validate preprocessing object
                required_keys = ['tokenizer', 'max_length', 'vocab_size']
                for key in required_keys:
                    if key not in preprocessing_obj:
                        raise KeyError(f"Missing key in preprocessing object: {key}")
                
                self.tokenizer = preprocessing_obj['tokenizer']
                self.max_length = preprocessing_obj['max_length']
                logging.info(f"✅ Tokenizer loaded (vocab size: {preprocessing_obj['vocab_size']})")
                
            except Exception as e:
                logging.error(f"❌ Error loading model or preprocessing: {str(e)}")
                raise e
    
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
            # Input validation
            if message_text is None:
                raise ValueError("Message text cannot be None")
            
            # Extract text if DataFrame
            if isinstance(message_text, pd.DataFrame):
                if 'text' not in message_text.columns:
                    raise KeyError("DataFrame must contain 'text' column")
                if len(message_text) == 0:
                    raise ValueError("DataFrame is empty")
                message_text = message_text['text'].iloc[0]
            
            # Convert to string and validate
            message_text = str(message_text).strip()
            if len(message_text) == 0:
                raise ValueError("Message text is empty")
            
            logging.info(f"\n🔍 Analyzing message: {message_text[:100]}...")
            
            # Load model if not loaded
            self.load_model()
            
            # Validate model components
            if self.model is None:
                raise RuntimeError("Model failed to load")
            if self.tokenizer is None:
                raise RuntimeError("Tokenizer failed to load")
            if self.max_length is None:
                raise RuntimeError("Max length not set")
            
            # Preprocess text
            cleaned_text = self.clean_text(message_text)
            if len(cleaned_text.strip()) == 0:
                logging.warning("Text became empty after cleaning, using original text")
                cleaned_text = message_text
            
            # Tokenize and pad
            sequence = self.tokenizer.texts_to_sequences([cleaned_text])
            
            # Check if tokenization produced any sequences
            if len(sequence) == 0 or len(sequence[0]) == 0:
                logging.warning("Tokenization produced empty sequence")
                # Return a default prediction for unknown text
                return "Legitimate", 0.5
            
            padded_sequence = pad_sequences(
                sequence, 
                maxlen=self.max_length, 
                padding='post', 
                truncating='post'
            )
            
            # Validate padded sequence
            if padded_sequence is None or len(padded_sequence) == 0:
                raise RuntimeError("Padding failed")
            
            # Predict
            prediction_proba = self.model.predict(padded_sequence, verbose=0)
            
            # Validate prediction output
            if prediction_proba is None or len(prediction_proba) == 0:
                raise RuntimeError("Model prediction failed")
            
            prediction_proba = float(prediction_proba[0][0])
            
            # Ensure probability is in valid range
            prediction_proba = max(0.0, min(1.0, prediction_proba))
            
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
        if message_text is None:
            raise ValueError("Message text cannot be None")
        self.message_text = str(message_text).strip()
        if len(self.message_text) == 0:
            raise ValueError("Message text cannot be empty")
        
    def data_frame(self):
        """Convert input to DataFrame"""
        try:
            df = pd.DataFrame({"text": [self.message_text]})
            if len(df) == 0:
                raise ValueError("Failed to create DataFrame")
            return df
        except Exception as e:
            logging.error(f"Error creating DataFrame: {str(e)}")
            raise e