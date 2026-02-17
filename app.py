import streamlit as st
import google.generativeai as genai
from PIL import Image
import io  # [NOWOŚĆ] Do przechwytywania wyników kodu
import sys # [NOWOŚĆ] Do obsługi wyjścia systemowego (print)

# --- KONFIGURACJA ---
st.set_page_config(page_title="FizykAI - Hybrid Engine", page_icon="⚛️", layout="wide") # [ZMIANA] Layout wide dla lepszej czytelności
st.title("⚛️ FizykAI - Silnik Hybrydowy")
st.caption("Powered by Gemini 2.5 Flash + Python Runtime") # [ZMIANA] Nowy opis

# --- KLUCZ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Brak klucza API w Secrets.")

# --- [NOWOŚĆ] FUNKCJA WYKONUJĄCA KOD PYTHON ---
# To jest serce zmiany. Ta funkcja bierze tekst kodu od AI i uruchamia go na serwerze.
def execute_python_code(code_str):
    output_capture = io.StringIO()
    sys.stdout = output_capture # Przekierowujemy 'print' do naszej zmiennej
    
    try:
        # Tworzymy czyste środowisko dla kodu
        local_vars = {}
        exec(code_str, {}, local_vars)
        result = output_capture.getvalue()
        return result, True # Zwracamy wynik i sukces
    except Exception as e:
        return f"Błąd obliczeń: {e}", False # Zwracamy błąd
    finally:
        sys.stdout = sys.__stdout__ # Sprzątamy (przywracamy normalne działanie print)

# --- MÓZG (GEMINI 2.5 FLASH) ---
def get_gemini_response(text, img):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    parts = []
    
    # [ZMIANA] NOWY SYSTEM PROMPT (INSTRUKCJA)
    # Zabraniamy AI liczyć w pamięci. Zmuszamy do pisania kodu.
    system_prompt = """
    Jesteś nauczycielem fizyki i programistą Python.
    Twoim zadaniem jest rozwiązanie problemu w dwóch etapach:
    1. ANALIZA FIZYCZNA: Wypisz Dane, Szukane i Wzory (używaj LaTeX). Wyjaśnij tok rozumowania.
    2. OBLICZENIA (PYTHON):
       - NIE licz ręcznie.
       - Napisz kod w Pythonie, który wykona obliczenia.
       - Kod umieść w bloku: ```python ... ```
       - Wynik wypisz funkcją print().
    """
    
    parts.append(system_prompt)
    
    if text: parts.append(f"Zadanie: {text}")
    if img: parts.append(img)
    
    response = model.generate_content(parts)
    return response.text

# --- INTERFEJS ---
# [ZMIANA] Dzielimy ekran na dwie kolumny: Zadanie i Obrazek
col1, col2 = st.columns([1, 1])

with col1:
    text_input = st.text_area("Treść zadania:", height=150)

with col2:
    file = st.file_uploader("Zdjęcie (opcjonalnie):", type=["jpg", "png", "jpeg"])
    image = None
    if file:
        image = Image.open(file)
        st.image(image, caption="Analiza wizualna", use_column_width=True)

if st.button("🚀 Rozwiąż z Weryfikacją Kodem"):
    if not api_key:
        st.error("Najpierw ustaw klucz API w ustawieniach!")
    else:
        with st.spinner("Gemini 2.5 analizuje fizykę i pisze kod..."):
            try:
                # 1. Pobieramy pełną odpowiedź od AI
                full_response = get_gemini_response(text_input, image)
                
                # [NOWOŚĆ] LOGIKA ROZDZIELANIA TEKSTU OD KODU
                # Sprawdzamy, czy AI wygenerowało kod Pythona
                if "```python" in full_response:
                    parts = full_response.split("```python")
                    explanation = parts[0] # To jest tekst przed kodem
                    
                    # Wyciągamy kod (usuwamy końcowe ```)
                    code_part = parts[1].split("```")[0]
                    
                    # 2. Wyświetlamy wyjaśnienie fizyczne
                    st.markdown("### 1. Analiza Fizyczna")
                    st.markdown(explanation)
                    
                    # 3. Wyświetlamy i uruchamiamy kod
                    st.markdown("### 2. Weryfikacja Obliczeń (Python)")
                    with st.expander("Kliknij, aby zobaczyć kod źródłowy wygenerowany przez AI"):
                        st.code(code_part, language='python')
                    
                    # Uruchomienie kodu!
                    calc_result, success = execute_python_code(code_part)
                    
                    if success:
                        st.success("✅ Wynik obliczony przez Python:")
                        st.text(calc_result) # Wyświetla to, co wypisał print()
                    else:
                        st.error("❌ Błąd w kodzie AI:")
                        st.text(calc_result)
                        
                    # Jeśli AI napisało coś jeszcze po kodzie (np. podsumowanie)
                    if len(parts[1].split("```")) > 1:
                        st.markdown(parts[1].split("```")[1])

                else:
                    # Jeśli AI z jakiegoś powodu nie napisało kodu, wyświetlamy sam tekst
                    st.warning("⚠️ AI podało rozwiązanie opisowe (bez weryfikacji kodem).")
                    st.markdown(full_response)

            except Exception as e:
                st.error(f"Wystąpił błąd krytyczny: {e}")
