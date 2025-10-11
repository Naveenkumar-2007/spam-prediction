import os
import numpy as np
import joblib
import logging
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)

class ModelTrainer:
    """
    TensorFlow/Keras LSTM Model Trainer for SMS Spam Detection
    
    Connection Flow:
    1. Reads: train_sequences.pkl, test_sequences.pkl (from data_transform.py)
    2. Builds: LSTM model with Embedding → Bidirectional LSTM → Dense layers
    3. Trains: For 20 epochs with early stopping
    4. Evaluates: Accuracy, Precision, Recall, F1-Score
    5. Outputs: best_model.h5, model_config.pkl, training_history.png
    6. Next: predict_pipeline.py loads this model
    
    Model Architecture:
    - Embedding Layer (128 dimensions)
    - Bidirectional LSTM (128 units)
    - Dropout (0.5)
    - Dense (64 units, ReLU)
    - Dropout (0.3)
    - Dense (1 unit, Sigmoid) - Binary classification
    
    Training Details:
    - Optimizer: Adam
    - Loss: Binary Crossentropy
    - Metrics: Accuracy
    - Batch Size: 64
    - Early Stopping: Patience 3
    """
    
    def __init__(self):
        self.artifacts_dir = "artifacts"
        
        # Check GPU availability
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logging.info(f"🎮 GPU Available: {len(gpus)} GPU(s) detected")
        else:
            logging.info("🖥️  Using CPU")
        
    def build_model(self, vocab_size, max_length):
        """
        Build LSTM model architecture
        
        Args:
            vocab_size (int): Size of vocabulary
            max_length (int): Maximum sequence length
            
        Returns:
            keras.Model: Compiled LSTM model
        """
        model = keras.Sequential([
            # Embedding layer
            layers.Embedding(
                input_dim=vocab_size,
                output_dim=128,
                input_length=max_length,
                name='embedding'
            ),
            
            # Bidirectional LSTM
            layers.Bidirectional(
                layers.LSTM(128, return_sequences=False),
                name='bidirectional_lstm'
            ),
            
            # Dropout for regularization
            layers.Dropout(0.5, name='dropout_1'),
            
            # Dense layers
            layers.Dense(64, activation='relu', name='dense_1'),
            layers.Dropout(0.3, name='dropout_2'),
            
            # Output layer
            layers.Dense(1, activation='sigmoid', name='output')
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def plot_training_history(self, history, save_path):
        """
        Plot training history
        
        Args:
            history: Training history object
            save_path (str): Path to save plot
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Accuracy plot
        axes[0].plot(history.history['accuracy'], label='Train Accuracy')
        axes[0].plot(history.history['val_accuracy'], label='Val Accuracy')
        axes[0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Loss plot
        axes[1].plot(history.history['loss'], label='Train Loss')
        axes[1].plot(history.history['val_loss'], label='Val Loss')
        axes[1].set_title('Model Loss', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"📊 Training history plot saved to: {save_path}")
        plt.close()
    
    def plot_confusion_matrix(self, y_true, y_pred, save_path):
        """
        Plot confusion matrix
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            save_path (str): Path to save plot
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Ham', 'Spam'],
                    yticklabels=['Ham', 'Spam'])
        plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"📊 Confusion matrix saved to: {save_path}")
        plt.close()
    
    def train_model(self, train_seq_path, test_seq_path):
        """
        Train LSTM model
        
        Args:
            train_seq_path (str): Path to training sequences
            test_seq_path (str): Path to test sequences
            
        Returns:
            str: Path to saved model
        """
        logging.info("=" * 70)
        logging.info("SMS SPAM DETECTION - MODEL TRAINING STARTED")
        logging.info("=" * 70)
        
        try:
            # Load sequences
            train_data = joblib.load(train_seq_path)
            test_data = joblib.load(test_seq_path)
            
            X_train = train_data['X']
            y_train = train_data['y']
            X_test = test_data['X']
            y_test = test_data['y']
            
            logging.info(f"📊 Training samples: {X_train.shape[0]}")
            logging.info(f"📊 Test samples: {X_test.shape[0]}")
            
            # Load preprocessing info
            preprocessing_obj = joblib.load(
                os.path.join(self.artifacts_dir, "preprocessing.pkl")
            )
            vocab_size = preprocessing_obj['vocab_size']
            max_length = preprocessing_obj['max_length']
            
            # Build model
            logging.info("\n🏗️  Building LSTM model...")
            model = self.build_model(vocab_size, max_length)
            
            # Print model summary
            logging.info("\n" + "=" * 70)
            model.summary(print_fn=lambda x: logging.info(x))
            logging.info("=" * 70)
            
            # Callbacks
            early_stopping = EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True,
                verbose=1
            )
            
            model_path = os.path.join(self.artifacts_dir, "best_model.h5")
            checkpoint = ModelCheckpoint(
                model_path,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
            
            # Train model
            logging.info("\n🚀 Training model...")
            history = model.fit(
                X_train, y_train,
                epochs=20,
                batch_size=64,
                validation_data=(X_test, y_test),
                callbacks=[early_stopping, checkpoint],
                verbose=1
            )
            
            # Evaluate model
            logging.info("\n📈 Evaluating model...")
            test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
            
            # Predictions
            y_pred_proba = model.predict(X_test, verbose=0)
            y_pred = (y_pred_proba > 0.5).astype(int).flatten()
            
            # Calculate metrics
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            logging.info("\n" + "=" * 70)
            logging.info("📊 MODEL PERFORMANCE:")
            logging.info(f"   Accuracy:  {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
            logging.info(f"   Precision: {precision:.4f}")
            logging.info(f"   Recall:    {recall:.4f}")
            logging.info(f"   F1-Score:  {f1:.4f}")
            logging.info(f"   Loss:      {test_loss:.4f}")
            logging.info("=" * 70)
            
            # Plot training history
            history_plot_path = os.path.join(self.artifacts_dir, "training_history.png")
            self.plot_training_history(history, history_plot_path)
            
            # Plot confusion matrix
            cm_plot_path = os.path.join(self.artifacts_dir, "confusion_matrix.png")
            self.plot_confusion_matrix(y_test, y_pred, cm_plot_path)
            
            # Save model configuration
            model_config = {
                'vocab_size': vocab_size,
                'max_length': max_length,
                'accuracy': float(test_accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1)
            }
            
            config_path = os.path.join(self.artifacts_dir, "model_config.pkl")
            joblib.dump(model_config, config_path)
            
            logging.info(f"\n💾 Model saved to: {model_path}")
            logging.info(f"💾 Config saved to: {config_path}")
            
            logging.info("\n" + "=" * 70)
            logging.info("✅ MODEL TRAINING COMPLETED SUCCESSFULLY")
            logging.info("=" * 70 + "\n")
            
            return model_path
            
        except Exception as e:
            logging.error(f"❌ Error in model training: {str(e)}")
            raise e

if __name__ == "__main__":
    from src.components.data_ingestion import DataIngestion
    from src.components.data_transform import DataTransformation
    
    # Run entire pipeline
    ingestion = DataIngestion()
    train_path, test_path = ingestion.initiate_data_ingestion()
    
    transformation = DataTransformation()
    train_seq_path, test_seq_path, _ = transformation.initiate_data_transformation(
        train_path, test_path
    )
    
    trainer = ModelTrainer()
    trainer.train_model(train_seq_path, test_seq_path)