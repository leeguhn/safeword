"""
Audio utilities for saving samples and recording triggered audio.
"""
import os
import wave
import time
from datetime import datetime
from typing import Optional
from cryptography.fernet import Fernet
import base64
import hashlib

def save_sample(wav_bytes: bytes, label: str, data_dir: str) -> dict:
    """
    Save a WAV audio sample to the appropriate dataset folder.
    
    Args:
        wav_bytes: Raw WAV file bytes
        label: 'wake-word' or 'not-wake-word'
        data_dir: Base data directory
        
    Returns:
        Dict with success status and file path
    """
    if label not in ['wake-word', 'not-wake-word']:
        return {'success': False, 'error': f'Invalid label: {label}'}
    
    target_dir = os.path.join(data_dir, label)
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    counter = 0
    filename = f'sample_{timestamp}_{counter}.wav'
    filepath = os.path.join(target_dir, filename)
    
    while os.path.exists(filepath):
        counter += 1
        filename = f'sample_{timestamp}_{counter}.wav'
        filepath = os.path.join(target_dir, filename)
    
    try:
        with open(filepath, 'wb') as f:
            f.write(wav_bytes)
        
        return {
            'success': True,
            'path': filepath,
            'filename': filename,
            'label': label
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def start_recording_to_file(duration: int, output_path: str, sample_rate: int = 16000) -> dict:
    """
    Record audio from microphone to file (used when alert is triggered).
    
    Args:
        duration: Recording duration in seconds
        output_path: Path to save the recording
        sample_rate: Audio sample rate
        
    Returns:
        Dict with success status and file info
    """
    try:
        import pyaudio
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        
        audio = pyaudio.PyAudio()
        
        print(f"Recording {duration} seconds to {output_path}...")
        
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=sample_rate,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        
        for i in range(0, int(sample_rate / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save to WAV file
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        
        print(f"Recording saved to {output_path}")
        
        return {
            'success': True,
            'path': output_path,
            'duration': duration,
            'size': os.path.getsize(output_path)
        }
        
    except ImportError:
        return {'success': False, 'error': 'PyAudio not installed. Install with: pip install pyaudio'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def encrypt_file(file_path: str, key: Optional[str] = None) -> dict:
    """
    Encrypt a file using Fernet symmetric encryption.
    
    Args:
        file_path: Path to file to encrypt
        key: Encryption key (will generate if not provided)
        
    Returns:
        Dict with success status and encrypted file path
    """
    try:
        # Generate key from password or use provided
        if key:
            # Derive key from password
            key_bytes = hashlib.sha256(key.encode()).digest()
            key_b64 = base64.urlsafe_b64encode(key_bytes)
        else:
            key_b64 = Fernet.generate_key()
        
        cipher = Fernet(key_b64)
        
        # Read original file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Encrypt
        encrypted_data = cipher.encrypt(data)
        
        # Save encrypted file
        encrypted_path = file_path + '.encrypted'
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Optionally remove original
        # os.remove(file_path)
        
        return {
            'success': True,
            'encrypted_path': encrypted_path,
            'original_path': file_path
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def decrypt_file(encrypted_path: str, key: str, output_path: Optional[str] = None) -> dict:
    """
    Decrypt a file encrypted with encrypt_file.
    
    Args:
        encrypted_path: Path to encrypted file
        key: Encryption key
        output_path: Path to save decrypted file (defaults to removing .encrypted)
        
    Returns:
        Dict with success status and decrypted file path
    """
    try:
        # Derive key from password
        key_bytes = hashlib.sha256(key.encode()).digest()
        key_b64 = base64.urlsafe_b64encode(key_bytes)
        cipher = Fernet(key_b64)
        
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Save decrypted file
        if not output_path:
            output_path = encrypted_path.replace('.encrypted', '')
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        return {
            'success': True,
            'decrypted_path': output_path
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
