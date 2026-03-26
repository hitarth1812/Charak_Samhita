🌍 MULTILINGUAL SUPPORT GUIDE — Charaka Vaidya
================================================

This system now supports 95+ languages for speech-to-text via Groq Whisper.
Hindi, English, and Gujarati have full UI translations.
All other languages are supported for transcription.

SUPPORTED LOCALES & LANGUAGES
==============================

### TIER 1: Full UI Translation (3 languages)
✅ English (en): Complete UI, strings, TTS
✅ Hindi (hi): Complete UI, strings, TTS with BCP-47 (hi-IN)
✅ Gujarati (gu): Complete UI, strings, TTS with BCP-47 (gu-IN)

Translation files:
  - charaka_vaidya/locales/en/translation.json
  - charaka_vaidya/locales/hi/translation.json
  - charaka_vaidya/locales/gu/translation.json

### TIER 2: Transcription Support (95+ languages)
Groq Whisper supports these languages for speech-to-text:

MAJOR LANGUAGES:
📍 Arabic (ar), Bengali (bn), Chinese (zh), French (fr), German (de)
📍 Japanese (ja), Korean (ko), Portuguese (pt), Russian (ru), Spanish (es)
📍 Thai (th), Turkish (tr), Vietnamese (vi)

SOUTH ASIAN LANGUAGES:
📍 Hindi (hi), Gujarati (gu), Punjabi (pa), Tamil (ta), Telugu (te)
📍 Kannada (kn), Malayalam (ml), Marathi (mr), Urdu (ur)
📍 Nepali (ne), Odia (or), Sinhala (si)

EUROPEAN LANGUAGES:
📍 Italian (it), Dutch (nl), Polish (pl), Greek (el), Czech (cs)
📍 Swedish (sv), Danish (da), Norwegian (no), Finnish (fi), Hungarian (hu)
📍 Romanian (ro), Bulgarian (bg), Croatian (hr), Serbian (sr), Ukrainian (uk)

AFRICAN LANGUAGES:
📍 Swahili (sw), Yoruba (yo), Igbo (ig), Hausa (ha), Somali (so)
📍 Amharic (am), Twi (tw)

And many more from Groq Whisper model.

ARCHITECTURE
=============

VOICE INPUT FLOW:
┌──────────────────────────────────────────────────────────┐
│ 1. User record audio in any language                     │
│    └─ Browser → Streamlit (via st.audio_input)           │
│                                                          │
│ 2. Frontend sends audio to backend                       │
│    └─ POST /transcribe with optional ?language=XX        │
│                                                          │
│ 3. Backend calls Groq Whisper                            │
│    └─ whisper-large-v3 model                             │
│    └─ Auto-detects if language not specified             │
│                                                          │
│ 4. Backend returns detected language code                │
│    └─ ISO 639-1 code (en, hi, gu, fr, de, etc.)         │
│    └─ Full language name                                 │
│                                                          │
│ 5. Frontend displays transcription                       │
│    └─ Shows detected language                            │
│    └─ Auto-switches UI if translation available          │
│    └─ For other languages: shows name, keeps UI as-is    │
│                                                          │
│ 6. User clicks "Listen" for text-to-speech               │
│    └─ Web Speech API with BCP-47 language tag            │
│    └─ Uses system default voice for language             │
└──────────────────────────────────────────────────────────┘

LANGUAGE DETECTION FLOW:
                        ┌─────────────────────────────┐
                        │ Streamlit st.audio_input()  │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
            ┌──────────▶│ POST /transcribe endpoint   │
            │           └──────────────┬──────────────┘
            │                          │
User records│                          ▼
            │           ┌──────────────────────────────┐
            └──────────▶│ Groq Whisper (auto-detect)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼ Returns: lang="gu"
                        ┌──────────────────────────────┐
                        │ Language mapping             │
                        │ gu → gu (supported in UI)    │
                        └──────────────┬───────────────┘
                                       │
            ┌──────────────────────────┘
            │
            ▼
        ┌──────────────────────┐
        │ UI switches to gu    │
        │ (if lang_pinned=false)
        └──────────────────────┘

ADDING NEW UI LANGUAGES
=========================

To add Spanish UI support (for example):

1. CREATE TRANSLATION FILE:
   charaka_vaidya/locales/es/translation.json
   
   {
     "language": "Español",
     "voice_start": "Preséntaré su pregunta",
     "voice_transcribing": "Transcribiendo...",
     "voice_detected_lang": "Idioma detectado",
     ...
   }

2. UPDATE i18n.py:
   SUPPORTED_LANGUAGES = {
       "en": ("English", "en-US"),
       "hi": ("हिंदी", "hi-IN"),
       "gu": ("ગુજરાતી", "gu-IN"),
       "es": ("Español", "es-ES"),  # ← Add this
   }

3. UPDATE voice_button.py:
   ui_lang_map = {
       "en": "en",
       "hi": "hi",
       "gu": "gu",
       "es": "es",  # ← Add this
       "spanish": "es",  # ← Add this
   }

4. UPDATE speak_button.py:
   In get_bcp47():
   return {
       "en": "en-US",
       "hi": "hi-IN",
       "gu": "gu-IN",
       "es": "es-ES",  # ← Add this
   }.get(lang, "en-US")

