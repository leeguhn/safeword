# 🛡️ SafeWord - Personal Safety Keyword Detection

A local prototype that detects a user-defined *safe word* and triggers protective actions (record audio, alert contacts). Built with **Mycroft Precise** for keyword spotting, **Flask** backend, and **React** frontend.

## 🎯 Features

- **Custom Wake Word Training**: Record your own safe word samples and train a personalized detection model
- **Real-time Detection**: Continuously listen for your safe word using Mycroft Precise
- **Automatic Actions**: When detected, automatically:
  - Record audio clip for evidence
  - Encrypt recordings for privacy
  - Send alerts to emergency contacts (SMS/Email - placeholder)
- **Web Interface**: User-friendly React app for training and configuration
- **Privacy-First**: All processing happens locally on your machine

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 16+** and npm
- **Microphone** access
- **Mycroft Precise** (installation instructions below)

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Mycroft Precise
pip install precise-runner

# Copy environment template (optional - for SMS/Email features)
cp .env.example .env
# Edit .env with your credentials if needed

# Start Flask server
python app.py
```

The backend will start on `http://127.0.0.1:5000`

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

The frontend will open automatically at `http://localhost:3000`

## 📖 Usage Guide

### Step 1: Record Training Samples

1. Open the React app at `http://localhost:3000`
2. In the **Record Training Samples** section:
   - Select "Wake Word (your safe word)"
   - Click "Start Recording"
   - Speak your safe word clearly
   - Repeat 10-20 times with slight variations in tone and volume
3. Optionally record some "Not Wake Word" samples (other phrases)

**Tip**: The more varied samples you provide, the better the detection accuracy.

### Step 2: Train the Model

1. In the **Train Model** section:
   - Verify you have at least 10 wake-word samples
   - Adjust training epochs if desired (10 is good for quick testing, 50+ for better accuracy)
   - Click "Start Training"
   - Wait for training to complete (may take 2-10 minutes depending on epochs)

### Step 3: Configure Actions (Optional)

1. In the **Actions Configuration** section:
   - Set recording duration (how long to record after detection)
   - Enable/disable encryption
   - Add emergency contacts (SMS/Email features are placeholders for now)
   - Set grace period if desired
   - Click "Save Configuration"

### Step 4: Start Detection

1. In the **Detection Control** section:
   - Adjust detection threshold (0.5 is a good default)
   - Click "Start Detection"
   - Speak your safe word to test
   - When detected, actions will trigger automatically

**Tip**: Use "Test Trigger" to test actions without speaking.

## 🗂️ Project Structure

```
safeword/
├── backend/
│   ├── app.py                 # Flask REST API
│   ├── precise_runner.py      # Mycroft Precise subprocess manager
│   ├── actions.py             # Action triggers (record, alert, etc.)
│   ├── audio_utils.py         # Audio recording and encryption
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── data/
│   │   ├── wake-word/        # Training samples for safe word
│   │   ├── not-wake-word/    # Training samples for other phrases
│   │   └── recordings/       # Alert recordings (created automatically)
│   └── models/
│       └── wake-word.net     # Trained model (created by training)
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js            # Main React app
        ├── index.js
        ├── index.css
        └── components/
            ├── RecordSamples.js      # Sample recording UI
            ├── ModelTrainer.js       # Model training UI
            ├── DetectionControl.js   # Detection controls
            └── ActionsConfig.js      # Action configuration
```

## 🔌 API Endpoints

### Backend (Flask) - `http://127.0.0.1:5000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/check-precise` | GET | Check if Precise is installed |
| `/record-sample` | POST | Upload audio sample for training |
| `/dataset-stats` | GET | Get training dataset statistics |
| `/train` | POST | Train wake word model |
| `/start-detection` | POST | Start listening for wake word |
| `/stop-detection` | POST | Stop listening |
| `/status` | GET | Get system status |
| `/trigger-action` | POST | Manually trigger actions (testing) |
| `/configure-actions` | POST | Update action configuration |

## 🧪 Testing

### Test Sample Upload
```bash
curl -X POST -F "file=@sample.wav" -F "label=wake-word" http://127.0.0.1:5000/record-sample
```

