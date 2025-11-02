import React, { useState } from 'react';
import axios from 'axios';

function ModelTrainer({ onTrainingComplete, datasetStats }) {
  const [isTraining, setIsTraining] = useState(false);
  const [epochs, setEpochs] = useState(10);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [logs, setLogs] = useState('');

  const startTraining = async () => {
    if (datasetStats && datasetStats.wake_word < 10) {
      setMessage('Error: Need at least 10 wake-word samples to train. Current: ' + datasetStats.wake_word);
      setMessageType('error');
      return;
    }

    setIsTraining(true);
    setMessage('Training model... This may take a few minutes.');
    setMessageType('info');
    setLogs('');

    try {
      const response = await axios.post('/train', { epochs });
      
      setIsTraining(false);
      setMessage(`✓ Training complete! Model saved to ${response.data.model_path}`);
      setMessageType('success');
      setLogs(response.data.logs || '');
      
      if (onTrainingComplete) {
        onTrainingComplete(response.data);
      }
      
    } catch (error) {
      console.error('Training error:', error);
      setIsTraining(false);
      setMessage('Error during training: ' + (error.response?.data?.error || error.message));
      setMessageType('error');
      
      if (error.response?.data?.logs) {
        setLogs(error.response.data.logs);
      }
      if (error.response?.data?.errors) {
        setLogs(logs + '\n\nErrors:\n' + error.response.data.errors);
      }
    }
  };

  const readyToTrain = datasetStats && datasetStats.wake_word >= 10;

  return (
    <div className="card">
      <h2>Train Model</h2>
      
      {datasetStats && (
        <div className="stats">
          <div className="stat-item">
            <div className="label">Wake Word</div>
            <div className="value">{datasetStats.wake_word}</div>
          </div>
          <div className="stat-item">
            <div className="label">Not Wake Word</div>
            <div className="value">{datasetStats.not_wake_word}</div>
          </div>
        </div>
      )}
      
      {!readyToTrain && (
        <div className="alert warning">
          Need at least 10 wake-word samples. Current: {datasetStats?.wake_word || 0}
        </div>
      )}
      
      <div className="form-group">
        <label>Training Epochs:</label>
        <input 
          type="number" 
          value={epochs} 
          onChange={(e) => setEpochs(parseInt(e.target.value))}
          min="1"
          max="100"
          disabled={isTraining}
        />
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          More epochs = better accuracy but longer training time
        </small>
      </div>
      
      <button 
        onClick={startTraining} 
        disabled={isTraining || !readyToTrain}
        className="success"
      >
        {isTraining ? 'Training...' : 'Start Training'}
      </button>
      
      {message && (
        <div className={`alert ${messageType}`}>
          {message}
        </div>
      )}
      
      {logs && (
        <div style={{ marginTop: '15px' }}>
          <strong>Training Logs:</strong>
          <pre style={{ 
            background: '#f8f9fa', 
            padding: '10px', 
            borderRadius: '4px', 
            fontSize: '12px',
            overflow: 'auto',
            maxHeight: '200px'
          }}>
            {logs}
          </pre>
        </div>
      )}
    </div>
  );
}

export default ModelTrainer;
