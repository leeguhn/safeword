import React, { useState, useRef } from 'react';
import axios from 'axios';

function RecordSamples({ onSampleRecorded }) {
  const [isRecording, setIsRecording] = useState(false);
  const [label, setLabel] = useState('wake-word');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [recordingDuration, setRecordingDuration] = useState(3);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const clearAllSamples = async () => {
    if (!window.confirm('Are you sure you want to delete ALL recorded samples?')) return;

    try {
      const response = await axios.post('/clear-samples');
      setMessage(`✓ Cleared ${response.data.deleted_count} samples`);
      setMessageType('success');
      if (onSampleRecorded) {
        onSampleRecorded({ dataset_stats: { wake_word: 0, not_wake_word: 0 } });
      }
    } catch (error) {
      console.error('Error clearing samples:', error);
      setMessage('Error clearing samples: ' + (error.response?.data?.error || error.message));
      setMessageType('error');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      });
      
      // Try to use WAV if supported, otherwise use webm
      const options = { mimeType: 'audio/webm' };
      mediaRecorderRef.current = new MediaRecorder(stream, options);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Check if blob has data
        if (audioBlob.size > 100) { // Minimum reasonable size
          await uploadSample(audioBlob);
        } else {
          setMessage('Error: Recording too short or empty. Please try again.');
          setMessageType('error');
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setMessage(`Recording for ${recordingDuration}s... Speak your safe word now!`);
      setMessageType('info');
      
      // Auto-stop after configured duration
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          stopRecording();
        }
      }, recordingDuration * 1000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setMessage('Error: Could not access microphone. Please grant permission.');
      setMessageType('error');
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };
  
  const uploadSample = async (audioBlob) => {
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'sample.wav');
      formData.append('label', label);
      
      const response = await axios.post('/record-sample', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setMessage(`✓ Sample saved! Total: ${response.data.dataset_stats.wake_word} wake-word, ${response.data.dataset_stats.not_wake_word} not-wake-word`);
      setMessageType('success');
      
      if (onSampleRecorded) {
        onSampleRecorded(response.data);
      }
      
    } catch (error) {
      console.error('Error uploading sample:', error);
      setMessage('Error uploading sample: ' + (error.response?.data?.error || error.message));
      setMessageType('error');
    }
  };

  return (
    <div className="card">
      <h2>Record Training Samples</h2>
      
      <div className="form-group">
        <label>Sample Type:</label>
        <select value={label} onChange={(e) => setLabel(e.target.value)} disabled={isRecording}>
          <option value="wake-word">Wake Word (your safe word)</option>
          <option value="not-wake-word">Not Wake Word (other phrases)</option>
        </select>
      </div>

      <div className="form-group">
        <label>Recording Duration (seconds):</label>
        <input 
          type="number" 
          value={recordingDuration} 
          onChange={(e) => setRecordingDuration(Math.max(1, Math.min(10, parseInt(e.target.value) || 3)))}
          min="1"
          max="10"
          disabled={isRecording}
          style={{ width: '100px' }}
        />
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          Recommended: 2-3 seconds for wake words
        </small>
      </div>
      
      <div className="recording-controls">
        <button 
          onClick={startRecording} 
          disabled={isRecording}
          className="success"
        >
          {isRecording ? 'Recording...' : 'Start Recording'}
        </button>

        <button 
          onClick={clearAllSamples}
          disabled={isRecording}
          style={{ marginLeft: '10px', background: '#dc3545' }}
        >
          Clear All Samples
        </button>
        
        {isRecording && (
          <>
            <span className="recording-indicator"></span>
            <span>Recording {recordingDuration}s...</span>
          </>
        )}
      </div>
      
      {message && (
        <div className={`alert ${messageType}`}>
          {message}
        </div>
      )}
      
      <div style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
        <p><strong>Instructions:</strong></p>
        <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
          <li>Record 10-20 samples of your safe word</li>
          <li>Speak clearly and naturally</li>
          <li>Vary your tone and volume slightly</li>
          <li>Optionally record some "not wake word" samples</li>
        </ul>
      </div>
    </div>
  );
}

export default RecordSamples;
