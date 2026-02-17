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
    /* Powiększamy czcionkę wzorów dla lepszej czytelności */
    .katex { font-size: 1.2em !important; }
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
def get_visual_response(text, img):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # SYSTEM PROMPT: FORMAT BLOKOWY (WIZUALNA SEPARACJA)
    system_prompt = """
    Jesteś nauczycielem fizyki. Twoim priorytetem jest CZYTELNOŚĆ.
    Uczeń musi widzieć różnicę między słowem a liczbą.
    
    ZASADA GŁÓWNA:
    Każdy wzór matematyczny i każde podstawienie liczb MUSI być w osobnej linii, wyśrodkowane (używaj podwójnego dolara: $$ ... $$).
    
    STRUKTURA ODPOWIEDZI (Krok po kroku):
    
    1. **Dane i Szukane**
       Wypisz je krótko od myślników.
       
    2. **Krok 1: [Nazwa]**
       Napisz 1 zdanie wyjaśnienia po polsku (np. "Liczymy siłę wypadkową").
       Dopiero POD SPODEM wstaw blok matematyczny ze wzorem:
       $$ F = m \\cdot a $$
       I pod spodem podstawienie:
       $$ F = 10 \\cdot 5 $$
       
    3. **Krok 2: [Nazwa]**
       Znowu tekst wyjaśnienia.
       I znowu blok matematyczny pod spodem.
       
    4. **Wynik**
       Na końcu podaj wynik w ramce lub pogrubiony.
    
    WAŻNE:
    - Wszystkie obliczenia wykonuj w ukrytym bloku ```python ... ``` (dla poprawności), ale w tekście pokazuj tylko gotowe liczby.
    - Nie zlewaj tekstu ze wzorami. Wzór ma być królem ekranu.
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

if st.button("Rozwiąż czytelnie 👁️", type="primary", use_container_width=True):
    if task or file:
        with st.spinner("Rozpisuję wzory..."):
            img = Image.open(file) if file else None
            
            try:
                full_response = get_visual_response(task, img)
                
                # Logika ukrywania kodu Python
                if "```python" in full_response:
                    parts = full_response.split("```python")
                    visible_text = parts[0]
                    code_part = parts[1].split("```")[0]
                    text_after = parts[1].split("```")[1] if len(parts[1].split("```")) > 1 else ""
                    
                    # Uruchamiamy Python w tle (dla pewności wyniku)
                    execute_hidden_code(code_part)
                    
                    # Wyświetlamy tekst (Streamlit sam sformatuje $$...$$ jako blok centralny)
                    st.markdown(visible_text + text_after)
                else:
                    st.markdown(full_response)
                    
            except Exception as e:
                st.error("Błąd generowania.")
