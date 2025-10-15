# 🚀 Quick Start Guide - Flask Web Application

## Running the Spam Detector Web App

### Step 1: Install Dependencies (if not already done)
```powershell
pip install -r requirements.txt
```

### Step 2: Make Sure Your Model is Trained
If you haven't trained your model yet, run:
```powershell
python run_pipeline.py
```

This will create:
- `artifacts/best_model.h5` (your trained model)
- `artifacts/preprocessing.pkl` (preprocessing objects)
- `artifacts/metrics.json` (model performance)

### Step 3: Start the Flask Web Application
```powershell
python app.py
```

### Step 4: Open Your Browser
The application will automatically start at:
```
http://127.0.0.1:5000
```

Or manually open your browser and go to: **http://localhost:5000**

---

## 🎨 Features

### Beautiful UI Components:
- ✨ Modern gradient design with animations
- 📱 Fully responsive (works on mobile, tablet, desktop)
- 🎯 Real-time spam detection
- 📊 Confidence meter with visual progress bar
- 💡 Quick example buttons to test
- ⚡ Lightning-fast predictions
- 🔒 Privacy-first (no data stored)

### Pages Available:
1. **Home (/)** - Main prediction interface
2. **About (/about)** - Project details and tech stack
3. **Health Check (/health)** - API health status

---

## 🎯 How to Use

### Method 1: Type Your Message
1. Enter or paste any SMS/email message in the text area
2. Click "Analyze Message" button
3. See instant results with confidence level

### Method 2: Try Examples
1. Click on "Spam Example" or "Legitimate Example" buttons
2. The example text will auto-fill
3. Click "Analyze Message" to see results

### Keyboard Shortcuts:
- **Ctrl + Enter** - Analyze message
- **Esc** - Clear message

---

## 📊 Understanding Results

### Result Display Shows:
- **Badge**: Green ✓ for Legitimate, Red ⚠️ for Spam
- **Confidence Level**: Percentage showing model's certainty
- **Progress Bar**: Visual representation of confidence
- **Classification**: Clear spam/legitimate indication
- **Accuracy Level**: High/Medium/Low based on confidence

### Confidence Levels:
- **80-100%**: High confidence - Very reliable
- **60-79%**: Medium confidence - Fairly reliable  
- **0-59%**: Low confidence - Less certain

---

## 🛠️ API Endpoints

### POST /predict
Predict if a message is spam

**Request:**
```json
{
  "message": "Your message text here"
}
```

**Response:**
```json
{
  "error": false,
  "prediction": "Spam",
  "confidence": 95.67,
  "message": "Your message text here",
  "is_spam": true
}
```

### GET /health
Check application health

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

## 🐛 Troubleshooting

### Error: "Model file not found"
**Solution:** Run the training pipeline first:
```powershell
python run_pipeline.py
```

### Error: "Port 5000 already in use"
**Solution:** Kill the process using port 5000 or change port in app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

### Error: "Module not found"
**Solution:** Install missing dependencies:
```powershell
pip install -r requirements.txt
```

### Slow Predictions
**Solution:** The first prediction loads the model and may be slow. Subsequent predictions are fast.

---

## 🎨 Customization

### Change Colors
Edit `static/css/style.css` and modify CSS variables:
```css
:root {
    --primary-color: #6366f1;  /* Change this */
    --success-color: #10b981;  /* Change this */
    --danger-color: #ef4444;   /* Change this */
}
```

### Change Port
Edit `app.py` at the bottom:
```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

### Add More Examples
Edit `templates/index.html` and add more example buttons:
```html
<button class="example-btn" data-text="Your example text">
    <i class="fas fa-icon"></i> Your Label
</button>
```

---

## 📁 Project Structure

```
├── app.py                          # Flask application (main file)
├── static/
│   ├── css/
│   │   └── style.css              # All styling
│   └── js/
│       └── main.js                # Frontend JavaScript
├── templates/
│   ├── index.html                 # Home page
│   ├── about.html                 # About page
│   ├── 404.html                   # Not found page
│   └── 500.html                   # Error page
├── src/
│   └── pipeline/
│       └── predict_pipeline.py    # Prediction logic
├── artifacts/
│   ├── best_model.h5              # Trained model
│   └── preprocessing.pkl          # Preprocessing objects
└── requirements.txt               # Python dependencies
```

---

## 🚀 Deployment Options

### Local Development
```powershell
python app.py
```

### Production with Gunicorn (Linux/Mac)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production with Waitress (Windows)
```powershell
pip install waitress
waitress-serve --port=5000 app:app
```

### Deploy to Cloud
- **Heroku**: Add `Procfile` with `web: gunicorn app:app`
- **AWS/Azure**: Use Docker container
- **Render/Railway**: Connect GitHub repo

---

## 📝 Tips for Best Results

1. **Message Length**: Works best with 10+ characters
2. **Language**: Optimized for English messages
3. **Context**: Include full message for accurate detection
4. **Examples**: Try both spam and legitimate examples
5. **Feedback**: Note confidence levels for reliability

---

## 🎓 Learn More

- **TensorFlow Documentation**: https://www.tensorflow.org/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Project GitHub**: https://github.com/Naveenkumar-2007/spam-prediction
- **MLflow Tracking**: https://dagshub.com/Naveenkumar-2007/spam-prediction.mlflow

---

## ❤️ Credits

Built with:
- **TensorFlow** - Deep learning framework
- **Flask** - Web framework
- **Font Awesome** - Icons
- **Custom CSS** - Beautiful design

---

## 📧 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the console/terminal for error messages
3. Ensure all dependencies are installed
4. Verify model files exist in `artifacts/` folder

---

**Enjoy using the Spam Detector! 🎉**
