"""
Complete ML Pipeline Runner with DVC and MLflow Integration

This script runs the entire SMS Spam Detection pipeline:
1. Data Ingestion
2. Data Transformation
3. Model Training (with MLflow tracking)

Usage:
    python run_pipeline.py
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_dagshub_setup():
    """
    Check if DagsHub is configured
    """
    try:
        import dagshub
        token = os.getenv('DAGSHUB_USER_TOKEN')
        
        if not token:
            logging.warning("⚠️  DAGSHUB_USER_TOKEN not found")
            logging.info("MLflow will track locally only")
            logging.info("To enable DagsHub tracking, run: python setup_dagshub.py")
            return False
        
        # Initialize DagsHub
        dagshub.init(
            repo_owner="Naveenkumar-2007",
            repo_name="spam-prediction",
            mlflow=True
        )
        logging.info("✅ DagsHub integration enabled")
        return True
        
    except Exception as e:
        logging.warning(f"⚠️  DagsHub setup failed: {str(e)}")
        logging.info("Continuing with local MLflow tracking")
        return False

def run_data_ingestion():
    """
    Run data ingestion stage
    """
    logging.info("\n" + "=" * 70)
    logging.info("STAGE 1: DATA INGESTION")
    logging.info("=" * 70)
    
    try:
        from src.components.data_ingestion import DataIngestion
        
        ingestion = DataIngestion()
        train_path, test_path = ingestion.initiate_data_ingestion()
        
        logging.info("✅ Data Ingestion completed successfully")
        return train_path, test_path
        
    except Exception as e:
        logging.error(f"❌ Data Ingestion failed: {str(e)}")
        raise e

def run_data_transformation(train_path, test_path):
    """
    Run data transformation stage
    """
    logging.info("\n" + "=" * 70)
    logging.info("STAGE 2: DATA TRANSFORMATION")
    logging.info("=" * 70)
    
    try:
        from src.components.data_transform import DataTransformation
        
        transformation = DataTransformation()
        train_seq_path, test_seq_path, preprocessing_path = transformation.initiate_data_transformation(
            train_path, test_path
        )
        
        logging.info("✅ Data Transformation completed successfully")
        return train_seq_path, test_seq_path, preprocessing_path
        
    except Exception as e:
        logging.error(f"❌ Data Transformation failed: {str(e)}")
        raise e

def run_model_training(train_seq_path, test_seq_path):
    """
    Run model training stage with MLflow tracking
    """
    logging.info("\n" + "=" * 70)
    logging.info("STAGE 3: MODEL TRAINING (with MLflow Tracking)")
    logging.info("=" * 70)
    
    try:
        from src.components.model_trainer import ModelTrainer
        
        trainer = ModelTrainer()
        model_path = trainer.train_model(train_seq_path, test_seq_path)
        
        logging.info("✅ Model Training completed successfully")
        return model_path
        
    except Exception as e:
        logging.error(f"❌ Model Training failed: {str(e)}")
        raise e

def display_results():
    """
    Display pipeline results and next steps
    """
    import mlflow
    
    logging.info("\n" + "=" * 70)
    logging.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    logging.info("=" * 70)
    
    logging.info("\n📊 Results saved in:")
    logging.info("   - artifacts/best_model.h5 (Trained model)")
    logging.info("   - artifacts/metrics.json (Performance metrics)")
    logging.info("   - artifacts/training_history.png (Training plots)")
    logging.info("   - artifacts/confusion_matrix.png (Confusion matrix)")
    
    logging.info(f"\n📈 MLflow Tracking URI: {mlflow.get_tracking_uri()}")
    
    logging.info("\n🔗 View MLflow Experiments:")
    logging.info("   Local:    mlflow ui (then visit http://127.0.0.1:5000)")
    logging.info("   DagsHub:  https://dagshub.com/Naveenkumar-2007/spam-prediction.mlflow")
    
    logging.info("\n📦 Next Steps:")
    logging.info("   1. View results: mlflow ui")
    logging.info("   2. Test model: python test_predictions.py")
    logging.info("   3. Run app: python app.py")
    logging.info("   4. Push to DVC: dvc push")
    logging.info("   5. Commit changes: git add . && git commit -m 'Update model'")
    
    logging.info("\n" + "=" * 70)

def main():
    """
    Main pipeline execution
    """
    start_time = datetime.now()
    
    print("\n" + "=" * 70)
    print("SMS SPAM DETECTION - ML PIPELINE")
    print("=" * 70)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Check DagsHub setup
        check_dagshub_setup()
        
        # Stage 1: Data Ingestion
        train_path, test_path = run_data_ingestion()
        
        # Stage 2: Data Transformation
        train_seq_path, test_seq_path, preprocessing_path = run_data_transformation(
            train_path, test_path
        )
        
        # Stage 3: Model Training
        model_path = run_model_training(train_seq_path, test_seq_path)
        
        # Display results
        end_time = datetime.now()
        duration = end_time - start_time
        
        display_results()
        
        print(f"\n⏱️  Total Duration: {duration}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        logging.error(f"\n❌ Pipeline failed: {str(e)}")
        logging.error("Please check the error message above and fix the issue")
        sys.exit(1)

if __name__ == "__main__":
    main()
