import React, { useState, useEffect } from 'react';
import axios from 'axios';

function WakeWordConfig() {
  const [keyPhrase, setKeyPhrase] = useState('');
  const [sensitivity, setSensitivity] = useState(0.5);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [currentConfig, setCurrentConfig] = useState(null);

  useEffect(() => {
    loadCurrentConfig();
  }, []);

  const loadCurrentConfig = async () => {
    try {
      const response = await axios.get('/status');
      const config = response.data.ovos;
      setCurrentConfig(config);
      setKeyPhrase(config.key_phrase || '');
      setSensitivity(config.sensitivity || 0.5);
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const saveConfig = async () => {
    if (!keyPhrase.trim()) {
      setMessage('Error: Please enter a wake word phrase');
      setMessageType('error');
      return;
    }

    try {
      const response = await axios.post('/train', {
        key_phrase: keyPhrase,
        sensitivity: sensitivity
      });

      setMessage(`✓ Wake word configured: "${keyPhrase}"`);
      setMessageType('success');
      
      // Reload config
      loadCurrentConfig();
    } catch (error) {
      console.error('Error saving config:', error);
      setMessage('Error: ' + (error.response?.data?.error || error.message));
      setMessageType('error');
    }
  };

  return (
    <div className="card">
      <h2>Configure Wake Word</h2>
      
      <div className="alert info" style={{ marginBottom: '15px' }}>
        <strong>ℹ️ OVOS uses speech recognition - no training required!</strong>
        <p style={{ marginTop: '5px', fontSize: '14px' }}>
          Simply type any word or phrase. The system will detect it when you speak.
          Examples: "help me", "emergency", "safe word", "pineapple"
        </p>
      </div>

      {currentConfig && (
        <div style={{ marginBottom: '15px', padding: '10px', background: '#f8f9fa', borderRadius: '4px' }}>
          <strong>Current Configuration:</strong>
          <div style={{ marginTop: '5px', fontSize: '14px' }}>
            <div>📢 Wake Word: <code>{currentConfig.key_phrase}</code></div>
            <div>🎚️ Sensitivity: {currentConfig.sensitivity}</div>
            <div>🔌 Module: {currentConfig.module}</div>
          </div>
        </div>
      )}

      <div className="form-group">
        <label>Wake Word / Phrase:</label>
        <input
          type="text"
          value={keyPhrase}
          onChange={(e) => setKeyPhrase(e.target.value)}
          placeholder="e.g., help me, emergency, safe word"
          style={{ width: '100%' }}
        />
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          Enter the word or phrase you want to detect. Can be any words.
        </small>
      </div>

      <div className="form-group">
        <label>Sensitivity: {sensitivity}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={sensitivity}
          onChange={(e) => setSensitivity(parseFloat(e.target.value))}
          style={{ width: '100%' }}
        />
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          Higher = more sensitive (may have false positives), Lower = more strict
        </small>
      </div>

      <button onClick={saveConfig} className="success">
        Save Wake Word Configuration
      </button>

      {message && (
        <div className={`alert ${messageType}`} style={{ marginTop: '15px' }}>
          {message}
        </div>
      )}
    </div>
  );
}

export default WakeWordConfig;
