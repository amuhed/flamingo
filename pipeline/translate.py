"""Translation using deep-translator (Google Translate, free)."""

from deep_translator import GoogleTranslator


def translate_to_english(text, source_lang="auto"):
    """Translate text to English. Returns original if already English or on error."""
    if not text or not text.strip():
        return text
    try:
        # deep-translator has a 5000 char limit per request
        if len(text) > 4900:
            text = text[:4900]
        result = GoogleTranslator(source=source_lang, target="en").translate(text)
        return result if result else text
    except Exception:
        return text
