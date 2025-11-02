#!/bin/bash

# Start both backend and frontend in separate terminals

echo "Starting SafeWord application..."

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript to open new Terminal windows
    
    # Start Vosk speech logger
    osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/backend && source .venv/bin/activate && echo \"🎤 VOSK SPEECH LOGGER - See what Vosk hears\" && python vosk_logger.py"'
    
    # Wait a moment
    sleep 1
    
    # Start backend
    osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/backend && source .venv/bin/activate && python app.py"'
    
    # Wait a moment for backend to start
    sleep 2
    
    # Start frontend
    osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/frontend && npm start"'
    
    echo "✓ Started Vosk logger, backend, and frontend in separate Terminal windows"
    echo "  - Vosk Logger: Shows what speech is being recognized"
    echo "  - Backend: Flask API server"
    echo "  - Frontend: Will open at http://localhost:3000"
    
else
    # Linux/Other - provide instructions
    echo "Please open three terminal windows:"
    echo ""
    echo "Terminal 1 (Vosk Logger):"
    echo "  cd $(pwd)/backend"
    echo "  source .venv/bin/activate"
    echo "  python vosk_logger.py"
    echo ""
    echo "Terminal 2 (Backend):"
    echo "  cd $(pwd)/backend"
    echo "  source .venv/bin/activate"
    echo "  python app.py"
    echo ""
    echo "Terminal 3 (Frontend):"
    echo "  cd $(pwd)/frontend"
    echo "  npm start"
fi
