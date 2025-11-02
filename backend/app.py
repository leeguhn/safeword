"""
Flask backend for SafeWord detection system.
Provides REST API for training, detection, and action management.
"""
import os
import shutil
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from ovos_runner import ovos_runner
from vosk_wakeword import vosk_detector  # Use working Vosk detector
from audio_utils import save_sample
from actions import action_manager

# Use Vosk detector instead of broken OVOS plugin
wake_word_detector = vosk_detector

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# In-memory store for detection events
detection_events = []

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'wake-word.net')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'safeword-backend'})


@app.route('/check-precise', methods=['GET'])
def check_precise():
    """Check if OVOS wake-word plugins are installed."""
    installed, message = wake_word_detector.check_ovos_installed()
    return jsonify({
        'installed': installed,
        'message': message
    }), 200 if installed else 500


@app.route('/record-sample', methods=['POST'])
def record_sample():
    """
    Save an audio sample to the training dataset.
    
    Expected form data:
        - file: Audio file (WAV or WebM)
        - label: 'wake-word' or 'not-wake-word'
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    label = request.form.get('label', 'wake-word')
    
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Accept both WAV and WebM formats
    # if not (file.filename.endswith('.wav') or file.filename.endswith('.webm')):
    #     return jsonify({'error': 'Only WAV and WebM files are supported'}), 400
    
    # Read file bytes
    audio_bytes = file.read()
    
    # Check if file has content
    if len(audio_bytes) < 100:
        return jsonify({'error': 'Audio file is too small or empty'}), 400
    
    # Save to appropriate directory
    result = save_sample(audio_bytes, label, DATA_DIR)
    
    if result['success']:
        # Count current samples
        wake_dir = os.path.join(DATA_DIR, 'wake-word')
        not_wake_dir = os.path.join(DATA_DIR, 'not-wake-word')
        
        wake_count = len([f for f in os.listdir(wake_dir) if f.endswith('.wav')]) if os.path.exists(wake_dir) else 0
        not_wake_count = len([f for f in os.listdir(not_wake_dir) if f.endswith('.wav')]) if os.path.exists(not_wake_dir) else 0
        
        return jsonify({
            'success': True,
            'path': result['path'],
            'filename': result['filename'],
            'label': label,
            'size': len(audio_bytes),
            'dataset_stats': {
                'wake_word': wake_count,
                'not_wake_word': not_wake_count
            }
        }), 200
    else:
        return jsonify(result), 400


@app.route('/dataset-stats', methods=['GET'])
def dataset_stats():
    """Get statistics about the training dataset."""
    wake_dir = os.path.join(DATA_DIR, 'wake-word')
    not_wake_dir = os.path.join(DATA_DIR, 'not-wake-word')
    
    wake_count = len([f for f in os.listdir(wake_dir) if f.endswith('.wav')]) if os.path.exists(wake_dir) else 0
    not_wake_count = len([f for f in os.listdir(not_wake_dir) if f.endswith('.wav')]) if os.path.exists(not_wake_dir) else 0
    
    return jsonify({
        'wake_word': wake_count,
        'not_wake_word': not_wake_count,
        'total': wake_count + not_wake_count,
        'ready_to_train': wake_count >= 10
    })


@app.route('/list-samples', methods=['GET'])
def list_samples():
    """List all recorded samples with metadata."""
    wake_dir = os.path.join(DATA_DIR, 'wake-word')
    not_wake_dir = os.path.join(DATA_DIR, 'not-wake-word')
    
    samples = []
    
    # List wake-word samples
    if os.path.exists(wake_dir):
        for filename in os.listdir(wake_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(wake_dir, filename)
                samples.append({
                    'filename': filename,
                    'label': 'wake-word',
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'created': os.path.getctime(filepath)
                })
    
    # List not-wake-word samples
    if os.path.exists(not_wake_dir):
        for filename in os.listdir(not_wake_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(not_wake_dir, filename)
                samples.append({
                    'filename': filename,
                    'label': 'not-wake-word',
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'created': os.path.getctime(filepath)
                })
    
    # Sort by creation time (most recent first)
    samples.sort(key=lambda x: x['created'], reverse=True)
    
    return jsonify({'samples': samples})


@app.route('/delete-sample', methods=['DELETE'])
def delete_sample():
    """Delete a specific sample."""
    data = request.get_json()
    filename = data.get('filename')
    label = data.get('label')
    
    if not filename or not label:
        return jsonify({'error': 'Missing filename or label'}), 400
    
    sample_dir = os.path.join(DATA_DIR, label)
    filepath = os.path.join(sample_dir, filename)
    
    # Security check: ensure file is within DATA_DIR
    if not os.path.abspath(filepath).startswith(os.path.abspath(DATA_DIR)):
        return jsonify({'error': 'Invalid file path'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        os.remove(filepath)
        return jsonify({'success': True, 'message': f'Deleted {filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/clear-samples', methods=['POST'])
def clear_samples():
    """Clear all recorded samples."""
    wake_dir = os.path.join(DATA_DIR, 'wake-word')
    not_wake_dir = os.path.join(DATA_DIR, 'not-wake-word')
    
    deleted_count = 0
    
    # Clear wake-word samples
    if os.path.exists(wake_dir):
        for filename in os.listdir(wake_dir):
            if filename.endswith('.wav'):
                os.remove(os.path.join(wake_dir, filename))
                deleted_count += 1
    
    # Clear not-wake-word samples
    if os.path.exists(not_wake_dir):
        for filename in os.listdir(not_wake_dir):
            if filename.endswith('.wav'):
                os.remove(os.path.join(not_wake_dir, filename))
                deleted_count += 1
    
    return jsonify({'success': True, 'deleted_count': deleted_count})


@app.route('/play-sample/<label>/<filename>', methods=['GET'])
def play_sample(label, filename):
    """Serve a sample file for playback."""
    from flask import send_file
    
    sample_dir = os.path.join(DATA_DIR, label)
    filepath = os.path.join(sample_dir, filename)
    
    # Security check
    if not os.path.abspath(filepath).startswith(os.path.abspath(DATA_DIR)):
        return jsonify({'error': 'Invalid file path'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, mimetype='audio/wav')


@app.route('/train', methods=['POST'])
def train_model():
    """
    Configure wake word with OVOS (no training required for Vosk plugin).
    
    Expected JSON body:
        - key_phrase: the wake word to detect (optional, default from config)
        - sensitivity: detection sensitivity 0-1 (optional)
        - module: which plugin to use (optional)
    """
    data = request.get_json() or {}
    
    key_phrase = data.get('key_phrase')
    sensitivity = data.get('sensitivity')
    module = data.get('module')
    
    # OVOS doesn't require training for keyword-based detection (Vosk)
    # If using Precise-Lite, model training would be done externally
    
    if key_phrase:
        result = wake_word_detector.update_config(
            'safe_word',
            key_phrase,
            sensitivity=sensitivity,
            module=module
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Wake word configured successfully',
                'config': result['config'],
                'note': 'OVOS uses plugin-based detection. No training required for keyword detection with Vosk plugin.'
            }), 200
        else:
            return jsonify(result), 400
    else:
        return jsonify({
            'success': True,
            'message': 'Using default configuration',
            'config': wake_word_detector.config.get('hotwords', {}).get('safe_word', {}),
            'note': 'Using Vosk direct speech recognition for wake word detection.'
        }), 200


@app.route('/start-detection', methods=['POST'])
def start_detection():
    """
    Start listening for the wake word.
    
    Expected JSON body:
        - threshold: detection sensitivity 0-1 (optional, default 0.5)
        - hotword_name: which hotword config to use (optional, default 'safe_word')
    """
    data = request.get_json() or {}
    threshold = data.get('threshold', 0.5)
    hotword_name = data.get('hotword_name', 'safe_word')
    
    # Define callback for detection events
    def on_detection():
        """Called when wake word is detected."""
        timestamp = datetime.now().isoformat()
        print(f"\n🚨 WAKE WORD DETECTED at {timestamp}! 🚨\n")
        
        # Add to events list
        detection_events.insert(0, {
            'timestamp': timestamp,
            'message': 'Wake word detected!'
        })
        # Keep only last 20 events
        if len(detection_events) > 20:
            detection_events.pop()
        
        # Trigger actions
        result = action_manager.trigger_actions()
        print(f"Actions result: {result}")
    
    # Start listener
    result = wake_word_detector.start_listener(on_detection, hotword_name, threshold)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/stop-detection', methods=['POST'])
def stop_detection():
    """Stop the wake word listener."""
    result = wake_word_detector.stop_listener()
    return jsonify(result), 200


@app.route('/status', methods=['GET'])
def get_status():
    """Get current system status."""
    ovos_status = wake_word_detector.get_status()
    
    # Get dataset stats
    wake_dir = os.path.join(DATA_DIR, 'wake-word')
    not_wake_dir = os.path.join(DATA_DIR, 'not-wake-word')
    
    wake_count = len([f for f in os.listdir(wake_dir) if f.endswith('.wav')]) if os.path.exists(wake_dir) else 0
    not_wake_count = len([f for f in os.listdir(not_wake_dir) if f.endswith('.wav')]) if os.path.exists(not_wake_dir) else 0
    
    return jsonify({
        'ovos': ovos_status,
        'precise': {'listening': ovos_status['listening']},  # Keep for backwards compatibility
        'model': {
            'exists': True,  # OVOS plugins don't require trained models
            'type': 'ovos-plugin',
            'module': ovos_status.get('module')
        },
        'dataset': {
            'wake_word': wake_count,
            'not_wake_word': not_wake_count,
            'wake_word_samples': wake_count,  # Keep for backwards compatibility
            'not_wake_word_samples': not_wake_count,  # Keep for backwards compatibility
            'ready_to_train': wake_count >= 10
        }
    })


@app.route('/trigger-action', methods=['POST'])
def trigger_action():
    """Manually trigger actions (for testing)."""
    result = action_manager.trigger_actions()
    return jsonify(result), 200


@app.route('/configure-actions', methods=['POST'])
def configure_actions():
    """
    Configure action settings.
    
    Expected JSON body:
        - record_duration: seconds to record
        - encrypt_recordings: boolean
        - contacts: array of {phone, email}
        - grace_period: seconds before triggering
    """
    config = request.get_json()
    
    # Update action manager configuration
    action_manager.config.update(config)
    action_manager.record_duration = config.get('record_duration', 30)
    action_manager.encrypt_recordings = config.get('encrypt_recordings', True)
    action_manager.contacts = config.get('contacts', [])
    action_manager.grace_period = config.get('grace_period', 0)
    
    return jsonify({
        'success': True,
        'config': action_manager.config
    }), 200


@app.route('/detection-events', methods=['GET'])
def get_detection_events():
    """Get recent detection events."""
    return jsonify({
        'events': detection_events[:10]  # Return last 10 events
    }), 200


if __name__ == '__main__':
    print("="*50)
    print("SafeWord Backend Server (OVOS)")
    print("="*50)
    print(f"Data directory: {DATA_DIR}")
    print(f"Models directory: {MODELS_DIR}")
    
    # Check OVOS installation
    installed, message = wake_word_detector.check_ovos_installed()
    print(f"\nWake word detector status: {message}")
    
    if not installed:
        print("\n⚠️  WARNING: Wake word detector not ready!")
    else:
        # Display current configuration
        config = wake_word_detector.config.get('hotwords', {}).get('safe_word', {})
        print(f"\nWake word configuration:")
        print(f"  Key phrase: {config.get('key_phrase', 'Not configured')}")
        print(f"  Sensitivity: {config.get('sensitivity', 0.5)}")
    
    print("\nStarting server on http://127.0.0.1:5001")
    print("="*50 + "\n")
    
    app.run(host='127.0.0.1', port=5001, debug=True)
