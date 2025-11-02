#!/usr/bin/env python3
"""
Vosk Speech Recognition Logger
Shows what Vosk is actually hearing/transcribing in real-time.
"""
import sys
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Initialize Vosk model
print("Loading Vosk model...")
model_path = "/Users/leeguhn/.local/share/vosk/vosk-model-small-en-us-0.15"
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

print("=" * 70)
print("🎤 VOSK SPEECH RECOGNITION LOGGER")
print("=" * 70)
print("Listening... Speak into your microphone!")
print("Press Ctrl+C to stop")
print("=" * 70)
print()

# Audio queue
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Called for each audio block from the microphone."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Open audio stream
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=audio_callback):
    print("🟢 Listening...\n")
    
    try:
        while True:
            data = q.get()
            
            if recognizer.AcceptWaveform(data):
                # Final result (complete phrase)
                result = json.loads(recognizer.Result())
                if result.get('text'):
                    print(f"✅ RECOGNIZED: \"{result['text']}\"")
            else:
                # Partial result (word in progress)
                partial = json.loads(recognizer.PartialResult())
                if partial.get('partial'):
                    print(f"🔄 Hearing: {partial['partial']}", end='\r')
                    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped")
        # Get any remaining recognition
        final = json.loads(recognizer.FinalResult())
        if final.get('text'):
            print(f"Final: \"{final['text']}\"")
