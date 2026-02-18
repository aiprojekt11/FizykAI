import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import sys
import re  # [NOWOŚĆ] Potrzebne do cięcia odpowiedzi na kawałki (Tekst/Kod)

# --- KONFIGURACJA ---
st.set_page_config(page_title="FizykAI - MultiStep", page_icon="⚛️", layout="wide")
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    .katex-display { margin: 1em 0; font-size: 1.2em; }
    /* Styl dla wyników pośrednich */
    .metric-box {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚛️ FizykAI - Silnik Kaskadowy")
st.caption("Step-by-Step Python Execution")

# --- API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Brak klucza API.")

# --- MÓZG (GEMINI 2.5 FLASH) ---
def get_gemini_response(text, img):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # [KLUCZOWA ZMIANA] PROMPT WYMUSZAJĄCY PRZEPLATANIE TEKSTU I KODU
    system_prompt = """
    Jesteś nauczycielem fizyki. Rozwiązuj zadania METODĄ MAŁYCH KROKÓW.
    
    ZASADA ŻELAZNA:
    NIGDY nie licz w pamięci. Jeśli masz cokolwiek policzyć (nawet proste dodawanie), musisz wstawić blok kodu Python.
    
    STRUKTURA ODPOWIEDZI (PRZEPLATANA):
    
    1. Napisz tekst wyjaśniający pierwszy krok (użyj wzoru w LaTeX: $$...$$).
    2. Wstaw blok kodu Python, który liczy TYLKO ten krok:
       ```python
       # Definiujemy zmienne
       m = 10
       a = 5
       F = m * a
       print(f"{F} N") # Wypisz wynik z jednostką
       ```
    3. Napisz tekst wyjaśniający drugi krok.
    4. Wstaw kolejny blok kodu Python (zmienne z poprzedniego kroku są pamiętane!):
       ```python
       s = 100
       W = F * s  # Używamy F z poprzedniego kodu!
       print(f"{W} J")
       ```
    5. Na końcu podsumuj wynik.

    PAMIĘTAJ: 
    - Zakaz HTML.
    - Wzory w LaTeX ($$...$$).
    - Kod Python musi być wykonywalny.
    """
    
    parts = [system_prompt]
    if text: parts.append(f"Zadanie: {text}")
    if img: parts.append(img)
    
    return model.generate_content(parts).text

# --- FUNKCJA WYKONUJĄCA KOD (Z PAMIĘCIĄ) ---
def execute_step(code_str, global_vars):
    output_capture = io.StringIO()
    sys.stdout = output_capture
    
    try:
        # Używamy global_vars jako pamięci podręcznej między krokami!
        exec(code_str, global_vars)
        result = output_capture.getvalue().strip()
        return result, True
    except Exception as e:
        return f"Błąd w kodzie: {e}", False
    finally:
        sys.stdout = sys.__stdout__

# --- INTERFEJS ---
col1, col2 = st.columns([1, 1])
with col1:
    text_input = st.text_area("Treść zadania:", height=150)
with col2:
    file = st.file_uploader("Zdjęcie:", type=["jpg", "png", "jpeg"])

if st.button("🚀 Rozwiąż Kaskadowo", type="primary"):
    if not api_key:
        st.error("Brak klucza API!")
    else:
        with st.spinner("Liczenie krok po kroku..."):
            try:
                img = Image.open(file) if file else None
                full_response = get_gemini_response(text_input, img)
                
                # --- [MAGIA] ROZBIJANIE NA KAWAŁKI ---
                # Dzielimy odpowiedź po znacznikach ```python ... ```
                # Używamy regex, żeby wyłapać wszystko
                parts = re.split(r"```python(.*?)```", full_response, flags=re.DOTALL)
                
                # Tworzymy pamięć dla tej sesji zadania
                session_memory = {} 
                
                # Iterujemy po kawałkach
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        # Parzyste indeksy (0, 2, 4...) to TEKST od nauczyciela
                        st.markdown(part)
                    else:
                        # Nieparzyste indeksy (1, 3, 5...) to KOD PYTHON
                        code_to_run = part.strip()
                        
                        # Uruchamiamy kod, przekazując mu pamięć (session_memory)
                        result, success = execute_step(code_to_run, session_memory)
                        
                        if success:
                            # Wyświetlamy wynik obliczeń w ładnym pudełku
                            if result:
                                st.markdown(f'<div class="metric-box">🧮 Wynik obliczeń: {result}</div>', unsafe_allow_html=True)
                        else:
                            st.error(f"Błąd obliczeń: {result}")
                            
            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")
