# SafeWord - Visual Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         SAFEWORD SYSTEM ARCHITECTURE                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE (React)                            │
│                          http://localhost:3000                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │  RecordSamples   │  │  ModelTrainer    │  │ DetectionControl │         │
│  │                  │  │                  │  │                  │         │
│  │ • Mic Access     │  │ • Start Train    │  │ • Start/Stop     │         │
│  │ • 2s Recording   │  │ • Epochs Config  │  │ • Threshold      │         │
│  │ • Upload Sample  │  │ • Show Logs      │  │ • Test Trigger   │         │
│  │ • Stats Display  │  │ • Validation     │  │ • Event History  │         │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘         │
│           │                     │                      │                    │
└───────────┼─────────────────────┼──────────────────────┼────────────────────┘
            │                     │                      │
            │   HTTP REST API     │                      │
            ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FLASK BACKEND SERVER                                │
│                          http://127.0.0.1:5000                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                          REST ENDPOINTS                             │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │  POST /record-sample    │ Upload training sample                   │    │
│  │  GET  /dataset-stats    │ Get sample counts                        │    │
│  │  POST /train            │ Start model training                     │    │
│  │  POST /start-detection  │ Begin listening for wake word            │    │
│  │  POST /stop-detection   │ Stop listening                           │    │
│  │  GET  /status           │ Get system status                        │    │
│  │  POST /trigger-action   │ Manually trigger actions (test)          │    │
│  │  POST /configure-actions│ Update action settings                   │    │
│  │  GET  /check-precise    │ Verify Precise installation              │    │
│  │  GET  /health           │ Health check                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │ precise_runner.py│  │  audio_utils.py  │  │   actions.py     │         │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤         │
│  │ • check_precise  │  │ • save_sample    │  │ • trigger_actions│         │
│  │ • train_model    │  │ • start_recording│  │ • record_audio   │         │
│  │ • start_listener │  │ • encrypt_file   │  │ • encrypt_file   │         │
│  │ • stop_listener  │  │ • decrypt_file   │  │ • send_alerts    │         │
│  │ • get_status     │  │                  │  │ • log_event      │         │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘         │
│           │                     │                      │                    │
└───────────┼─────────────────────┼──────────────────────┼────────────────────┘
            │                     │                      │
            ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL INTEGRATIONS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │ Mycroft Precise  │  │     PyAudio      │  │  Cryptography    │         │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤         │
│  │ precise-train    │  │ Audio Recording  │  │ Fernet Encryption│         │
│  │ precise-listen   │  │ Microphone Input │  │ File Security    │         │
│  │ Wake Detection   │  │ WAV Output       │  │ Key Management   │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA STORAGE (Local)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  backend/data/                                                               │
│  ├── wake-word/              Training samples for safe word                 │
│  │   └── sample_*.wav        User recordings                                │
│  ├── not-wake-word/          Training samples for other phrases             │
│  │   └── sample_*.wav        Negative examples                              │
│  └── recordings/             Alert recordings                               │
│      ├── alert_*.wav         Triggered audio recordings                     │
│      ├── alert_*.wav.encrypted  Encrypted recordings                        │
│      └── events.log          Detection event log                            │
│                                                                              │
│  backend/models/                                                             │
│  └── wake-word.net           Trained detection model                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                              WORKFLOW DIAGRAM                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. SAMPLE COLLECTION                    2. MODEL TRAINING
   ┌─────────────┐                         ┌─────────────┐
   │    User     │                         │  Trainer UI │
   │ Speaks into │                         │   Clicks    │
   │ Microphone  │                         │   "Train"   │
   └──────┬──────┘                         └──────┬──────┘
          │                                       │
          ▼                                       ▼
   ┌─────────────┐                         ┌─────────────┐
   │ RecordSamples│                        │   Flask     │
   │  Component  │                         │  /train     │
   └──────┬──────┘                         └──────┬──────┘
          │                                       │
          │ POST /record-sample                   │ spawn subprocess
          ▼                                       ▼
   ┌─────────────┐                         ┌─────────────┐
   │   Flask     │                         │precise-train│
   │  Backend    │                         │   Process   │
   └──────┬──────┘                         └──────┬──────┘
          │                                       │
          │ save_sample()                         │ train model
          ▼                                       ▼
   ┌─────────────┐                         ┌─────────────┐
   │ data/wake-  │                         │wake-word.net│
   │   word/     │                         │   Model     │
   └─────────────┘                         └─────────────┘

3. START DETECTION                      4. WAKE WORD DETECTED
   ┌─────────────┐                         ┌─────────────┐
   │ Detection   │                         │precise-listen│
   │   Control   │                         │   Detects   │
   │   Clicks    │                         │  Wake Word  │
   └──────┬──────┘                         └──────┬──────┘
          │                                       │
          │ POST /start-detection                 │ callback
          ▼                                       ▼
   ┌─────────────┐                         ┌─────────────┐
   │   Flask     │                         │   Flask     │
   │  Backend    │                         │  Callback   │
   └──────┬──────┘                         └──────┬──────┘
          │                                       │
          │ start_listener()                      │ trigger_actions()
          ▼                                       ▼
   ┌─────────────┐                         ┌─────────────┐
   │precise-listen│                        │   Actions   │
   │   Process   │                         │   Manager   │
   └──────┬──────┘                         └──────┬──────┘
          │                                       │
          │ monitor audio                         ├─ Record Audio
          │                                       ├─ Encrypt File
          │                                       ├─ Send Alerts
          │                                       └─ Log Event
          │                                       ▼
          │                                ┌─────────────┐
          └────────────────────────────────│  Evidence   │
                    LISTENING              │   Saved     │
                                           └─────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                          DATA FLOW SUMMARY                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Audio → Browser → React → Flask → Disk (samples)
                           │
                           ├─→ precise-train → Model
                           │
                           └─→ precise-listen → Detection → Actions
                                                              │
                                                              ├─→ PyAudio → Recording
                                                              ├─→ Encrypt → Secure File
                                                              ├─→ SMS/Email (TODO)
                                                              └─→ Log → events.log

╔══════════════════════════════════════════════════════════════════════════════╗
║                        SECURITY BOUNDARIES                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│  LOCAL MACHINE ONLY                                                       │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │  Browser                                                        │     │
│  │  • Microphone access requires user permission                  │     │
│  │  • All data sent to localhost:5000 only                        │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │  Flask Server (localhost:5000)                                 │     │
│  │  • CORS enabled for localhost:3000                             │     │
│  │  • No authentication (local use only)                          │     │
│  │  • Processes audio locally                                     │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │  File System                                                    │     │
│  │  • Recordings encrypted with user key                          │     │
│  │  • Model and samples stored locally                            │     │
│  │  • No cloud upload                                             │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

NO EXTERNAL NETWORK CALLS (except optional SMS/Email if configured)
