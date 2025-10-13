"""
DagsHub Setup and Configuration Script

This script configures DagsHub integration for MLflow and DVC tracking.
DagsHub provides a unified platform for data science collaboration.

Usage:
    python setup_dagshub.py

Environment Variables Required:
    DAGSHUB_USER_TOKEN: Your DagsHub access token
    
Get your token from: https://dagshub.com/user/settings/tokens
"""

import os
import dagshub
import mlflow

def setup_dagshub():
    """
    Configure DagsHub integration with MLflow
    """
    # DagsHub repository details
    DAGSHUB_REPO_OWNER = "Naveenkumar-2007"
    DAGSHUB_REPO_NAME = "spam-prediction"
    
    # Initialize DagsHub
    print("=" * 70)
    print("🚀 Setting up DagsHub Integration")
    print("=" * 70)
    
    try:
        # Initialize DagsHub
        dagshub.init(
            repo_owner=DAGSHUB_REPO_OWNER,
            repo_name=DAGSHUB_REPO_NAME,
            mlflow=True
        )
        
        print(f"✅ DagsHub initialized successfully!")
        print(f"📦 Repository: {DAGSHUB_REPO_OWNER}/{DAGSHUB_REPO_NAME}")
        
        # Set MLflow tracking URI
        mlflow_tracking_uri = mlflow.get_tracking_uri()
        print(f"📊 MLflow Tracking URI: {mlflow_tracking_uri}")
        
        # Display DagsHub URLs
        dagshub_url = f"https://dagshub.com/{DAGSHUB_REPO_OWNER}/{DAGSHUB_REPO_NAME}"
        mlflow_url = f"{dagshub_url}.mlflow"
        dvc_url = f"{dagshub_url}/data"
        
        print(f"\n🔗 DagsHub URLs:")
        print(f"   Repository: {dagshub_url}")
        print(f"   MLflow UI:  {mlflow_url}")
        print(f"   DVC Data:   {dvc_url}")
        
        print("\n" + "=" * 70)
        print("✅ DagsHub setup completed!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up DagsHub: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you have created the repository on DagsHub")
        print("2. Set DAGSHUB_USER_TOKEN environment variable")
        print("3. Install dagshub: pip install dagshub")
        return False

def setup_dvc_remote():
    """
    Configure DVC remote storage with DagsHub
    """
    print("\n" + "=" * 70)
    print("📦 Setting up DVC Remote Storage")
    print("=" * 70)
    
    DAGSHUB_REPO_OWNER = "Naveenkumar-2007"
    DAGSHUB_REPO_NAME = "spam-prediction"
    
    # Get DagsHub credentials
    dagshub_user = os.getenv('DAGSHUB_USER', DAGSHUB_REPO_OWNER)
    dagshub_token = os.getenv('DAGSHUB_USER_TOKEN', '')
    
    if not dagshub_token:
        print("⚠️  DAGSHUB_USER_TOKEN not found in environment variables")
        print("Please set it using:")
        print("  Windows PowerShell: $env:DAGSHUB_USER_TOKEN='your_token_here'")
        print("  Linux/Mac: export DAGSHUB_USER_TOKEN='your_token_here'")
        return False
    
    try:
        import subprocess
        
        # Configure DVC remote
        dvc_remote_url = f"https://dagshub.com/{DAGSHUB_REPO_OWNER}/{DAGSHUB_REPO_NAME}.dvc"
        
        commands = [
            ["dvc", "remote", "add", "-d", "dagshub", dvc_remote_url],
            ["dvc", "remote", "modify", "dagshub", "auth", "basic"],
            ["dvc", "remote", "modify", "dagshub", "user", dagshub_user],
            ["dvc", "remote", "modify", "dagshub", "password", dagshub_token]
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 and "already exists" not in result.stderr:
                print(f"⚠️  {' '.join(cmd)}")
                if result.stderr:
                    print(f"   {result.stderr.strip()}")
        
        print(f"✅ DVC remote configured: {dvc_remote_url}")
        print("\nNext steps:")
        print("  1. Add data to DVC: dvc add artifacts/")
        print("  2. Push to DagsHub: dvc push")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configuring DVC remote: {str(e)}")
        return False

def display_instructions():
    """
    Display setup instructions for the user
    """
    print("\n" + "=" * 70)
    print("📚 SETUP INSTRUCTIONS")
    print("=" * 70)
    
    print("""
1. Create a DagsHub Account:
   - Visit: https://dagshub.com/
   - Sign up or log in with GitHub

2. Create a New Repository:
   - Name: spam-prediction
   - Make it public or private

3. Get Your Access Token:
   - Go to: https://dagshub.com/user/settings/tokens
   - Create a new token
   - Copy the token

4. Set Environment Variable (PowerShell):
   $env:DAGSHUB_USER_TOKEN='your_token_here'

5. Initialize Git and DVC:
   git init
   dvc init
   git add .
   git commit -m "Initial commit with DVC and MLflow"

6. Add DagsHub as remote:
   git remote add origin https://dagshub.com/Naveenkumar-2007/spam-prediction.git

7. Push to DagsHub:
   git push -u origin main
   dvc push

8. Run Your Pipeline:
   python -m src.components.data_ingestion
   python -m src.components.data_transform
   python -m src.components.model_trainer

9. View Results on DagsHub:
   - MLflow experiments: https://dagshub.com/Naveenkumar-2007/spam-prediction.mlflow
   - DVC data: https://dagshub.com/Naveenkumar-2007/spam-prediction/data
""")
    
    print("=" * 70)

if __name__ == "__main__":
    # Display instructions
    display_instructions()
    
    # Setup DagsHub
    success = setup_dagshub()
    
    # Setup DVC remote (optional)
    if success:
        setup_dvc_remote()
    
    print("\n🎉 Setup script completed!")
    print("\nYou can now run your ML pipeline and track it on DagsHub!")
