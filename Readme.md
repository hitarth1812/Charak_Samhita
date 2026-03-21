# 🌿 Charaka Vaidya

> RAG-powered Ayurvedic AI grounded in the Charaka Samhita  
> **LLM: Groq** | **Embeddings: HuggingFace (local)** | **Vector DB: ChromaDB (local)**

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env → add your GROQ_API_KEY (free at console.groq.com)

# 3. Add Charaka Samhita PDF
cp /your/path/charaka_samhita.pdf data/charaka_samhita.pdf

# 4. Index the PDF into ChromaDB  (run ONCE)
python scripts/ingest.py

# 5a. Start FastAPI backend  (Terminal 1)
uvicorn api.main:app --reload --port 8000

# 5b. Start Streamlit frontend  (Terminal 2)
streamlit run app.py
```

> 💡 **No FastAPI?** The Streamlit app auto-falls back to direct in-process pipeline calls.

---

## 🔑 API Keys Needed

| Service | Key Required | Where to Get |
|---|---|---|
| **Groq** (LLM) | ✅ Yes — free | [console.groq.com](https://console.groq.com) |
| HuggingFace Embeddings | ❌ No | Runs locally |
| ChromaDB Vector Store | ❌ No | Runs locally |

Add your key to `.env` **or** paste it directly in the sidebar at runtime.

---

## 🧠 Available Groq Models

| Model | Speed | Context | Best For |
|---|---|---|---|
| `llama-3.3-70b-versatile` | Fast | 128K | Best quality (default) |
| `llama-3.1-8b-instant` | Fastest | 128K | Quick responses |
| `mixtral-8x7b-32768` | Fast | 32K | Long conversations |
| `gemma2-9b-it` | Fast | 8K | Lightweight |

---

## 📁 Project Structure

```
charaka_vaidya/
├── app.py                     ← Streamlit home (entry point)
├── requirements.txt           ← groq + langchain + chromadb + streamlit
├── .env.example               ← Only GROQ_API_KEY needed
├── core/
│   ├── config.py              ← Groq + HuggingFace + Chroma config
│   ├── constants.py           ← Doshas, Sthanas, Glossary
│   └── prompts.py             ← 4-layer system prompt
├── rag/
│   ├── document_loader.py     ← PDF → chunks with Sthana metadata
│   ├── embedder.py            ← HuggingFace embeddings + ChromaDB
│   ├── retriever.py           ← Semantic search
│   └── reranker.py            ← Sthana-weighted re-ranking
├── pipeline/
│   ├── intent_classifier.py   ← health/herb/dosha/emergency
│   ├── safety_filter.py       ← Emergency escalation
│   ├── context_builder.py     ← RAG context assembly
│   ├── llm_engine.py          ← Groq API calls + streaming
│   └── response_formatter.py ← 4-layer output parsing
├── api/                       ← FastAPI backend (optional)
│   ├── main.py
│   ├── schemas.py
│   └── routes/ [chat, herbs, dosha, routine, samhita]
├── frontend/
│   ├── styles/theme.py        ← Ayurvedic CSS (terracotta/sage/gold)
│   ├── components/ [sidebar, chat_ui, source_panel]
│   └── pages/ [1_Chat, 2_Herb_Glossary, 3_Dosha_Quiz, 4_Daily_Routine]
├── scripts/
│   └── ingest.py              ← PDF → ChromaDB (run once)
└── data/
    ├── charaka_samhita.pdf    ← Place your PDF here
    ├── herbs_db.json
    └── dosha_quiz.json
```

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Intent Classifier ──► Safety Filter ──► 🚨 Emergency (if triggered)
    │
    ▼
ChromaDB Retrieval  (HuggingFace embeddings)
    │
    ▼
Sthana-Weighted Reranker
    │
    ▼
Context Builder
    │
    ▼
Groq LLaMA 3 70B  (4-Layer Response)
    │
    ▼
Response Formatter ──► Streamlit UI
```

---

⚠️ *Charaka Vaidya is an educational tool. Always consult a qualified Ayurvedic practitioner or medical doctor for health decisions.*
