#!/usr/bin/env python3
"""
Test script to verify Vosk wake word detection is working.
Run this while speaking to see if audio is being processed.
"""
import json
import numpy as np
import sounddevice as sd
from ovos_plugin_manager.wakewords import OVOSWakeWordFactory

# Load config
with open('ovos_config.json', 'r') as f:
    config = json.load(f)

print("Creating OVOS wake word engine...")
engine = OVOSWakeWordFactory.create_hotword('safe_word', config)
print(f"✓ Engine created: {type(engine)}")
print(f"✓ Listening for: '{config['hotwords']['safe_word']['key_phrase']}'")
print("\nSpeak now! (Ctrl+C to stop)\n")

detected_count = 0

def audio_callback(indata, frames, time_info, status):
    """Process audio for wake word detection."""
    global detected_count
    
    if status:
        print(f"Audio status: {status}")
    
    try:
        # Convert float32 to int16
        audio_data = (indata * 32767).astype(np.int16)
        
        # Update engine
        engine.update(audio_data.tobytes())
        
        # Check for wake word
        if engine.found_wake_word(audio_data.tobytes()):
            detected_count += 1
            print(f"\n🚨 WAKE WORD DETECTED! (Count: {detected_count}) 🚨\n")
    
    except Exception as e:
        print(f"Error: {e}")

# Start audio stream
print("Opening audio stream...")
stream = sd.InputStream(
    callback=audio_callback,
    channels=1,
    samplerate=16000,
    blocksize=1024,
    dtype='float32'
)

stream.start()
print("✓ Audio stream started. Listening...\n")

try:
    # Keep running
    import time
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nStopping...")
    stream.stop()
    stream.close()
    print(f"Total detections: {detected_count}")
