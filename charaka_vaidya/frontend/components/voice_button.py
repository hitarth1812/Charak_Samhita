"""
Voice input using st.audio_input (Streamlit 1.33+) + Groq Whisper via FastAPI backend.
GROQ_API_KEY stays server-side; the browser only sends audio bytes.
"""
import streamlit as st
import os
import hashlib
import requests
from charaka_vaidya.core.i18n import t, get_lang, get_bcp47
from charaka_vaidya.utils.logger import get_logger

logger = get_logger(__name__)

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8888")

def transcribe_audio(audio_bytes: bytes, lang: str = None) -> dict:
    """Call FastAPI backend to transcribe via Groq Whisper. Returns {text, detected_language, language_name}."""
    try:
        # Send audio to backend /transcribe endpoint
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        params = {}
        if lang:
            params["language"] = lang
            logger.info(f"🎤 Requesting transcription with explicit language: {lang}")
        else:
            logger.info(f"🎤 Requesting transcription with auto-detect")
        
        response = requests.post(f"{API_BASE}/transcribe", files=files, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            detected = data.get("detected_language", "en")
            lang_name = data.get("language_name", detected.upper())
            logger.info(f"✅ Transcription success: {lang_name} ({detected})")
            return {
                "text": data.get("text", ""),
                "detected_language": detected,
                "language_name": lang_name,
                "error": None
            }
        else:
            error_msg = response.json().get("detail", response.text)
            logger.error(f"Transcription API error: {error_msg}")
            return {"text": "", "detected_language": "en", "language_name": "English", "error": f"API error: {error_msg}"}
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to backend at {API_BASE}")
        return {"text": "", "detected_language": "en", "language_name": "English", "error": f"Backend not running at {API_BASE}. Start FastAPI on port 8888."}
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        return {"text": "", "detected_language": "en", "language_name": "English", "error": str(e)}

def render_voice_input(key: str = "voice_main") -> str | None:
    """
    Renders the voice input widget.
    Returns the transcribed text string if audio was recorded and transcribed,
    otherwise returns None.
    """
    st.markdown(f"**{t('voice_start')}** — record your question, then click Transcribe.")
    audio = st.audio_input(
        label=t("voice_start"),
        key=f"audio_input_{key}",
        label_visibility="collapsed",
    )

    if audio is not None:
        audio_bytes = audio.read()
        audio_hash = hashlib.sha1(audio_bytes).hexdigest()
        hash_key = f"voice_last_hash_{key}"

        # Avoid reprocessing the same audio blob after Streamlit reruns.
        if st.session_state.get(hash_key) == audio_hash:
            return None
        st.session_state[hash_key] = audio_hash

        logger.info(f"🎙️ Audio recorded: {len(audio_bytes)} bytes")
        
        with st.spinner(t("voice_transcribing")):
            result = transcribe_audio(audio_bytes)

        if result["error"]:
            st.error(f"⚠️ {result['error']}")
            logger.error(f"Transcription failed: {result['error']}")
            return None

        text = result["text"]
        detected = result["detected_language"]
        lang_name = result.get("language_name", detected.upper())

        if text:
            logger.info(f"✅ Transcription successful")
            logger.info(f"   Detected language (raw): {detected}")
            logger.info(f"   Text: {text[:100]}")

            # Persist detected language for downstream consultation response.
            st.session_state["consult_lang_code"] = detected.lower().strip()
            st.session_state["consult_lang_name"] = lang_name
            
            st.success(f"🎙️ *{t('voice_detected_lang')}: {detected.upper()}*")
            st.info(f"**Transcribed:** {text}")

            # Auto-switch app language if detected differs from current
            # Map language codes to supported UI languages
            # Whisper returns ISO 639-1 codes (en, hi, gu, fr, de, es, zh, ja, ko, ar, etc.)
            
            # Build comprehensive mapping for all 95+ Groq Whisper languages
            # Mapping for UI language switching (only for languages with UI translations)
            ui_lang_map = {
                "en": "en", "english": "en",
                "hi": "hi", "hindi": "hi",
                "gu": "gu", "gujarati": "gu",
            }
            
            detected_lower = detected.lower().strip()
            logger.info(f"   Language: {detected_lower}")
            
            # Try to map to UI language
            mapped_ui_lang = ui_lang_map.get(detected_lower)
            
            if mapped_ui_lang:
                # This language has UI translations
                current_lang = st.session_state.get("lang", "en")
                logger.info(f"   Current session lang: {current_lang}")
                logger.info(f"   Lang pinned: {st.session_state.get('lang_pinned', False)}")
                
                if mapped_ui_lang != current_lang:
                    if not st.session_state.get("lang_pinned", False):
                        logger.info(f"   🔄 Switching language: {current_lang} → {mapped_ui_lang}")
                        st.session_state["lang"] = mapped_ui_lang
                    else:
                        logger.info(f"   ⏸️ Language pinned, not switching")
                else:
                    logger.info(f"   ℹ️ Language already {mapped_ui_lang}, no switch needed")
            else:
                # Language detected but no UI translation available
                logger.info(f"   ℹ️ {lang_name}: Supported by Whisper, no UI translation yet")
                st.info(f"💬 Transcribed in {lang_name} — UI translations for this language coming soon!")

            return text
    return None
