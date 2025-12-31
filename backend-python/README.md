# AI Sales Agent Backend (Python)

Production-grade voice-first SDR & Sales Agent built with Cerebras, Cartesia, and LiveKit.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend-python
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in `backend-python/` based on `.env.example`:
```env
CEREBRAS_API_KEY=your_key
CARTESIA_API_KEY=your_key
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_key
LIVEKIT_URL=your_url
```

### 3. Run the Agent Worker
This script handles the real-time audio pipeline (VAD -> STT -> LLM -> TTS).
```bash
python -m app.worker dev
```

### 4. Run the Control API (FastAPI)
In a separate terminal:
```bash
python -m app.main
```

## 🧪 Local Testing
You can join the room via the LiveKit Sandbox or use the local microphone/speaker simulation:
```bash
python -m app.worker dev --local
```

## 🏗 Architecture
- **Reasoning**: Cerebras (Llama 3.3 70B) for 100ms+ inference latency.
- **Voice**: Cartesia for natural, human-like voice synthesis.
- **Streaming**: LiveKit for real-time WebRTC audio handling.
- **Controller**: FastAPI for session management and health metrics.

## 📁 Structure
- `app/agent/`: Intelligence, prompts, and memory.
- `app/voice/`: Audio plugins (VAD, TTS).
- `app/services/`: External API wrappers (Cerebras).
- `app/main.py`: REST entry point.
- `app/worker.py`: LiveKit Agent logic.
