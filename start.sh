#!/bin/bash

# Start both backend and frontend in separate terminals

echo "Starting SafeWord application..."

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript to open new Terminal windows
    
    # Start backend
    osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/backend && source .venv/bin/activate && python app.py"'
    
    # Wait a moment for backend to start
    sleep 2
    
    # Start frontend
    osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/frontend && npm start"'
    
    echo "✓ Started backend and frontend in separate Terminal windows"
    echo "Frontend will open at http://localhost:3000"
    
else
    # Linux/Other - provide instructions
    echo "Please open two terminal windows:"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "  cd $(pwd)/backend"
    echo "  source .venv/bin/activate"
    echo "  python app.py"
    echo ""
    echo "Terminal 2 (Frontend):"
    echo "  cd $(pwd)/frontend"
    echo "  npm start"
fi
