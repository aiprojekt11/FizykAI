import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="FizykAI", page_icon="⚛️", layout="centered")

# --- KLUCZ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Brak klucza API. Ustaw GOOGLE_API_KEY w Streamlit Secrets.")

# --- INSTRUKCJA DLA AI ---
SYSTEM_PROMPT = """
Jesteś nauczycielem fizyki (poziom rozszerzony/studia).
1. Rozwiązuj zadania krok po kroku: DANE, SZUKANE, WZÓR, OBLICZENIA, WYNIK.
2. Używaj LaTeX do wzorów.
3. Tłumacz tak, by uczeń zrozumiał.
4. Nie podawaj tylko wyniku!
"""

def get_gemini_response(text, img):
    model = genai.GenerativeModel('gemini-1.5-flash')
    parts = [SYSTEM_PROMPT]
    if text: parts.append(text)
    if img: parts.append(img)
    return model.generate_content(parts).text

# --- WYGLĄD APLIKACJI ---
st.title("⚛️ FizykAI - Twój Tutor")
st.markdown("Wklej treść zadania lub zdjęcie.")

text = st.text_area("Treść zadania:")
file = st.file_uploader("Zdjęcie (opcjonalnie):", type=["jpg", "png", "jpeg"])

if st.button("🚀 Rozwiąż"):
    if not text and not file:
        st.warning("Podaj treść lub zdjęcie!")
    else:
        with st.spinner("Liczenie..."):
            try:
                img = Image.open(file) if file else None
                if img: st.image(img, caption="Twoje zdjęcie")
                response = get_gemini_response(text, img)
                st.markdown("### Rozwiązanie:")
                st.markdown(response)
            except Exception as e:
                st.error(f"Błąd: {e}")