5. Test:
   - Go to Streamlit app
   - Change language preference to Spanish
   - Record in Spanish
   - Verify UI is in Spanish
   - Verify transcription is correct
   - Test TTS with Spanish voice

API ENDPOINTS
=============

POST /transcribe
────────────────
Record audio in ANY language, get automatic transcription.

URL: http://localhost:8888/transcribe
Method: POST

QUERY PARAMETERS:
  language (optional): ISO 639-1 code for explicit language
                      Omit for auto-detect
                      
Examples:
  /transcribe?language=hi     # Force Hindi
  /transcribe?language=es     # Force Spanish
  /transcribe                 # Auto-detect

REQUEST BODY (multipart/form-data):
  file: Audio file (WAV, MP3, OGG, FLAC, etc.)

RESPONSE (JSON):
  {
    "text": "Transcribed text in detected language",
    "detected_language": "hi",
    "language_name": "Hindi",
    "segments": [
      {"id": 0, "start": 0.0, "end": 2.5, "text": "..."},
      ...
    ]
  }

EXAMPLES:

curl -F "file=@audio_hindi.wav" \
     http://localhost:8888/transcribe

curl -F "file=@audio_spanish.wav" \
     -G --data-urlencode "language=es" \
     http://localhost:8888/transcribe

Python:
  import requests
  
  response = requests.post(
      "http://localhost:8888/transcribe",
      files={"file": ("audio.wav", audio_bytes, "audio/wav")},
      params={"language": "gu"}  # Optional
  )
  
  data = response.json()
  print(f"Text: {data['text']}")
  print(f"Language: {data['language_name']}")

TESTING WORKFLOW
====================

1. START BACKEND:
   cd charaka_vaidya
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8888
   
   Look for: "Uvicorn running on http://127.0.0.1:8888"

2. START STREAMLIT:
   Open NEW terminal:
   cd Charak_Samhita
   python -m streamlit run charaka_vaidya/pages/1_Chat.py
   
   Look for: "http://localhost:8501"

3. TEST A LANGUAGE:
   a) Open http://localhost:8501 in browser
   b) Go to "Chat" page
   c) Select "Voice Input" tab
   d) Record audio in target language (e.g., "नमस्ते")
   e) Check backend logs for:
      📥 Audio received: [bytes]
      🎤 Whisper Response:
         language attr: hi
      ✅ Normalized language code: hi
   f) Check Streamlit UI:
      - 🎙️ Detected lang: HI
      - Transcribed text shown in Hindi
      - If UI translation exists: Page switches language
   g) Click "Listen" button
      - Audio plays with appropriate voice

4. VERIFY LANGUAGE DETECTION:
   Record in different languages:
   
   ENGLISH:
   "Hello, I want to ask about Ayurveda"
   Expected: detected_language = "en"
   
   HINDI:
   "नमस्ते, मुझे आयुर्वेद के बारे में पूछना है"
   Expected: detected_language = "hi"
   
   GUJARATI:
   "નમસ્તે, આને આયુર્વેદ વિશે પૂછવું છે"
   Expected: detected_language = "gu"
   
   SPANISH:
   "Hola, quiero hacer preguntas sobre Ayurveda"
   Expected: detected_language = "es"
   
   FRENCH:
   "Bonjour, je veux poser des questions sur l'Ayurvéda"
   Expected: detected_language = "fr"

TROUBLESHOOTING
=================

PROBLEM: "ModuleNotFoundError: No module named 'frontend'"
────────────────────────────────────────────────────────
SOLUTION: Already fixed! Import paths now use try/except with fallbacks.
Just run from any directory:
  cd Charak_Samhita
  python -m streamlit run charaka_vaidya/pages/1_Chat.py

PROBLEM: Transcription fails for non-English
─────────────────────────────────────────────
SOLUTION: 
1. Check backend logs for error message
2. Verify audio quality (clear speech, mic volume ok)
3. Check file size: Audio should be >1KB
4. Try longer recording (5+ seconds)

PROBLEM: Language detected but UI doesn't switch
────────────────────────────────────────────────
SOLUTION:
1. Check if language has UI support (only en/hi/gu)
2. Uncheck "Pin Language" in sidebar if present
3. Check browser console for errors (F12)

PROBLEM: TTS plays in wrong language
────────────────────────────────────
SOLUTION:
1. Check browser language settings
2. Verify BCP-47 code is correct in speak_button.py
3. On Windows: Some languages may not have default voices
4. Try selecting system voice from browser

CURRENT STATUS
================

✅ Fixed: Import paths robust across all runs
✅ Fixed: ModuleNotFoundError resolved  
✅ Added: Support for 95+ languages (Groq Whisper)
✅ Added: Full language detection and normalization
✅ Added: Language names included in API response
✅ Added: Comprehensive language mapping
✅ Tested: Hindi, English, Gujarati
✅ Tested: Cross-directory imports

🟡 Coming Soon:
  - Additional UI translations (Spanish, French, etc.)
  - Language preference persistence
  - Multilingual RAG (Charaka Samhita in Hindi/Gujarati)
  - Voice-specific language selection UI

RESOURCES
===========

Groq Whisper Languages: 
  https://groq.com/openrouter-labs/whisper-large-v3

ISO 639-1 Codes:
  https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes

BCP-47 Language Tags:
  https://www.w3.org/International/questions/qa-what-is-language-tag

Web Speech API:
  https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

Contact: For questions about multilingual support, check the logs!
