# SafeWord - Quick Reference

## 🚀 Quick Commands

### First Time Setup
```bash
./setup.sh
```

### Start Application
```bash
# Option 1: Automatic (macOS)
./start.sh

# Option 2: Manual - Terminal 1 (Backend)
cd backend
source .venv/bin/activate
python app.py

# Option 2: Manual - Terminal 2 (Frontend)
cd frontend
npm start
```

### Stop Application
- Press `Ctrl+C` in each terminal window

## 📝 Workflow

### 1. Record Samples (10-20 samples minimum)
- Open http://localhost:3000
- Click "Start Recording"
- Speak your safe word
- Repeat with variations

### 2. Train Model (~2-10 minutes)
- Click "Start Training" 
- Wait for completion
- Check logs for errors

### 3. Configure Actions
- Set recording duration
- Add emergency contacts
- Save configuration

### 4. Start Detection
- Click "Start Detection"
- Speak your safe word to test
- Watch for "DETECTED" message

## 🔧 Common Issues

### "Precise not installed"
```bash
cd backend
source .venv/bin/activate
pip install precise-runner
```

### "PyAudio error" on macOS
```bash
brew install portaudio
pip install pyaudio
```

### "Permission denied" for microphone
- Browser: Grant mic permission in browser settings
- macOS: System Preferences → Security & Privacy → Microphone

### Port already in use
```bash
# Find process using port 5000
lsof -i :5000
# Kill it
kill -9 <PID>
```

## 🧪 Testing with curl

### Upload sample
```bash
curl -X POST -F "file=@sample.wav" -F "label=wake-word" \
  http://127.0.0.1:5000/record-sample
```

### Check status
```bash
curl http://127.0.0.1:5000/status | python3 -m json.tool
```

### Start detection
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"threshold": 0.5}' \
  http://127.0.0.1:5000/start-detection
```

### Test trigger
```bash
curl -X POST http://127.0.0.1:5000/trigger-action
```

## 📊 File Locations

### Training Data
- Wake word samples: `backend/data/wake-word/`
- Not wake word samples: `backend/data/not-wake-word/`

### Model
- Trained model: `backend/models/wake-word.net`

### Recordings
- Alert recordings: `backend/data/recordings/`
- Event log: `backend/data/recordings/events.log`

### Configuration
- Backend: `backend/.env`
- Frontend: `frontend/src/` (components)

## ⚙️ Configuration

### Detection Sensitivity
- **Lower threshold (0.3-0.4)**: More sensitive, may have false positives
- **Default (0.5)**: Balanced
- **Higher threshold (0.6-0.8)**: More strict, may miss detections

### Training Epochs
- **5-10**: Quick testing
- **10-30**: Normal use
- **50-100**: Best accuracy (slower)

### Recording Duration
- **10s**: Quick evidence
- **30s**: Recommended default
- **60s+**: Extended context

## 🆘 Emergency Stops

### Stop Detection Only
- Click "Stop Detection" in UI
- Or: `curl -X POST http://127.0.0.1:5000/stop-detection`

### Stop Everything
- `Ctrl+C` in backend terminal
- `Ctrl+C` in frontend terminal

### Force Kill
```bash
# Kill Python processes
pkill -f "python app.py"

# Kill Node processes
pkill -f "react-scripts"
```

## 📚 More Help

- Full documentation: `README.md`
- API details: See README API Endpoints section
- Contributing: `CONTRIBUTING.md`
- Issues: Open a GitHub issue

## 🔐 Security Reminder

- Keep `.env` file secure (contains encryption keys)
- Don't commit training samples to git
- Recordings are saved locally only
- Review code before deploying to production

---

**Need more help?** Check the README.md or open an issue on GitHub.
