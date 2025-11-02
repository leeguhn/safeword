"""
OVOS wake-word detection runner.
Replaces Mycroft Precise with modern OVOS plugin framework.
"""
import json
import os
import threading
from typing import Optional, Callable, Dict, Any
import numpy as np


class OVOSRunner:
    """Manages OVOS wake-word detection using plugin framework."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize OVOS runner with configuration.
        
        Args:
            config_path: Path to ovos_config.json file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 'ovos_config.json'
        )
        self.config = self._load_config()
        
        self.engine = None
        self.stream = None
        self.detection_callback: Optional[Callable] = None
        self.is_listening = False
        self.listener_thread: Optional[threading.Thread] = None
        
        # Audio settings from config
        listener_config = self.config.get('listener', {})
        self.sample_rate = listener_config.get('sample_rate', 16000)
        self.channels = listener_config.get('channels', 1)
        self.chunk_size = listener_config.get('chunk_size', 1024)
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}")
            return {
                'hotwords': {
                    'safe_word': {
                        'module': 'ovos-ww-plugin-vosk',
                        'key_phrase': 'pineapple',
                        'listen': True,
                        'sensitivity': 0.5,
                        'trigger_level': 3
                    }
                }
            }
    
    def check_ovos_installed(self) -> tuple[bool, str]:
        """Check if OVOS plugin manager and wake word plugins are available."""
        try:
            from ovos_plugin_manager.wakewords import OVOSWakeWordFactory
            import sounddevice as sd
            
            # Try to get available plugins
            try:
                # Check if we can create a plugin instance
                hotword_config = self.config.get('hotwords', {}).get('safe_word', {})
                module = hotword_config.get('module', 'ovos-ww-plugin-vosk')
                
                return True, f"OVOS plugin manager is installed. Using module: {module}"
            except Exception as e:
                return True, f"OVOS installed but plugin may need configuration: {str(e)}"
                
        except ImportError as e:
            return False, f"OVOS wake-word plugins not found. Install with: pip install ovos-plugin-manager ovos-ww-plugin-vosk sounddevice. Error: {str(e)}"
    
    def start_listener(self, callback: Callable, hotword_name: str = 'safe_word', 
                      threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Start listening for wake word using OVOS plugins.
        
        Args:
            callback: Function to call when wake word detected
            hotword_name: Name of hotword config to use (default 'safe_word')
            threshold: Override sensitivity threshold (0-1)
            
        Returns:
            Dict with success status and process info
        """
        if self.is_listening:
            return {'success': False, 'error': 'Listener already running'}
        
        try:
            from ovos_plugin_manager.wakewords import OVOSWakeWordFactory
            import sounddevice as sd
            
            # Get hotword configuration
            hotword_config = self.config.get('hotwords', {}).get(hotword_name, {})
            
            if not hotword_config:
                return {
                    'success': False, 
                    'error': f'Hotword "{hotword_name}" not found in config'
                }
            
            # Override threshold if provided
            if threshold is not None:
                hotword_config['sensitivity'] = threshold
            
            # Store callback
            self.detection_callback = callback
            
            # Create OVOS wake word engine
            print(f"Initializing OVOS wake word engine...")
            print(f"Module: {hotword_config.get('module')}")
            print(f"Key phrase: {hotword_config.get('key_phrase')}")
            print(f"Sensitivity: {hotword_config.get('sensitivity', 0.5)}")
            
            try:
                # Pass the full config, not just the hotword config
                self.engine = OVOSWakeWordFactory.create_hotword(
                    hotword_name,
                    self.config
                )
                
                print(f"\n{'='*60}")
                print(f"✓ Wake word engine initialized")
                print(f"  Looking for: '{hotword_config.get('key_phrase')}'")
                print(f"  When you speak, watch for detection messages!")
                print(f"{'='*60}\n")
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to create wake word engine: {str(e)}'
                }
            
            if not self.engine:
                return {
                    'success': False,
                    'error': 'Failed to create wake word engine. Check plugin installation.'
                }
            
            # Start audio stream
            self.is_listening = True
            
            def audio_callback(indata, frames, time_info, status):
                """Process audio chunks for wake word detection."""
                if status:
                    print(f"Audio status: {status}")
                
                if not self.is_listening:
                    return
                
                try:
                    # Convert to the format expected by OVOS
                    # sounddevice provides float32 by default, convert to int16
                    audio_data = (indata * 32767).astype(np.int16)
                    
                    # Calculate audio level for debugging
                    volume_norm = np.linalg.norm(indata) * 10
                    if volume_norm > 5:  # Only log when there's significant audio
                        print(f"🎤 Audio level: {volume_norm:.1f}", end='\r')
                    
                    # Feed audio to wake word engine
                    self.engine.update(audio_data.tobytes())
                    
                    # Check for detection (no argument needed!)
                    detected = self.engine.found_wake_word()
                    
                    if detected:
                        print(f"\n{'='*60}")
                        print("🚨 WAKE WORD DETECTED by OVOS!")
                        print(f"  Target phrase: '{hotword_config.get('key_phrase')}'")
                        print(f"{'='*60}\n")
                        
                        if self.detection_callback:
                            try:
                                # Run callback in separate thread to avoid blocking audio
                                threading.Thread(
                                    target=self.detection_callback,
                                    daemon=True
                                ).start()
                            except Exception as e:
                                print(f"Error in detection callback: {e}")
                
                except Exception as e:
                    print(f"Error processing audio: {e}")
            
            # Open audio stream
            self.stream = sd.InputStream(
                callback=audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype='float32'
            )
            
            self.stream.start()
            
            print(f"✓ OVOS listener started successfully")
            print(f"  Sample rate: {self.sample_rate} Hz")
            print(f"  Channels: {self.channels}")
            print(f"  Listening for: '{hotword_config.get('key_phrase')}'")
            
            return {
                'success': True,
                'module': hotword_config.get('module'),
                'key_phrase': hotword_config.get('key_phrase'),
                'sensitivity': hotword_config.get('sensitivity', 0.5),
                'sample_rate': self.sample_rate
            }
            
        except ImportError as e:
            self.is_listening = False
            return {
                'success': False,
                'error': f'Missing dependencies: {str(e)}. Install with: pip install ovos-plugin-manager ovos-ww-plugin-vosk sounddevice'
            }
        except Exception as e:
            self.is_listening = False
            return {'success': False, 'error': f'Failed to start listener: {str(e)}'}
    
    def stop_listener(self) -> Dict[str, Any]:
        """Stop the listening process."""
        if not self.is_listening:
            return {'success': True, 'message': 'No listener running'}
        
        try:
            self.is_listening = False
            
            # Stop and close audio stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # Clean up engine
            if self.engine:
                self.engine = None
            
            print("✓ OVOS listener stopped")
            
            return {'success': True, 'message': 'Listener stopped'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_config(self, hotword_name: str, key_phrase: str, 
                     sensitivity: Optional[float] = None,
                     module: Optional[str] = None) -> Dict[str, Any]:
        """
        Update hotword configuration.
        
        Args:
            hotword_name: Name of hotword to update
            key_phrase: New wake word phrase
            sensitivity: New sensitivity (0-1)
            module: Change plugin module
            
        Returns:
            Dict with success status
        """
        try:
            # Update in-memory config
            if hotword_name not in self.config.get('hotwords', {}):
                self.config['hotwords'][hotword_name] = {}
            
            hotword_config = self.config['hotwords'][hotword_name]
            hotword_config['key_phrase'] = key_phrase
            
            if sensitivity is not None:
                hotword_config['sensitivity'] = sensitivity
            
            if module is not None:
                hotword_config['module'] = module
            
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
        """Get current status of the wake word listener."""
        hotword_config = self.config.get('hotwords', {}).get('safe_word', {})
        
        return {
            'listening': self.is_listening,
            'module': hotword_config.get('module'),
            'key_phrase': hotword_config.get('key_phrase'),
            'sensitivity': hotword_config.get('sensitivity', 0.5),
            'sample_rate': self.sample_rate,
            'engine_loaded': self.engine is not None
        }


# Global runner instance
ovos_runner = OVOSRunner()