### Test Training
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"epochs": 10}' \
  http://127.0.0.1:5000/train
```

### Test Detection Start
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"threshold": 0.5}' \
  http://127.0.0.1:5000/start-detection
```

### Test Manual Trigger
```bash
curl -X POST http://127.0.0.1:5000/trigger-action
```

### Check Status
```bash
curl http://127.0.0.1:5000/status
```

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Flask
FLASK_APP=app.py
FLASK_ENV=development

# Encryption (for recording encryption)
ENCRYPTION_KEY=your-secure-key-here

# Twilio (for SMS - optional, not yet implemented)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_FROM_NUMBER=+1234567890

# SMTP (for Email - optional, not yet implemented)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Action Configuration

Configure via the React UI or POST to `/configure-actions`:

```json
{
  "record_duration": 30,
  "encrypt_recordings": true,
  "grace_period": 0,
  "contacts": [
    {"phone": "+1234567890", "email": "contact@example.com"}
  ]
}
```

## 🐛 Troubleshooting

### Mycroft Precise Not Found

**Error**: `precise-train` or `precise-listen` command not found

**Solution**: 
```bash
pip install precise-runner
# Or install from source: https://github.com/MycroftAI/mycroft-precise
```

### PyAudio Installation Issues

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian**:
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Windows**:
```bash
pip install pipwin
pipwin install pyaudio
```

### Microphone Permission Denied

- **Browser**: Grant microphone permission when prompted
- **macOS**: System Preferences → Security & Privacy → Microphone → Allow Terminal/Python
- **Linux**: Check PulseAudio/ALSA configuration

### Training Takes Too Long

- Reduce epochs (try 5-10 for quick testing)
- Use fewer samples (minimum 10 wake-word samples)
- Consider training on a more powerful machine

### False Detections

- Increase detection threshold (0.6-0.8)
- Record more varied wake-word samples
- Add more "not wake word" samples
- Retrain with more epochs (50-100)

### Low Detection Rate

- Decrease detection threshold (0.3-0.4)
- Ensure samples are similar to real usage (volume, tone, environment)
- Record more samples (20-30)
- Check microphone quality and positioning

## 🔐 Security & Privacy

- **Local Processing**: All audio processing happens on your machine
- **No Cloud**: No data is sent to external servers
- **Encryption**: Recordings can be encrypted with your key
- **Open Source**: Review and audit the code yourself

⚠️ **Disclaimer**: This is a prototype for educational/personal use. For production safety applications, conduct thorough testing and security audits.

## 🚧 Known Limitations & TODOs

- [ ] SMS/Email alerts are placeholders (Twilio/SMTP code commented out)
- [ ] Training blocks the main thread (should be async/background)
- [ ] No authentication/authorization (local use only)
- [ ] Limited error recovery in subprocess management
- [ ] No mobile app (web UI only)
- [ ] No background service mode (must keep terminal open)

## 🎯 Future Enhancements

- **Background Mode**: Run as system service/daemon
- **Mobile Apps**: iOS/Android native apps
- **Cloud Sync**: Optional encrypted cloud backup of recordings
- **Multi-word Support**: Train multiple safe words
- **Location Sharing**: Send GPS coordinates on detection
- **Video Recording**: Optional camera recording
- **False Positive Protection**: Confirmation mechanism
- **Better Notifications**: Desktop/push notifications

## 📚 Resources

- [Mycroft Precise Documentation](https://github.com/MycroftAI/mycroft-precise)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

## 📝 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Async training implementation
- SMS/Email integration completion
- Better error handling
- Unit tests
- Docker containerization
- Mobile apps

## ⚠️ Important Notes

1. **Test Thoroughly**: Always test in a safe environment before relying on this system
2. **Privacy**: Be aware of recording laws in your jurisdiction
3. **Accuracy**: No detection system is 100% accurate - use as one layer of safety
4. **Emergency Services**: This doesn't replace calling emergency services (911, etc.)
5. **Backup Power**: Consider what happens if power/internet fails

---

**Stay Safe! 🛡️**

For questions or issues, please open a GitHub issue.
