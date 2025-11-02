import React, { useState, useEffect } from 'react';
import axios from 'axios';

function DetectionControl({ modelExists }) {
  const [isListening, setIsListening] = useState(false);
  const [threshold, setThreshold] = useState(0.5);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [detectionEvents, setDetectionEvents] = useState([]);

  useEffect(() => {
    // Poll status every 2 seconds
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const response = await axios.get('/status');
      setIsListening(response.data.precise.listening);
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const startDetection = async () => {
    if (!modelExists) {
      setMessage('Error: No trained model found. Please train a model first.');
      setMessageType('error');
      return;
    }

    try {
      const response = await axios.post('/start-detection', { threshold });
      
      if (response.data.success) {
        setIsListening(true);
        setMessage(`✓ Listening for wake word (PID: ${response.data.pid})`);
        setMessageType('success');
      } else {
        setMessage('Error: ' + response.data.error);
        setMessageType('error');
      }
      
    } catch (error) {
      console.error('Error starting detection:', error);
      setMessage('Error starting detection: ' + (error.response?.data?.error || error.message));
      setMessageType('error');
    }
  };

  const stopDetection = async () => {
    try {
      const response = await axios.post('/stop-detection');
      setIsListening(false);
      setMessage('✓ Detection stopped');
      setMessageType('info');
      
    } catch (error) {
      console.error('Error stopping detection:', error);
      setMessage('Error stopping detection: ' + error.message);
      setMessageType('error');
    }
  };

  const testTrigger = async () => {
    try {
      const response = await axios.post('/trigger-action');
      
      const event = {
        time: new Date().toLocaleTimeString(),
        message: response.data.triggered ? 'Actions triggered successfully' : response.data.reason
      };
      
      setDetectionEvents([event, ...detectionEvents.slice(0, 4)]);
      setMessage('✓ Test trigger executed');
      setMessageType('success');
      
    } catch (error) {
      console.error('Error testing trigger:', error);
      setMessage('Error testing trigger: ' + error.message);
      setMessageType('error');
    }
  };

  return (
    <div className="card">
      <h2>
        Detection Control
        {isListening && <span className="status-badge listening">Listening</span>}
        {!isListening && <span className="status-badge idle">Idle</span>}
      </h2>
      
      {!modelExists && (
        <div className="alert warning">
          No trained model found. Please train a model before starting detection.
        </div>
      )}
      
      <div className="form-group">
        <label>Detection Threshold: {threshold}</label>
        <input 
          type="range" 
          min="0.1" 
          max="1" 
          step="0.1"
          value={threshold} 
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          disabled={isListening}
        />
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          Lower = more sensitive (may have false positives), Higher = more strict
        </small>
      </div>
      
      <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
        {!isListening ? (
          <button 
            onClick={startDetection} 
            disabled={!modelExists}
            className="success"
          >
            Start Detection
          </button>
        ) : (
          <button 
            onClick={stopDetection}
            className="danger"
          >
            Stop Detection
          </button>
        )}
        
        <button onClick={testTrigger}>
          Test Trigger
        </button>
      </div>
      
      {message && (
        <div className={`alert ${messageType}`}>
          {message}
        </div>
      )}
      
      {detectionEvents.length > 0 && (
        <div style={{ marginTop: '15px' }}>
          <strong>Recent Events:</strong>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '10px' }}>
            {detectionEvents.map((event, idx) => (
              <li key={idx} style={{ 
                background: '#f8f9fa', 
                padding: '8px', 
                borderRadius: '4px',
                marginBottom: '5px',
                fontSize: '14px'
              }}>
                <strong>{event.time}</strong>: {event.message}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <div style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
        <p><strong>How it works:</strong></p>
        <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
          <li>Click "Start Detection" to begin listening</li>
          <li>Speak your safe word to trigger actions</li>
          <li>Use "Test Trigger" to test without speaking</li>
          <li>Actions: record audio, send alerts (if configured)</li>
        </ul>
      </div>
    </div>
  );
}

export default DetectionControl;
