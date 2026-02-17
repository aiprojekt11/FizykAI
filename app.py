import streamlit as st
import google.generativeai as genai
from PIL import Image


# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="FizykAI", page_icon="⚛️")

# --- KLUCZ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Brak klucza API w Secrets.")

# --- MÓZG (Logika) ---
def get_gemini_response(text, img):
    # Model Flash jest najszybszy i najtańszy/darmowy
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    parts = []
    # System Prompt (Instrukcja)
    parts.append("Jesteś nauczycielem fizyki. Rozwiązuj zadania krok po kroku (Dane, Szukane, Wzór).")
    
    if text: parts.append(text)
    if img: parts.append(img)
    
    response = model.generate_content(parts)
    return response.text

# --- WYGLĄD ---
st.title("⚛️ FizykAI - Twój Tutor")
st.info("Wersja Stabilna: Gemini 1.5 Flash")

text = st.text_area("Treść zadania:", height=100)
file = st.file_uploader("Zdjęcie (opcjonalnie):", type=["jpg", "png", "jpeg"])

if st.button("🚀 Rozwiąż"):
    if not api_key:
        st.error("Najpierw ustaw klucz API w ustawieniach!")
    else:
        with st.spinner("Analizuję fizykę..."):
            try:
                img = Image.open(file) if file else None
                if img: st.image(img, caption="Twoje zdjęcie")
                
                response = get_gemini_response(text, img)
                
                st.markdown("### Rozwiązanie:")
                st.markdown(response)
            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")
