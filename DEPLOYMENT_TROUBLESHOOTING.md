# Render Deployment Troubleshooting Guide

## 🔧 Common Issues & Solutions

### 1. **TensorFlow Version Conflicts**
**Error**: `ERROR: Could not find a version that satisfies the requirement tensorflow==2.18.0`

**Solution**: 
- Use compatible TensorFlow versions
- Check Python version compatibility
- Current fix: tensorflow==2.16.2 with Python 3.11.9

### 2. **Build Timeout Issues**
**Error**: Build takes too long or times out

**Solutions**:
- Reduce dependencies in requirements.txt
- Comment out optional packages (matplotlib, seaborn)
- Use smaller TensorFlow builds

### 3. **Memory Issues**
**Error**: Out of memory during build or runtime

**Solutions**:
- Reduce model size
- Use tensorflow-cpu instead of full tensorflow
- Optimize model loading

### 4. **Python Version Mismatch**
**Error**: Package compatibility issues

**Solutions**:
- Add runtime.txt with specific Python version
- Update render.yaml with correct Python version
- Test locally with same Python version

## 🚀 Quick Fixes for Current Deployment

### Step 1: Test Locally First
```bash
# Create virtual environment
python -m venv render_test_env
render_test_env\Scripts\activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Test app locally
python app.py
```

### Step 2: Minimal Requirements (if still failing)
Create a minimal requirements.txt:
```
Flask==3.0.3
gunicorn==22.0.0
tensorflow-cpu==2.16.2
numpy==1.26.4
pandas==2.2.2
nltk==3.8.1
scikit-learn==1.5.1
joblib==1.4.2
PyYAML==6.0.1
```

### Step 3: Alternative - Use Docker Build
If issues persist, consider using Docker for consistent deployment.

## 📊 Build Optimization Tips

1. **Reduce Build Time**:
   - Remove unnecessary packages
   - Use requirements-min.txt for deployment
   - Cache dependencies when possible

2. **Memory Optimization**:
   - Use `tensorflow-cpu` instead of `tensorflow`
   - Load model lazily (only when needed)
   - Reduce model complexity if possible

3. **Deployment Monitoring**:
   - Watch build logs in real-time
   - Check resource usage
   - Monitor cold start times

## 🎯 Recommended Render Settings

```yaml
# render.yaml optimized settings
services:
  - type: web
    name: spam-prediction-app
    env: python
    buildCommand: |
      pip install --upgrade pip &&
      pip install --no-cache-dir -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app --timeout 120 --workers 1 --max-requests 1000 --preload
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: PYTHONUNBUFFERED
        value: 1
```

## 🔍 Debug Commands

```bash
# Check Python version
python --version

# Check TensorFlow installation
python -c "import tensorflow as tf; print(tf.__version__)"

# Test model loading
python -c "from src.pipeline.predict_pipeline import predict; p = predict()"

# Check Flask app
python -c "from app import app; print(app.url_map)"
```