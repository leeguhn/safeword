import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ModelTrainer({ onTrainingComplete, datasetStats, onSamplesUpdated }) {
  const [isTraining, setIsTraining] = useState(false);
  const [epochs, setEpochs] = useState(10);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [logs, setLogs] = useState('');
  const [samples, setSamples] = useState([]);
  const [playingFile, setPlayingFile] = useState(null);

  useEffect(() => {
    loadSamples();
  }, [datasetStats]);

  const loadSamples = async () => {
    try {
      const response = await axios.get('/list-samples');
      setSamples(response.data.samples);
    } catch (error) {
      console.error('Error loading samples:', error);
    }
  };

  const playSample = (sample) => {
    const audio = new Audio(`/play-sample/${sample.label}/${sample.filename}`);
    setPlayingFile(sample.filename);
    audio.play();
    audio.onended = () => setPlayingFile(null);
    audio.onerror = () => {
      setPlayingFile(null);
      alert('Error playing audio file');
    };
  };

  const deleteSample = async (sample) => {
    if (!window.confirm(`Delete ${sample.filename}?`)) return;

    try {
      await axios.delete('/delete-sample', {
        data: { filename: sample.filename, label: sample.label }
      });
      // Reload the samples list
      await loadSamples();
      // Update parent component stats
      const statsResponse = await axios.get('/dataset-stats');
      if (onSamplesUpdated) {
        onSamplesUpdated(statsResponse.data);
      }
    } catch (error) {
      console.error('Error deleting sample:', error);
      alert('Error deleting sample: ' + (error.response?.data?.error || error.message));
    }
  };

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

  const wakeSamples = samples.filter(s => s.label === 'wake-word');
  const notWakeSamples = samples.filter(s => s.label === 'not-wake-word');

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

      {/* Samples Review Section */}
      {samples.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Review Recorded Samples</h3>
          
          {wakeSamples.length > 0 && (
            <div style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#28a745' }}>Wake Word Samples ({wakeSamples.length})</h4>
              <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '4px', padding: '10px' }}>
                {wakeSamples.map((sample, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px', borderBottom: '1px solid #f0f0f0' }}>
                    <span style={{ fontSize: '13px' }}>{sample.filename}</span>
                    <div>
                      <button 
                        onClick={() => playSample(sample)}
                        disabled={playingFile === sample.filename}
                        style={{ marginRight: '5px', padding: '4px 8px', fontSize: '12px' }}
                      >
                        {playingFile === sample.filename ? '▶️ Playing...' : '▶️ Play'}
                      </button>
                      <button 
                        onClick={() => deleteSample(sample)}
                        style={{ padding: '4px 8px', fontSize: '12px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {notWakeSamples.length > 0 && (
            <div style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#6c757d' }}>Not Wake Word Samples ({notWakeSamples.length})</h4>
              <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '4px', padding: '10px' }}>
                {notWakeSamples.map((sample, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px', borderBottom: '1px solid #f0f0f0' }}>
                    <span style={{ fontSize: '13px' }}>{sample.filename}</span>
                    <div>
                      <button 
                        onClick={() => playSample(sample)}
                        disabled={playingFile === sample.filename}
                        style={{ marginRight: '5px', padding: '4px 8px', fontSize: '12px' }}
                      >
                        {playingFile === sample.filename ? '▶️ Playing...' : '▶️ Play'}
                      </button>
                      <button 
                        onClick={() => deleteSample(sample)}
                        style={{ padding: '4px 8px', fontSize: '12px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
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
