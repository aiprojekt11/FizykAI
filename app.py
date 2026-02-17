import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="FizykAI - Gemini Edition")

# --- KLUCZ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Ustaw GOOGLE_API_KEY w Secrets.")

# --- MÓZG (Z LISTĄ REZERWOWĄ MODELI) ---
def get_gemini_response(text, img):
    # Próbujemy kolejno dostępnych modeli (od najnowszych do stabilnych)
    models_to_try = [
        'gemini-3-flash-preview', 
        'gemini-2.5-flash', 
        'gemini-2.0-flash', 
        'gemini-1.5-flash'
    ]
    
    last_error = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            parts = ["Jesteś nauczycielem fizyki. Rozwiązuj zadania krok po kroku.", text]
            if img: parts.append(img)
            
            response = model.generate_content(parts)
            return response.text, model_name
        except Exception as e:
            last_error = str(e)
            continue # Próbuj kolejny model z listy
            
    return f"Błąd: Żaden model nie odpowiedział. Ostatni błąd: {last_error}", None

# --- INTERFEJS ---
st.title("⚛️ FizykAI - Wersja Gemini")
user_text = st.text_area("Treść zadania:")
file = st.file_uploader("Zdjęcie:", type=["jpg", "png", "jpeg"])

if st.button("🚀 Rozwiąż"):
    with st.spinner("Szukam aktywnego modelu Gemini..."):
        img = Image.open(file) if file else None
        res, used_model = get_gemini_response(user_text, img)
        if used_model:
            st.success(f"Użyto modelu: {used_model}")
        st.markdown(res)
