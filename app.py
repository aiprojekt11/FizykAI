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
    /* Powiększamy i centrujemy wzory matematyczne */
    .katex-display { margin: 1em 0; font-size: 1.3em; }
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
        exec(code_str, {}, {})
        return output_capture.getvalue().strip()
    except Exception:
        return None
    finally:
        sys.stdout = sys.__stdout__

# --- MÓZG (GEMINI 2.5 FLASH) ---
def get_clean_response(text, img):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # SYSTEM PROMPT: ZAKAZ HTML
    system_prompt = """
    Jesteś nauczycielem fizyki. Twoim priorytetem jest CZYTELNOŚĆ i PROSTOTA.
    
    ZASADY ABSOLUTNE (BŁĘDY KRYTYCZNE):
    1. ZAKAZ UŻYWANIA HTML: Nie wolno Ci pisać <div>, <span>, <br> ani żadnych stylów CSS. To psuje wyświetlanie!
    2. ZAKAZ RAMEK: Nie próbuj robić ramek wokół wyniku.
    
    WYMAGANY FORMAT (WIZUALNA SEPARACJA):
    
    1. **Dane:** Wypisz je od myślników.
    
    2. **Krok [Numer]: [Tytuł]**
       Napisz jedno zdanie wyjaśnienia.
       Dopiero W NOWEJ LINII wstaw wzór w bloku LaTeX (podwójny dolar):
       
       $$ WZÓR $$
       
       A pod nim podstawienie liczb:
       
       $$ PODSTAWIENIE $$
       
    3. **Wynik**
       Napisz słowo "Wynik:", a potem w nowej linii samą wartość w LaTeX:
       $$ WYNIK $$
    
    Wszystkie obliczenia wykonuj w ukrytym bloku ```python ... ```, ale uczniowi pokazuj tylko czyste liczby w LaTeX.
    """
    
    parts = [system_prompt]
    if text: parts.append(f"Zadanie: {text}")
    if img: parts.append(img)
    
    return model.generate_content(parts).text

# --- INTERFEJS ---
st.title("FizykAI")

col1, col2 = st.columns([3, 1])
with col1:
    task = st.text_area("Treść zadania:", height=100, placeholder="Wpisz treść...", label_visibility="collapsed")
with col2:
    file = st.file_uploader("📷", type=["jpg", "png"], label_visibility="collapsed")

if st.button("Rozwiąż 👁️", type="primary", use_container_width=True):
    if task or file:
        with st.spinner("Analizuję..."):
            img = Image.open(file) if file else None
            
            try:
                full_response = get_clean_response(task, img)
                
                # Logika ukrywania kodu Python
                if "```python" in full_response:
                    parts = full_response.split("```python")
                    visible_text = parts[0]
                    code_part = parts[1].split("```")[0]
                    text_after = parts[1].split("```")[1] if len(parts[1].split("```")) > 1 else ""
                    
                    # Uruchamiamy Python w tle (dla pewności)
                    execute_hidden_code(code_part)
                    
                    # Wyświetlamy tekst
                    st.markdown(visible_text + text_after)
                else:
                    st.markdown(full_response)
                    
            except Exception as e:
                st.error("Błąd generowania.")
