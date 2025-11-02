#!/usr/bin/env python3
"""
Test what Vosk is actually recognizing in real-time.
This will show you what words Vosk hears vs what it's looking for.
"""
import json
import time
import numpy as np
import sounddevice as sd
from ovos_plugin_manager.wakewords import OVOSWakeWordFactory

# Load config
config = json.load(open('ovos_config.json'))
hotword_config = config['hotwords']['safe_word']

print("=" * 60)
print("VOSK RECOGNITION TEST")
print("=" * 60)
print(f"Looking for: '{hotword_config['key_phrase']}'")
print(f"Sensitivity: {hotword_config.get('sensitivity', 0.5)}")
print(f"Trigger level: {hotword_config.get('trigger_level', 3)}")
print("=" * 60)

# Create engine
engine = OVOSWakeWordFactory.create_hotword('safe_word', config)

# Check if engine has a method to get recognized text
print(f"\nEngine type: {type(engine).__name__}")
print(f"Engine module: {type(engine).__module__}")

# Try to access the internal recognizer if available
if hasattr(engine, 'rec') or hasattr(engine, 'recognizer'):
    print("✓ Engine has recognizer - we can see what it hears!")
else:
    print("⚠ Engine doesn't expose recognizer - will only show detections")

print("\n" + "=" * 60)
print("LISTENING - Speak now! (Ctrl+C to stop)")
print("=" * 60)
print()

detected_count = 0
audio_count = 0

def audio_callback(indata, frames, time_info, status):
    global detected_count, audio_count
    
    if status:
        print(f"Status: {status}")
    
    audio_count += 1
    
    # Convert audio
    audio_data = (indata * 32767).astype(np.int16)
    
    # Show audio level
    volume = np.linalg.norm(indata) * 10
    if volume > 3:
        print(f"🎤 Level: {volume:5.1f} | ", end='')
        
        # Update engine
        engine.update(audio_data.tobytes())
        
        # Check detection
        if engine.found_wake_word():
            detected_count += 1
            print(f"\n{'='*60}")
            print(f"🚨 WAKE WORD DETECTED! (Count: {detected_count})")
            print(f"{'='*60}\n")
        else:
            print("Not detected", end='\r')

# Start stream
stream = sd.InputStream(
    callback=audio_callback,
    channels=1,
    samplerate=16000,
    blocksize=1024,
    dtype='float32'
)

stream.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nStopping...")
    stream.stop()
    stream.close()
    print(f"\nTotal audio chunks processed: {audio_count}")
    print(f"Total detections: {detected_count}")
    print("\nIf no detections occurred, the issue might be:")
    print("1. Vosk model doesn't recognize the phrase clearly")
    print("2. Audio quality or microphone issues")
    print("3. Need to speak more slowly and clearly")
    print(f"4. Try changing the wake word to something simpler like 'computer' or 'hello'")
