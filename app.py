import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import sys

# --- KONFIGURACJA UI ---
st.set_page_config(page_title="FizykAI", page_icon="⚛️")
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

# --- SILNIK UKRYTEGO PYTHONA (DLA PRECYZJI) ---
def execute_hidden_code(code_str):
    output_capture = io.StringIO()
    sys.stdout = output_capture
    try:
        exec(code_str, {}, {})
        return output_capture.getvalue().strip()
    except Exception:
        return None
    finally:
        sys.stdout = sys.__stdout__

# --- MÓZG (GEMINI 2.5 FLASH) ---
def get_academic_response(text, img):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # SYSTEM PROMPT: STYL AKADEMICKI / PODRĘCZNIKOWY
    system_prompt = """
    Jesteś profesjonalnym nauczycielem fizyki. Twoim celem jest generowanie idealnych, wzorcowych rozwiązań zadań.
    
    STYL ODPOWIEDZI:
    Ma być identyczny jak w dobrym podręczniku lub kluczu maturalnym. Konkretny, numerowany, uporządkowany.

    WYMAGANA STRUKTURA (Trzymaj się jej sztywno):
    
    1. Dane wejściowe
       - Wypisz zmienne z treści zadania.
       - Jeśli trzeba, przekonwertuj jednostki na SI (np. cm² na m²) i pokaż to.
       
    2. [Nazwa Kroku Fizycznego, np. Wyznaczenie Siły]
       - Napisz z jakiego prawa korzystasz (np. "Z II zasady dynamiki...").
       - Podaj wzór w LaTeX (np. $F = m \\cdot a$).
       - Podstaw wartości liczbowe do wzoru (np. $F = 10 \\cdot 5$).
       
    3. [Kolejny Krok - jeśli potrzebny]
       - Analogicznie: Prawo -> Wzór -> Podstawienie.
       
    4. Wynik
       - Podaj ostateczną odpowiedź pełnym zdaniem.
    
    INSTRUKCJA TECHNICZNA:
    - Wszystkie obliczenia wykonuj w ukrytym bloku ```python ... ``` dla pewności, ale w tekście wyjściowym pokazuj tylko wynik (nie pokazuj kodu uczniowi).
    - Używaj LaTeX do wszystkich wzorów matematycznych.
    - Bądź precyzyjny.
    """
    
    parts = [system_prompt]
    if text: parts.append(f"Zadanie do rozwiązania: {text}")
    if img: parts.append(img)
    
    return model.generate_content(parts).text

# --- INTERFEJS ---
st.title("FizykAI")
st.caption("Rozwiązania krok po kroku.")

col1, col2 = st.columns([3, 1])
with col1:
    task = st.text_area("Treść zadania:", height=100, placeholder="Wklej zadanie...", label_visibility="collapsed")
with col2:
    file = st.file_uploader("📷", type=["jpg", "png"], label_visibility="collapsed")

if st.button("Rozwiąż krok po kroku 📝", type="primary", use_container_width=True):
    if task or file:
        with st.spinner("Generuję rozwiązanie..."):
            img = Image.open(file) if file else None
            
            try:
                full_response = get_academic_response(task, img)
                
                # Logika ukrywania kodu Python (Code Execution w tle)
                if "```python" in full_response:
                    parts = full_response.split("```python")
                    # To co widzi uczeń (Tekst przed kodem)
                    visible_text = parts[0]
                    
                    # Kod i ewentualny tekst po nim
                    code_part = parts[1].split("```")[0]
                    text_after = parts[1].split("```")[1] if len(parts[1].split("```")) > 1 else ""
                    
                    # Uruchamiamy Python dla pewności (żeby model się nie pomylił w obliczeniach)
                    # Choć w tym stylu model często wpisuje wynik od razu w tekst
                    execute_hidden_code(code_part)
                    
                    # Wyświetlamy całość (bez kodu)
                    st.markdown(visible_text + text_after)
                else:
                    st.markdown(full_response)
                    
            except Exception as e:
                st.error("Wystąpił błąd podczas generowania rozwiązania.")
