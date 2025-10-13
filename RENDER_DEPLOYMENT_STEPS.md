# Render Deployment Instructions - UPDATED for Python 3.13

## 🎯 IMMEDIATE SOLUTION

### Option 1: Use Updated Requirements (Current Fix)
Your requirements.txt now uses TensorFlow 2.20.0 which is compatible with Python 3.13.4

### Option 2: Alternative Render Settings 

In your Render dashboard, update these settings:

**Environment Variables:**
```
PYTHON_VERSION=3.11.9
```

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT app:app --timeout 120 --workers 1 --memory-limit 512
```

### Option 3: Use Minimal Requirements (If Still Failing)

Replace requirements.txt content with:
```
Flask==3.0.3
gunicorn==22.0.0
tensorflow==2.20.0
numpy
pandas
scikit-learn
nltk
joblib
PyYAML
```

## 🔧 STEP-BY-STEP DEPLOYMENT PROCESS

1. **Go to Render Dashboard** → Your Service
2. **Click "Environment"** → Add:
   - `PYTHON_VERSION` = `3.11.9`
3. **Go to "Settings"** → Update Build Command to:
   ```
   pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
   ```
4. **Click "Manual Deploy"** 

## 🚨 ALTERNATIVE: Force Python 3.11

If Render keeps using 3.13, create a `.python-version` file:

```bash
echo "3.11.9" > .python-version
```

Then commit and push:
```bash
git add .python-version
git commit -m "Force Python 3.11.9"
git push origin main
```

## 📊 MONITORING THE BUILD

Watch these logs in Render dashboard:
- ✅ Python version installation
- ✅ TensorFlow installation success  
- ✅ All requirements installed
- ✅ Gunicorn server startup

## 🎯 CURRENT STATUS

✅ Fixed TensorFlow version to 2.20.0  
✅ Simplified requirements.txt  
✅ Compatible with Python 3.13.4  
✅ Pushed to GitHub  

**Next**: Go to Render and click "Manual Deploy"