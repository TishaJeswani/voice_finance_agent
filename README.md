# 🎙️ Voice-Based Personal Finance Assistant (WhatsApp AI Agent)

## 📌 Overview

A production-level AI-powered WhatsApp assistant that helps users manage and analyze their personal finances using **text and voice inputs**.

Users can send messages or voice notes on WhatsApp, and the system:

* Understands the query using LLM
* Analyzes financial data
* Generates smart insights
* Replies in text or voice

---

## 🚀 Features

✅ WhatsApp Integration using Twilio
✅ Supports **Text + Voice Messages**
✅ Speech-to-Text using Whisper
✅ AI-powered insights using LLM (OpenRouter - DeepSeek)
✅ Finance data analysis using Pandas
✅ Context-aware responses (Memory support)
✅ Text-to-Speech (audio replies)
✅ Clean modular backend architecture

---

## 🏗️ System Architecture

```
User (WhatsApp)
   ↓
Twilio Webhook
   ↓
FastAPI Backend
   ↓
-----------------------------------
Modules:
- Input Handler
- Audio Downloader
- Speech-to-Text (Whisper)
- Finance Engine (Pandas)
- Memory Service
- LLM Service (DeepSeek via OpenRouter)
- Text-to-Speech (edge-tts)
-----------------------------------
   ↓
Response (Text / Audio)
```

---

## 🛠️ Tech Stack

### Backend

* FastAPI (Python)

### Messaging

* Twilio WhatsApp API

### AI / ML

* Whisper (Speech-to-Text)
* OpenRouter (DeepSeek LLM)

### Data Processing

* Pandas

### Storage

* CSV (transactions dataset)

### Voice

* edge-tts

### Dev Tools

* ngrok (for webhook exposure)

---

## 📂 Project Structure

```
voice-finance-agent/
│
├── app/
│   ├── api/routes/
│   │   └── whatsapp.py
│   │
│   ├── services/
│   │   ├── input_handler.py
│   │   ├── audio_service.py
│   │   ├── stt_service.py
│   │   ├── llm_service.py
│   │   ├── finance_service.py
│   │   ├── memory_service.py
│   │   ├── tts_service.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── models/
│   │   └── message.py
│   │
│   └── main.py
│
├── data/
│   └── transactions.csv
│
├── app/media/   (generated audio files)
│
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

Sample dataset includes:

* Date
* Category (Groceries, Entertainment, etc.)
* Amount
* Description
* Payment Method

---

## ⚙️ Setup Instructions

### 1. Clone Repo

```bash
git clone <your-repo-url>
cd voice-finance-agent
```

---

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Setup Environment Variables

Create `.env` file:

```
OPENROUTER_API_KEY=your_api_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
```

---

### 5. Run Server

```bash
uvicorn app.main:app --reload
```

---

### 6. Start ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL and paste it into:
👉 Twilio WhatsApp Sandbox → Webhook URL

---

## 🧪 How It Works

### Flow:

1. User sends message (text/voice)
2. Twilio sends webhook request
3. Backend processes:

   * Text → direct
   * Voice → download → Whisper STT
4. Finance engine analyzes data
5. Context + user query → LLM
6. LLM generates insights
7. Optional: convert to speech
8. Send response back via Twilio

---

## 💡 Example Queries

* "How much did I spend on groceries?"
* "Am I spending too much on games?"
* "Give me summary of my expenses"
* (Voice) "How much did I spend this month?"

---

## 🧠 Key Concepts Implemented

* LLM + Structured Data Integration
* Retrieval-Augmented Generation (RAG-like flow)
* Conversational Memory
* Multimodal Input (Text + Voice)
* Real-time AI inference pipeline

---

## 🚀 Future Improvements

* Switch CSV → SQLite / PostgreSQL
* Add user authentication
* Deploy on AWS / GCP
* Add dashboards (React frontend)
* Multi-user financial tracking
* Budget alerts & notifications

---


