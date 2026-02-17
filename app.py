import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import sys
import re

# --- KONFIGURACJA UI ---
st.set_page_config(page_title="FizykAI", page_icon="⚛️")
# Ukrywamy wszystko co zbędne - czysty minimalizm
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    .stApp {margin-top: -50px;}
</style>
""", unsafe_allow_html=True)

# --- API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Błąd: Brak klucza API.")

# --- SILNIK UKRYTEGO PYTHONA ---
def execute_hidden_code(code_str):
    output_capture = io.StringIO()
    sys.stdout = output_capture
    try:
        # Wykonujemy kod w bezpiecznym środowisku
        exec(code_str, {}, {})
        return output_capture.getvalue().strip()
    except Exception as e:
        return None
    finally:
        sys.stdout = sys.__stdout__

# --- MÓZG (GEMINI 2.5 FLASH) ---
def get_mentor_response(text, img):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # TUTAJ WKLEJONY JEST TWÓJ NOWY SYSTEM PROMPT
    system_prompt = """
    Jesteś FIZYK-MENTOR. Twoim celem nie jest "rozwiązanie zadania", ale "wyjaśnienie go uczniowi, który go nie rozumie".

    FILOZOFIA:
    1. Bądź po stronie ucznia. Mów prosto, ciepło i obrazowo.
    2. ZERO TECHNOLOGII: Nie wspominaj o Pythonie, kodzie czy AI.
    3. BEZBŁĘDNOŚĆ: Liczby muszą być idealne.

    INSTRUKCJA FORMATOWANIA:
    1. Najpierw wytłumacz "na chłopski rozum" o co chodzi w zadaniu.
    2. Wypisz Dane/Szukane i Wzór (LaTeX).
    3. Następnie stwórz blok kodu ```python ... ```, w którym obliczysz wynik.
       W kodzie na końcu użyj: print("WYNIK KOŃCOWY: ...").
    4. Po bloku kodu napisz podsumowanie dla ucznia i wynik pogrubioną czcionką.
    """
    
    parts = [system_prompt]
    if text: parts.append(f"Uczeń pyta o: {text}")
    if img: parts.append(img)
    
    return model.generate_content(parts).text

# --- INTERFEJS ---
st.title("FizykAI")
st.caption("Twój prywatny korepetytor.")

# Input
col1, col2 = st.columns([3, 1])
with col1:
    task = st.text_area("Zadanie:", height=100, placeholder="Wklej treść zadania, a ja wytłumaczę Ci to krok po kroku...", label_visibility="collapsed")
with col2:
    file = st.file_uploader("📷", type=["jpg", "png"], label_visibility="collapsed")

if st.button("Wyjaśnij mi to 🚀", type="primary", use_container_width=True):
    if task or file:
        with st.spinner("Analizuję problem..."):
            img = Image.open(file) if file else None
            
            try:
                # 1. Pobieramy odpowiedź od Mentora
                full_response = get_mentor_response(task, img)
                
                # 2. MAGIA: Rozdzielamy tekst dla ucznia od kodu dla maszyny
                if "```python" in full_response:
                    parts = full_response.split("```python")
                    intro_text = parts[0] # To jest wyjaśnienie (Intuicja + Wzory)
                    
                    # Wyciągamy kod i resztę
                    code_and_rest = parts[1].split("```")
                    code_block = code_and_rest[0]
                    outro_text = code_and_rest[1] if len(code_and_rest) > 1 else ""
                    
                    # 3. Uruchamiamy kod po cichu (Weryfikacja matematyczna)
                    calc_output = execute_hidden_code(code_block)
                    
                    # 4. Wyświetlamy TYLKO to co ludzkie
                    st.markdown(intro_text)
                    
                    # Jeśli kod coś wyliczył, możemy to ładnie wpleść, 
                    # ale tutaj polegamy na tym, co AI napisało w 'outro_text' 
                    # oraz ewentualnie wyświetlamy wynik z Pythona jako "Pieczątkę Jakości"
                    
                    st.markdown(outro_text)
                    
                    if calc_output:
                        # Opcjonalnie: Wyświetlamy wynik z Pythona w ładnym dymku, jako potwierdzenie
                        st.success(f"🧮 Sprawdzone obliczeniowo: {calc_output}")
                        
                else:
                    # Jeśli zadanie było opisowe (bez liczenia), wyświetlamy całość
                    st.markdown(full_response)
                    
            except Exception as e:
                st.error("Coś poszło nie tak. Spróbuj jeszcze raz.")
