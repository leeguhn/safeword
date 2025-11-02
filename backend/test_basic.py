"""
Basic tests for SafeWord backend.
Run with: pytest test_basic.py
"""
import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from audio_utils import save_sample
from precise_runner import PreciseRunner


def test_save_sample_valid_label():
    """Test saving a sample with valid label."""
    wav_bytes = b'RIFF' + b'\x00' * 100  # Fake WAV data
    result = save_sample(wav_bytes, 'wake-word', 'data')
    assert result['success'] == True
    assert 'wake-word' in result['path']
    
    # Cleanup
    if os.path.exists(result['path']):
        os.remove(result['path'])


def test_save_sample_invalid_label():
    """Test saving a sample with invalid label."""
    wav_bytes = b'RIFF' + b'\x00' * 100
    result = save_sample(wav_bytes, 'invalid-label', 'data')
    assert result['success'] == False
    assert 'error' in result


def test_precise_runner_initialization():
    """Test that PreciseRunner initializes correctly."""
    runner = PreciseRunner()
    assert runner.train_process is None
    assert runner.listen_process is None
    assert runner.is_listening == False


def test_precise_runner_check_installation():
    """Test Precise installation check."""
    runner = PreciseRunner()
    installed, message = runner.check_precise_installed()
    # This may fail if Precise is not installed, which is okay for initial setup
    assert isinstance(installed, bool)
    assert isinstance(message, str)


def test_precise_runner_status():
    """Test getting status from PreciseRunner."""
    runner = PreciseRunner()
    status = runner.get_status()
    assert 'training' in status
    assert 'listening' in status
    assert status['training'] == False
    assert status['listening'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
