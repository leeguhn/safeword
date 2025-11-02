"""
Mycroft Precise subprocess wrapper for training and detection.
"""
import subprocess
import threading
import os
import shutil
import signal
from typing import Optional, Callable, Dict, List

class PreciseRunner:
    """Manages Precise training and listening subprocesses."""
    
    def __init__(self):
        self.train_process: Optional[subprocess.Popen] = None
        self.listen_process: Optional[subprocess.Popen] = None
        self.detection_callback: Optional[Callable] = None
        self.listener_thread: Optional[threading.Thread] = None
        self.is_listening = False
        
    def check_precise_installed(self) -> tuple[bool, str]:
        """Check if Precise runner library is available."""
        try:
            import precise_runner
            return True, "Precise runner library is installed"
        except ImportError:
            return False, "Precise runner library not found. Install with: pip install -e backend/mycroft-precise/mycroft-precise/runner"
    
    def train_model(self, data_dir: str, model_path: str, epochs: int = 10) -> Dict[str, any]:
        """
        Train a wake word model using precise-train.
        
        Args:
            data_dir: Directory containing wake-word/ and not-wake-word/ folders
            model_path: Output path for trained model (.net file)
            epochs: Number of training epochs
            
        Returns:
            Dict with success status, logs, and model path
        """
        # Validate data directory
        wake_word_dir = os.path.join(data_dir, 'wake-word')
        not_wake_word_dir = os.path.join(data_dir, 'not-wake-word')
        
        if not os.path.exists(wake_word_dir):
            return {'success': False, 'error': f'Wake word directory not found: {wake_word_dir}'}
        
        # Count samples
        wake_samples = len([f for f in os.listdir(wake_word_dir) if f.endswith('.wav')])
        not_wake_samples = len([f for f in os.listdir(not_wake_word_dir) if f.endswith('.wav')]) if os.path.exists(not_wake_word_dir) else 0
        
        if wake_samples < 10:
            return {'success': False, 'error': f'Insufficient wake word samples: {wake_samples} (minimum 10 required)'}
        
        # Build training command
        cmd = [
            'precise-train',
            '-e', str(epochs),
            model_path,
            data_dir
        ]
        
        print(f"Training command: {' '.join(cmd)}")
        print(f"Wake word samples: {wake_samples}, Not wake word samples: {not_wake_samples}")
        
        try:
            self.train_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = self.train_process.communicate()
            
            if self.train_process.returncode == 0:
                return {
                    'success': True,
                    'model_path': model_path,
                    'logs': stdout,
                    'wake_samples': wake_samples,
                    'not_wake_samples': not_wake_samples
                }
            else:
                return {
                    'success': False,
                    'error': f'Training failed with return code {self.train_process.returncode}',
                    'logs': stdout,
                    'errors': stderr
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.train_process = None
    
    def start_listener(self, model_path: str, callback: Callable, threshold: float = 0.5) -> Dict[str, any]:
        """
        Start listening for wake word using precise-listen.
        
        Args:
            model_path: Path to trained model file
            callback: Function to call when wake word detected
            threshold: Detection sensitivity (0-1, default 0.5)
            
        Returns:
            Dict with success status and process info
        """
        if not os.path.exists(model_path):
            return {'success': False, 'error': f'Model file not found: {model_path}'}
        
        if self.is_listening:
            return {'success': False, 'error': 'Listener already running'}
        
        self.detection_callback = callback
        
        cmd = [
            'precise-listen',
            model_path,
            '--threshold', str(threshold)
        ]
        
        print(f"Starting listener: {' '.join(cmd)}")
        
        try:
            self.listen_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.is_listening = True
            
            # Start thread to monitor output
            self.listener_thread = threading.Thread(target=self._monitor_listener, daemon=True)
            self.listener_thread.start()
            
            return {
                'success': True,
                'pid': self.listen_process.pid,
                'model': model_path,
                'threshold': threshold
            }
            
        except Exception as e:
            self.is_listening = False
            return {'success': False, 'error': str(e)}
    
    def _monitor_listener(self):
        """Monitor precise-listen output for detection events."""
        if not self.listen_process:
            return
        
        print("Listener monitoring thread started")
        
        try:
            for line in self.listen_process.stdout:
                line = line.strip()
                print(f"Precise output: {line}")
                
                # Precise outputs specific strings on detection
                if 'detected' in line.lower() or line.startswith('!'):
                    print("Wake word DETECTED!")
                    if self.detection_callback:
                        try:
                            self.detection_callback()
                        except Exception as e:
                            print(f"Error in detection callback: {e}")
        
        except Exception as e:
            print(f"Error monitoring listener: {e}")
        finally:
            self.is_listening = False
            print("Listener monitoring thread stopped")
    
    def stop_listener(self) -> Dict[str, any]:
        """Stop the listening process."""
        if not self.listen_process or not self.is_listening:
            return {'success': True, 'message': 'No listener running'}
        
        try:
            # Try graceful termination
            self.listen_process.terminate()
            try:
                self.listen_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if necessary
                self.listen_process.kill()
                self.listen_process.wait()
            
            self.is_listening = False
            self.listen_process = None
            
            if self.listener_thread:
                self.listener_thread.join(timeout=2)
                self.listener_thread = None
            
            return {'success': True, 'message': 'Listener stopped'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict[str, any]:
        """Get current status of training and listening processes."""
        return {
            'training': self.train_process is not None and self.train_process.poll() is None,
            'listening': self.is_listening,
            'listener_pid': self.listen_process.pid if self.listen_process and self.is_listening else None
        }


# Global runner instance
precise_runner = PreciseRunner()
