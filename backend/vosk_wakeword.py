"""
Direct Vosk-based wake word detection (bypassing OVOS plugin).
This works by using Vosk's speech recognition and comparing transcriptions.
"""
import json
import queue
import threading
from typing import Optional, Callable, Dict, Any
import sounddevice as sd
from vosk import Model, KaldiRecognizer


class VoskWakeWordDetector:
    """Wake word detector using raw Vosk speech recognition."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Vosk wake word detector."""
        import os
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 'ovos_config.json'
        )
        self.config = self._load_config()
        
        # Vosk model
        model_path = os.path.expanduser("~/.local/share/vosk/vosk-model-small-en-us-0.15")
        self.model = Model(model_path)
        self.recognizer = None
        
        # Detection state
        self.is_listening = False
        self.stream = None
        self.audio_queue = queue.Queue()
        self.detection_callback: Optional[Callable] = None
        self.listener_thread: Optional[threading.Thread] = None
        
        # Audio settings
        listener_config = self.config.get('listener', {})
        self.sample_rate = listener_config.get('sample_rate', 16000)
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'hotwords': {'safe_word': {'key_phrase': 'hello'}}}
    
    def start_listener(self, callback: Callable, hotword_name: str = 'safe_word',
                      threshold: Optional[float] = None) -> Dict[str, Any]:
        """Start listening for wake word."""
        if self.is_listening:
            return {'success': False, 'error': 'Listener already running'}
        
        try:
            # Get wake word configuration
            hotword_config = self.config.get('hotwords', {}).get(hotword_name, {})
            if not hotword_config:
                return {'success': False, 'error': f'Hotword "{hotword_name}" not found'}
            
            self.wake_phrase = hotword_config.get('key_phrase', '').lower()
            self.detection_callback = callback
            
            print(f"\n{'='*60}")
            print(f"✓ Vosk Wake Word Detector Starting")
            print(f"  Target phrase: '{self.wake_phrase}'")
            print(f"  Sample rate: {self.sample_rate} Hz")
            print(f"{'='*60}\n")
            
            # Create recognizer
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            
            # Start audio stream
            self.is_listening = True
            
            def audio_callback(indata, frames, time, status):
                """Queue audio for processing."""
                if status:
                    print(f"Audio status: {status}")
                if self.is_listening:
                    self.audio_queue.put(bytes(indata))
            
            self.stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=audio_callback
            )
            
            self.stream.start()
            
            # Start processing thread
            self.listener_thread = threading.Thread(target=self._process_audio, daemon=True)
            self.listener_thread.start()
            
            print("✓ Listening started successfully!\n")
            
            return {
                'success': True,
                'key_phrase': self.wake_phrase,
                'sample_rate': self.sample_rate
            }
            
        except Exception as e:
            self.is_listening = False
            return {'success': False, 'error': f'Failed to start: {str(e)}'}
    
    def _process_audio(self):
        """Process audio and detect wake word."""
        print("🎧 Audio processing thread started\n")
        
        while self.is_listening:
            try:
                data = self.audio_queue.get(timeout=1)
                
                if self.recognizer.AcceptWaveform(data):
                    # Final result
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower()
                    
                    if text:
                        print(f"📝 Recognized: \"{text}\"")
                        
                        # Check if wake phrase is in the text
                        if self.wake_phrase in text:
                            print(f"\n{'='*60}")
                            print(f"🚨 WAKE WORD DETECTED!")
                            print(f"  Target: '{self.wake_phrase}'")
                            print(f"  Heard: '{text}'")
                            print(f"{'='*60}\n")
                            
                            if self.detection_callback:
                                threading.Thread(
                                    target=self.detection_callback,
                                    daemon=True
                                ).start()
                else:
                    # Partial result
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '')
                    if partial_text:
                        print(f"🔄 Hearing: {partial_text}", end='\r')
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
        
        print("\n🎧 Audio processing thread stopped")
    
    def stop_listener(self) -> Dict[str, Any]:
        """Stop listening."""
        if not self.is_listening:
            return {'success': True, 'message': 'No listener running'}
        
        try:
            self.is_listening = False
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            if self.listener_thread:
                self.listener_thread.join(timeout=2)
                self.listener_thread = None
            
            # Clear queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            print("✓ Vosk listener stopped\n")
            
            return {'success': True, 'message': 'Listener stopped'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_config(self, hotword_name: str, key_phrase: str,
                     sensitivity: Optional[float] = None,
                     module: Optional[str] = None) -> Dict[str, Any]:
        """Update configuration."""
        try:
            if hotword_name not in self.config.get('hotwords', {}):
                self.config['hotwords'][hotword_name] = {}
            
            hotword_config = self.config['hotwords'][hotword_name]
            hotword_config['key_phrase'] = key_phrase
            
            if sensitivity is not None:
                hotword_config['sensitivity'] = sensitivity
            
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            return {
                'success': True,
                'message': f'Configuration updated for {hotword_name}',
                'config': hotword_config
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        hotword_config = self.config.get('hotwords', {}).get('safe_word', {})
        
        return {
            'listening': self.is_listening,
            'module': 'vosk-direct',
            'key_phrase': hotword_config.get('key_phrase'),
            'sensitivity': hotword_config.get('sensitivity', 0.5),
            'sample_rate': self.sample_rate,
            'engine_loaded': self.recognizer is not None
        }
    
    def check_ovos_installed(self) -> tuple[bool, str]:
        """Check if system is ready."""
        return True, "Vosk direct wake word detection is ready"


# Global instance
vosk_detector = VoskWakeWordDetector()
