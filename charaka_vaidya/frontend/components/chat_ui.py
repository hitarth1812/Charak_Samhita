import streamlit as st
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

def render_message(role: str, content: str):
    if role == "user":
        st.markdown(f'<div class="user-bubble">👤 {content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-bubble">🌿 {content}</div>', unsafe_allow_html=True)

def call_chat_api(query: str, history: list, simple_mode: bool = False) -> dict:
    """Try FastAPI backend first; fall back to direct pipeline call."""
    import requests
    try:
        resp = requests.post(
            f"{API_BASE}/chat",
            json={"query": query, "history": history, "simple_mode": simple_mode},
            timeout=300,
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.ConnectionError:
        pass
    return _direct_pipeline(query, history)

def _direct_pipeline(query: str, history: list) -> dict:
    """Direct in-process call when FastAPI server is not running."""
    try:
        # Apply session API key to environment before calling pipeline
        groq_key = st.session_state.get("groq_api_key", "")
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
        llm_model = st.session_state.get("llm_model", "llama-3.3-70b-versatile")
        os.environ["LLM_MODEL"] = llm_model

        from pipeline.intent_classifier import classify_intent
        from pipeline.safety_filter import check_safety
        from pipeline.context_builder import build_context
        from pipeline.llm_engine import generate_response
        from pipeline.response_formatter import format_response

        intent = classify_intent(query)
        is_emergency, emsg = check_safety(query, intent)
        if is_emergency:
            return {"answer": emsg, "intent": "emergency",
                    "sources": [], "has_disclaimer": True, "is_emergency": True}

        context, sources = build_context(query, intent)
        raw = generate_response(query, context, history, intent)
        fmt = format_response(raw, intent, sources)
        return {**fmt, "is_emergency": False}

    except RuntimeError as e:
        if "Vector store not found" in str(e):
            return {
                "answer": "⚠️ **Vector store not found.**\n\nRun this once to index the PDF:\n```bash\npython scripts/ingest.py\n```",
                "intent": "error", "sources": [], "has_disclaimer": False, "is_emergency": False,
            }
        return {"answer": f"⚠️ **Error:** {e}", "intent": "error",
                "sources": [], "has_disclaimer": False, "is_emergency": False}
    except Exception as e:
        return {"answer": f"⚠️ **Error:** {e}",
                "intent": "error", "sources": [], "has_disclaimer": False, "is_emergency": False}

def init_chat_state():
    if "messages"     not in st.session_state: st.session_state.messages     = []
    if "last_sources" not in st.session_state: st.session_state.last_sources = []
