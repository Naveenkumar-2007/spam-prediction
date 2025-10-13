# Render Deployment Fix Guide

## ✅ Fixed Issues

### 1. **TensorFlow Version Problem**
- **Issue**: `tensorflow>=2.20.0` doesn't exist 
- **Fix**: Changed to `tensorflow-cpu==2.15.0` for stability and faster builds

### 2. **Memory Optimization** 
- **Issue**: Render free tier has limited memory (~512MB)
- **Fix**: 
  - Using `tensorflow-cpu` instead of full TensorFlow
  - Added `--no-cache-dir` to pip install
  - Optimized gunicorn settings with memory limits

### 3. **Better Error Handling**
- Added comprehensive error handling for deployment issues
- Created `/health` endpoint for debugging
- More specific error messages for different failure types

## 🚀 Deployment Steps

### Method 1: Use Updated Files (Recommended)

1. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "Fix deployment issues for Render"
   git push origin main
   ```

2. **In Render Dashboard:**
   - Go to your service
   - Click "Manual Deploy" → "Deploy latest commit"
   - Monitor build logs for any errors

3. **Test endpoints:**
   - Main app: `https://your-app.onrender.com/`
   - Health check: `https://your-app.onrender.com/health`
   - Prediction: `https://your-app.onrender.com/predict`

### Method 2: Alternative Configuration

If still having issues, try this render.yaml:

```yaml
services:
  - type: web
    name: spam-prediction-app
    env: python
    buildCommand: |
      pip install --upgrade pip
      pip install --no-cache-dir -r requirements-minimal.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app --timeout 300 --workers 1 --memory-limit 450
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: TF_CPP_MIN_LOG_LEVEL
        value: "3"
      - key: PYTHONUNBUFFERED
        value: "1"
```

## 🔧 Troubleshooting

### If build fails:
1. Check build logs in Render dashboard
2. Try using `requirements-minimal.txt` instead of `requirements.txt`
3. Consider upgrading to Render paid plan for more resources

### If app starts but crashes:
1. Check `/health` endpoint first
2. Look at runtime logs in Render dashboard
3. Check if model files are included in git repository

### If getting "Error processing your request":
1. The error handling now shows more specific messages
2. Check if TensorFlow is loading properly
3. Verify model files are accessible

## 📦 Key Files Updated

1. **requirements.txt** - Fixed TensorFlow version
2. **requirements-minimal.txt** - Lightweight version for deployment  
3. **render.yaml** - Optimized build and start commands
4. **app.py** - Better error handling and health check
5. **predict_pipeline.py** - Deployment-friendly model loading

## 🎯 Expected Results

After deployment:
- Main page should load without errors
- `/health` endpoint should show service status
- Spam prediction should work correctly
- Better error messages if something fails

## 💡 Tips

- Monitor build time (should be under 15 minutes)
- First model load might be slow (30-60 seconds)
- Use `/health` endpoint to debug issues
- Check Render logs for detailed error information