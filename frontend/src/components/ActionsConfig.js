import React, { useState } from 'react';
import axios from 'axios';

function ActionsConfig() {
  const [recordDuration, setRecordDuration] = useState(30);
  const [encryptRecordings, setEncryptRecordings] = useState(true);
  const [gracePeriod, setGracePeriod] = useState(0);
  const [contacts, setContacts] = useState([]);
  const [newContactPhone, setNewContactPhone] = useState('');
  const [newContactEmail, setNewContactEmail] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const addContact = () => {
    if (!newContactPhone && !newContactEmail) {
      setMessage('Please enter at least phone or email');
      setMessageType('error');
      return;
    }

    const newContact = {};
    if (newContactPhone) newContact.phone = newContactPhone;
    if (newContactEmail) newContact.email = newContactEmail;

    setContacts([...contacts, newContact]);
    setNewContactPhone('');
    setNewContactEmail('');
    setMessage('');
  };

  const removeContact = (index) => {
    setContacts(contacts.filter((_, i) => i !== index));
  };

  const saveConfiguration = async () => {
    try {
      const config = {
        record_duration: recordDuration,
        encrypt_recordings: encryptRecordings,
        grace_period: gracePeriod,
        contacts: contacts
      };

      await axios.post('/configure-actions', config);
      
      setMessage('✓ Configuration saved successfully');
      setMessageType('success');
      
    } catch (error) {
      console.error('Error saving configuration:', error);
      setMessage('Error saving configuration: ' + error.message);
      setMessageType('error');
    }
  };

  return (
    <div className="card">
      <h2>Actions Configuration</h2>
      
      <div className="form-group">
        <label>Recording Duration (seconds):</label>
        <input 
          type="number" 
          value={recordDuration} 
          onChange={(e) => setRecordDuration(parseInt(e.target.value))}
          min="10"
          max="300"
        />
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          How long to record audio after detection
        </small>
      </div>
      
      <div className="form-group">
        <label>
          <input 
            type="checkbox" 
            checked={encryptRecordings} 
            onChange={(e) => setEncryptRecordings(e.target.checked)}
          />
          Encrypt recordings
        </label>
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          Encrypts saved audio files for privacy
        </small>
      </div>
      
      <div className="form-group">
        <label>Grace Period (seconds):</label>
        <input 
          type="number" 
          value={gracePeriod} 
          onChange={(e) => setGracePeriod(parseInt(e.target.value))}
          min="0"
          max="60"
        />
        <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
          Delay before triggering actions (0 = instant)
        </small>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <strong>Emergency Contacts</strong>
        <small style={{ color: '#666', display: 'block', marginBottom: '10px' }}>
          (Note: SMS/Email not yet implemented - placeholders only)
        </small>
        
        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
          <input 
            type="tel" 
            placeholder="Phone number"
            value={newContactPhone}
            onChange={(e) => setNewContactPhone(e.target.value)}
            style={{ flex: 1 }}
          />
          <input 
            type="email" 
            placeholder="Email address"
            value={newContactEmail}
            onChange={(e) => setNewContactEmail(e.target.value)}
            style={{ flex: 1 }}
          />
          <button onClick={addContact}>Add</button>
        </div>
        
        {contacts.length > 0 && (
          <ul className="contact-list">
            {contacts.map((contact, index) => (
              <li key={index} className="contact-item">
                <div>
                  {contact.phone && <div>📱 {contact.phone}</div>}
                  {contact.email && <div>✉️ {contact.email}</div>}
                </div>
                <button onClick={() => removeContact(index)} className="danger">
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <button 
        onClick={saveConfiguration}
        style={{ marginTop: '20px' }}
        className="success"
      >
        Save Configuration
      </button>
      
      {message && (
        <div className={`alert ${messageType}`} style={{ marginTop: '15px' }}>
          {message}
        </div>
      )}
    </div>
  );
}

export default ActionsConfig;
