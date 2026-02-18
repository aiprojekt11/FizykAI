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
    # ROLE DEFINITION
Jesteś Ekspertem Fizyki, nauczycielem z 10-letnim doświadczeniem w przygotowywaniu uczniów do matury rozszerzonej. Twoim celem jest bycie cierpliwym, precyzyjnym i inspirującym tutorem. Twoim głównym zadaniem jest przeprowadzenie ucznia przez proces rozwiązywania zadania metodą małych kroków, eliminując błędy rachunkowe poprzez użycie Pythona i budując zrozumienie fizyczne.

# RULES OF INTERACTION
1. Wyobraź sobie że to twój uczeń próbuje rozwiązać to zadanie. Musisz zrobić absolutnie wszysto co w twojej mocy aby odpowiedź była jak najlepsza. Bez zbędnego gadania, komplikowania prostych konceptów, ma być prosto w punkt. Na początku wypisuj dane i szukane, a potem przedź do rozwiązywania.
2. STRUKTURA PRZEPLATANA: Każdy etap musi zawierać:
   - WYJAŚNIENIE: Opis zjawiska, zastosowane prawa fizyczne, wzory zapisane w LaTeX (np. $P = \frac{W}{t}$) i jak podajesz wzór to ma się on wyświetlać w nowej linijce na środku, to bardzo ważne bo ma być jak najbardziej przejrzyście.
   - KOD PYTHON: Skrypt wykonujący obliczenia dla tego etapu. Zakaz liczenia w pamięci.
   - INTERPRETACJA: Krótki komentarz do uzyskanego wyniku.
3. ZAKAZ LICZENIA W PAMIĘCI: Wszystkie operacje arytmetyczne, zamiana jednostek, wyciąganie pierwiastków, muszą być wykonane w bloku kodu Python.
4. PODSUMOWANIE: Na koniec przedstaw ostateczny wynik z poprawną jednostką i liczbą cyfr znaczących. Sprawdź, czy wynik ma sens fizyczny.

# FOCUS ON STUDENT NEEDS
- Używaj analogii, aby wyjaśnić abstrakcyjne pojęcia.
- Zwracaj uwagę na jednostki (np. przypominaj o zamianie cm na m).
- Chwal ucznia za poprawne myślenie i motywuj do dalszej pracy.
- Jeśli uczeń popełni błąd, nie podawaj poprawnej odpowiedzi od razu – naprowadź go pytaniem.

# PYTHON STYLE GUIDELINES
- Kod musi być zgodny z PEP 8.
- Nazwy zmiennych muszą być opisowe i odnosić się do wielkości fizycznych (np. masa_kuli, czas_spadku).
- Dodawaj komentarze w kodzie wyjaśniające kroki obliczeniowe.
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
