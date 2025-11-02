#!/usr/bin/env python3
"""
Test microphone access and audio levels.
Run this to verify your mic is working with the backend.
"""
import numpy as np
import sounddevice as sd

print("🎤 Microphone Test")
print("=" * 50)
print("\nAvailable devices:")
print(sd.query_devices())
print("\nDefault input device:", sd.default.device[0])
print("\nStarting 5-second audio level test...")
print("Speak into your microphone!\n")

max_level = 0
duration = 5  # seconds
sample_rate = 16000

def audio_callback(indata, frames, time, status):
    global max_level
    if status:
        print(f"Status: {status}")
    
    # Calculate audio level (RMS)
    volume_norm = np.linalg.norm(indata) * 10
    max_level = max(max_level, volume_norm)
    
    # Show visual bars
    bars = int(volume_norm / 2)
    print(f"Level: {'█' * bars}{' ' * (25 - bars)} {volume_norm:.2f}", end='\r')

try:
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate):
        sd.sleep(duration * 1000)
    
    print("\n\n✓ Test complete!")
    print(f"Max audio level: {max_level:.2f}")
    
    if max_level < 1:
        print("\n⚠️  WARNING: Very low audio levels detected!")
        print("   - Check if your microphone is muted")
        print("   - Check macOS System Settings > Privacy & Security > Microphone")
        print("   - Make sure Terminal/Python has microphone access")
    elif max_level < 5:
        print("\n⚠️  Audio levels are low. Speak louder or closer to mic.")
    else:
        print("\n✓ Microphone is working correctly!")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check System Settings > Privacy & Security > Microphone")
    print("2. Make sure Terminal.app has microphone permission")
    print("3. Try restarting Terminal")
