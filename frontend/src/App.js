import React, { useState, useEffect } from 'react';
import './index.css';
import RecordSamples from './components/RecordSamples';
import ModelTrainer from './components/ModelTrainer';
import DetectionControl from './components/DetectionControl';
import ActionsConfig from './components/ActionsConfig';
import WakeWordConfig from './components/WakeWordConfig';
import axios from 'axios';

function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [preciseInstalled, setPreciseInstalled] = useState(null);
  const [datasetStats, setDatasetStats] = useState(null);

  useEffect(() => {
    checkPreciseInstallation();
    fetchStatus();
    
    // Poll status every 5 seconds
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkPreciseInstallation = async () => {
    try {
      const response = await axios.get('/check-precise');
      setPreciseInstalled(response.data.installed);
      
      if (!response.data.installed) {
        console.warn('OVOS not installed:', response.data.message);
      }
    } catch (error) {
      console.error('Error checking OVOS installation:', error);
      setPreciseInstalled(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await axios.get('/status');
      setSystemStatus(response.data);
      setDatasetStats(response.data.dataset);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const handleSampleRecorded = (data) => {
    // Refresh dataset stats
    setDatasetStats(data.dataset_stats);
  };

  const handleSamplesUpdated = (stats) => {
    // Update dataset stats when samples are deleted
    setDatasetStats(stats);
  };

  const handleTrainingComplete = (data) => {
    // Refresh status to show model exists
    fetchStatus();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🛡️ SafeWord</h1>
        <p>Personal Safety Keyword Detection System</p>
      </header>

      {preciseInstalled === false && (
        <div className="alert error">
          <strong>⚠️ OVOS Wake Word Plugins not installed!</strong>
          <p>Install with: <code>pip install ovos-plugin-manager ovos-ww-plugin-vosk</code></p>
          <p>Some features will not work until OVOS plugins are installed.</p>
        </div>
      )}

      {systemStatus && (
        <div className="card">
          <h2>System Status</h2>
          <div className="stats">
            <div className="stat-item">
              <div className="label">Model</div>
              <div className="value" style={{ fontSize: '16px' }}>
                {systemStatus.model.exists ? '✓ Trained' : '✗ Not Trained'}
              </div>
            </div>
            <div className="stat-item">
              <div className="label">Detection</div>
              <div className="value" style={{ fontSize: '16px' }}>
                {systemStatus.precise.listening ? '🎤 Listening' : '⏸ Idle'}
              </div>
            </div>
            <div className="stat-item">
              <div className="label">Samples</div>
              <div className="value">
                {systemStatus.dataset.wake_word_samples}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="container">
        <WakeWordConfig />
      </div>

      <div className="container">
        <DetectionControl modelExists={true} />
        <ActionsConfig />
      </div>

      <details style={{ marginTop: '20px', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
        <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>
          📁 Advanced: Sample Recording & Management (Optional)
        </summary>
        <p style={{ color: '#666', fontSize: '14px', marginBottom: '15px' }}>
          OVOS doesn't require training samples, but you can still record and manage audio samples for other purposes.
        </p>
        <div className="container">
          <RecordSamples onSampleRecorded={handleSampleRecorded} />
          <ModelTrainer 
            onTrainingComplete={handleTrainingComplete}
            onSamplesUpdated={handleSamplesUpdated}
            datasetStats={datasetStats}
          />
        </div>
      </details>

      <footer style={{ 
        textAlign: 'center', 
        marginTop: '40px', 
        padding: '20px', 
        color: '#666',
        fontSize: '14px'
      }}>
        <p>SafeWord v0.1.0 - Personal Safety Prototype</p>
        <p>Built with React + Flask + OVOS</p>
      </footer>
    </div>
  );
}

export default App;
