# Setup Issue Resolution

## Problem
The initial `./setup.sh` script failed with:
```
error: command '/usr/bin/clang' failed with exit code 1
fatal error: 'portaudio.h' file not found
Failed to build pyaudio
```

## Root Cause
PyAudio requires the **PortAudio** library to be installed on macOS before pip can compile it. The library provides the low-level audio I/O functionality that PyAudio wraps.

## Solution Applied

### 1. Updated `setup.sh` Script
Added automatic PortAudio detection and installation for macOS:
- Checks if PortAudio is installed via Homebrew
- Automatically installs it if missing (with Homebrew check)
- Provides fallback instructions if Homebrew is not available
- Separates PyAudio installation with better error handling
- Allows continuation without PyAudio if user chooses (with warning)

### 2. Installed PortAudio
```bash
brew install portaudio
```

### 3. Re-ran Setup
After PortAudio installation, the setup script completed successfully:
- ✅ Python dependencies installed
- ✅ PyAudio compiled and installed
- ✅ Flask and other backend dependencies installed
- ✅ Mycroft Precise installed
- ✅ Frontend npm dependencies installed

## Status: ✅ RESOLVED

The application is now ready to run!

## To Start the Application

### Option 1: Automatic (macOS)
```bash
./start.sh
```

### Option 2: Manual
**Terminal 1 (Backend):**
```bash
cd backend
source .venv/bin/activate
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

Then open: http://localhost:3000

## Notes

### PyAudio Installation on Different Platforms

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

### What the Updated Setup Script Does

1. **Checks prerequisites**: Python 3, Node.js
2. **Detects OS**: Runs macOS-specific PortAudio check
3. **Installs PortAudio**: If not found and Homebrew available
4. **Creates virtual environment**: For Python isolation
5. **Installs PyAudio separately**: With better error handling
6. **Installs remaining dependencies**: Flask, Precise, etc.
7. **Sets up frontend**: npm install
8. **Creates .env**: From example template

### Dependencies Installed

**Backend:**
- flask==3.0.0
- flask-cors==4.0.0
- python-dotenv==1.0.0
- pyaudio==0.2.14 ✅ (now working)
- requests==2.31.0
- psutil==5.9.6
- cryptography==41.0.7
- precise-runner (Mycroft Precise)

**Frontend:**
- react@18.2.0
- react-dom@18.2.0
- react-scripts@5.0.1
- axios@1.6.0
- 1323 additional packages (dependencies)

## Next Steps

1. **Start the application** using one of the methods above
2. **Record training samples** (10-20 samples of your safe word)
3. **Train the model** (~5-10 minutes)
4. **Start detection** and test with your safe word

See `README.md` for detailed usage instructions.

---

**Issue**: Setup failure due to missing PortAudio  
**Fixed**: Updated setup script + installed PortAudio  
**Status**: ✅ Working  
**Date**: November 2, 2025
