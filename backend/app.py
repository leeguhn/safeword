"""
Flask backend for SafeWord detection system.
Provides REST API for training, detection, and action management.
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from precise_runner import precise_runner
from audio_utils import save_sample
from actions import action_manager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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
    """Check if Mycroft Precise is installed."""
    installed, message = precise_runner.check_precise_installed()
    return jsonify({
        'installed': installed,
        'message': message
    }), 200 if installed else 500


@app.route('/record-sample', methods=['POST'])
def record_sample():
    """
    Save an audio sample to the training dataset.
    
    Expected form data:
        - file: WAV audio file
        - label: 'wake-word' or 'not-wake-word'
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    label = request.form.get('label', 'wake-word')
    
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    if not file.filename.endswith('.wav'):
        return jsonify({'error': 'Only WAV files are supported'}), 400
    
    # Read file bytes
    wav_bytes = file.read()
    
    # Save to appropriate directory
    result = save_sample(wav_bytes, label, DATA_DIR)
    
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


@app.route('/train', methods=['POST'])
def train_model():
    """
    Train a wake word model using Mycroft Precise.
    
    Expected JSON body:
        - epochs: number of training epochs (optional, default 10)
    """
    data = request.get_json() or {}
    epochs = data.get('epochs', 10)
    
    # Check if Precise is installed
    installed, message = precise_runner.check_precise_installed()
    if not installed:
        return jsonify({'error': message}), 500
    
    # Start training (this blocks, so consider running in background for production)
    print(f"Starting training with {epochs} epochs...")
    result = precise_runner.train_model(DATA_DIR, MODEL_PATH, epochs)
    
    if result['success']:
        return jsonify({
            'success': True,
            'model_path': result['model_path'],
            'wake_samples': result['wake_samples'],
            'not_wake_samples': result['not_wake_samples'],
            'logs': result['logs']
        }), 200
    else:
        return jsonify(result), 400


@app.route('/start-detection', methods=['POST'])
def start_detection():
    """
    Start listening for the wake word.
    
    Expected JSON body:
        - threshold: detection sensitivity 0-1 (optional, default 0.5)
    """
    data = request.get_json() or {}
    threshold = data.get('threshold', 0.5)
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        return jsonify({
            'error': 'Model not found. Please train a model first.',
            'model_path': MODEL_PATH
        }), 400
    
    # Define callback for detection events
    def on_detection():
        """Called when wake word is detected."""
        print("\n🚨 WAKE WORD DETECTED! 🚨\n")
        # Trigger actions
        result = action_manager.trigger_actions()
        print(f"Actions result: {result}")
    
    # Start listener
    result = precise_runner.start_listener(MODEL_PATH, on_detection, threshold)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/stop-detection', methods=['POST'])
def stop_detection():
    """Stop the wake word listener."""
    result = precise_runner.stop_listener()
    return jsonify(result), 200


@app.route('/status', methods=['GET'])
def get_status():
    """Get current system status."""
    precise_status = precise_runner.get_status()
    
    # Check if model exists
    model_exists = os.path.exists(MODEL_PATH)
    
    # Get dataset stats
    wake_dir = os.path.join(DATA_DIR, 'wake-word')
    not_wake_dir = os.path.join(DATA_DIR, 'not-wake-word')
    
    wake_count = len([f for f in os.listdir(wake_dir) if f.endswith('.wav')]) if os.path.exists(wake_dir) else 0
    not_wake_count = len([f for f in os.listdir(not_wake_dir) if f.endswith('.wav')]) if os.path.exists(not_wake_dir) else 0
    
    return jsonify({
        'precise': precise_status,
        'model': {
            'exists': model_exists,
            'path': MODEL_PATH if model_exists else None
        },
        'dataset': {
            'wake_word_samples': wake_count,
            'not_wake_word_samples': not_wake_count,
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


if __name__ == '__main__':
    print("="*50)
    print("SafeWord Backend Server")
    print("="*50)
    print(f"Data directory: {DATA_DIR}")
    print(f"Models directory: {MODELS_DIR}")
    print(f"Model path: {MODEL_PATH}")
    
    # Check Precise installation
    installed, message = precise_runner.check_precise_installed()
    print(f"\nPrecise status: {message}")
    
    if not installed:
        print("\n⚠️  WARNING: Mycroft Precise not installed!")
        print("Install with: pip install precise-runner")
    
    print("\nStarting server on http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
