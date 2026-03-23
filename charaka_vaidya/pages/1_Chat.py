import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from frontend.components.sidebar import render_sidebar
from frontend.components.source_panel import render_sources as render_source_panel
from frontend.components.voice_button import render_voice_input
from frontend.components.speak_button import render_speak_button
from frontend.components.uhc_widget import render_uhc_widget
from frontend.styles.theme import inject_theme
from core.i18n import t
from pipeline.intent_classifier import classify_intent
from pipeline.safety_filter import check_safety
from pipeline.context_builder import build_context
from pipeline.llm_engine import generate_response
from pipeline.response_formatter import format_response

st.set_page_config(page_title="Consult Vaidya", page_icon="💬", layout="wide")
inject_theme()
render_sidebar()

st.title(f"💬 {t('chat_title')}")
st.caption(t("chat_subtitle"))

# ── UHC Widget ────────────────────────────────────────────────────────────────
render_uhc_widget()

# ── Chat History ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "simple_mode" not in st.session_state:
    st.session_state["simple_mode"] = False

# ── Toolbar ───────────────────────────────────────────────────────────────────
col_mode, col_clear = st.columns([3, 1])
with col_mode:
    st.session_state["simple_mode"] = st.toggle(t("chat_simple_mode"), value=st.session_state["simple_mode"])
with col_clear:
    if st.button(t("chat_clear"), use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# ── Render Chat History ───────────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"📚 {t('chat_sources_label')}"):
                render_source_panel(msg["sources"])
        if msg["role"] == "assistant":
            render_speak_button(msg["content"], key=f"speak_{msg.get('ts', id(msg))}")

# ── Voice Input ───────────────────────────────────────────────────────────────
with st.expander(f"🎙️ {t('voice_start')} (Groq Whisper)", expanded=False):
    voice_text = render_voice_input(key="chat_voice")
    if voice_text:
        st.session_state["pending_voice"] = voice_text

# ── Text Input (prefilled from voice if available) ───────────────────────────
pending = st.session_state.pop("pending_voice", None)
voice_origin = False
user_input = st.chat_input(
    placeholder=t("chat_placeholder"),
)
if pending and not user_input:
    user_input = pending
    voice_origin = True

# ── Quick Prompts ─────────────────────────────────────────────────────────────
if not st.session_state["messages"]:
    st.markdown(f"**{t('chat_try_asking')}**")
    QUICK = {
        "en": ["I have constant bloating and gas after meals",
               "Tell me about Ashwagandha benefits",
               "How should I structure my daily routine?"],
        "hi": ["मुझे खाने के बाद पेट फूलने की समस्या है",
               "अश्वगंधा के फायदे बताएं",
               "दैनिक दिनचर्या कैसे बनाएं?"],
        "gu": ["ખોરાક પછી પેટ ફૂલવાની સમસ્યા છે",
               "અશ્વગંધાના ફાયદા બતાવો",
               "દૈનિક દિનચર્યા કેવી રીતે બનાવી?"],
    }
    lang = st.session_state.get("lang", "en")
    prompts = QUICK.get(lang, QUICK["en"])
    cols = st.columns(len(prompts))
    for i, prompt in enumerate(prompts):
        if cols[i].button(prompt, key=f"quick_prompt_{i}", use_container_width=True):
            st.session_state["pending_query"] = prompt
            st.rerun()

# ── Handle pending query from quick prompts ──────────────────────────────────
pending_query = st.session_state.pop("pending_query", None)
if pending_query and not user_input:
    user_input = pending_query

# ── Process Query ─────────────────────────────────────────────────────────────
if user_input:
    import time

    # If query is from voice transcription, prefer detected transcription language.
    # Otherwise fall back to current UI language for consultation language.
    ui_lang_name = {
        "en": "English",
        "hi": "Hindi",
        "gu": "Gujarati",
    }.get(st.session_state.get("lang", "en"), "English")
    response_language = st.session_state.get("consult_lang_name") if voice_origin else ui_lang_name

    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        sources = []
        response_text = ""
        with st.spinner("🌿 Consulting the Charaka Samhita..."):
            try:
                # Classify intent first
                intent = classify_intent(user_input)

                # Check safety with intent
                is_emergency, emergency_msg = check_safety(user_input, intent)

                if is_emergency:
                    response_text = emergency_msg
                    sources = []
                else:
                    # Build context and generate response
                    context, sources = build_context(user_input, intent=intent)
                    raw = generate_response(
                        user_query=user_input,
                        context=context,
                        intent=intent,
                        response_language=response_language,
                        stream=False,
                    )
                    # format_response returns a dict; extract the text
                    formatted = format_response(raw, intent, sources)
                    response_text = formatted.get("text", raw) if isinstance(formatted, dict) else str(formatted)
                    # also update sources from formatted response
                    if isinstance(formatted, dict) and formatted.get("sources"):
                        sources = formatted["sources"]

            except Exception as e:
                response_text = f"⚠️ **Error:** {str(e)}\n\nPlease check your Groq API key in the sidebar."
                sources = []

        st.markdown(response_text)
        render_speak_button(response_text, key=f"speak_resp_{int(time.time())}")

        if sources:
            with st.expander(f"📚 {t('chat_sources_label')}"):
                render_source_panel(sources)

    ts = int(time.time())
    st.session_state["messages"].append({
        "role": "assistant",
        "content": response_text,
        "sources": sources,
        "ts": ts,
    })

st.markdown("---")
st.caption(t("disclaimer"))
