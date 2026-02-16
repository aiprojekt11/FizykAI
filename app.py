import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- DIAGNOSTYKA (To nam powie prawdę) ---
import pkg_resources
try:
    ver = pkg_resources.get_distribution("google-generativeai").version
except:
    ver = "Nieznana"

# --- KONFIGURACJA ---
st.set_page_config(page_title="FizykAI", page_icon="⚛️")
st.title("⚛️ FizykAI - Twój Tutor")
st.caption(f"Status systemu: Biblioteka Google wersja {ver} (Wymagana: 0.8.3)")

# --- KLUCZ API ---
try:
    # Pobieramy klucz
    api_key = st.secrets["GOOGLE_API_KEY"]
    # Konfiguracja
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Problem z kluczem: {e}")

# --- MÓZG ---
def get_gemini_response(text, img):
    # Używamy najnowszego modelu
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    parts = []
    if text: parts.append(text)
    if img: parts.append(img)
    
    # Prosty prompt na start
    parts.append("Rozwiąż to zadanie z fizyki krok po kroku. Używaj LaTeX.")
    
    response = model.generate_content(parts)
    return response.text

# --- INTERFEJS ---
text = st.text_area("Treść zadania:")
file = st.file_uploader("Zdjęcie (opcjonalnie):", type=["jpg", "png", "jpeg"])

if st.button("🚀 Rozwiąż"):
    if not api_key:
        st.error("BRAK KLUCZA API W SEKRETACH!")
    else:
        with st.spinner("Liczenie..."):
            try:
                img = Image.open(file) if file else None
                if img: st.image(img, caption="Twoje zdjęcie")
                
                response = get_gemini_response(text, img)
                
                st.markdown("### Rozwiązanie:")
                st.markdown(response)
            except Exception as e:
                st.error(f"BŁĄD KRYTYCZNY: {e}")
                st.info("Jeśli widzisz błąd 404, sprawdź czy klucz API nie ma spacji na początku lub końcu!")
