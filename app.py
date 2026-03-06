import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import io

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="PhysiTutor v2.5", page_icon="⚛️", layout="centered")

# --- STYL CSS (Dark Mode Sci-Fi) ---
st.markdown("""
<style>
    .stApp {
        background-color: #020617;
        color: #ecfeff;
    }
    .stChatMessage {
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(6, 182, 212, 0.2);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: rgba(8, 145, 178, 0.2);
        border-color: rgba(6, 182, 212, 0.4);
    }
    /* Stylizacja renderowanych bloków SVG */
    .svg-container {
        background-color: #050B14;
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 10px;
        padding: 20px;
        margin: 20px auto;
        box-shadow: 0 0 20px rgba(0,229,255,0.15);
        display: flex;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """Rola: Jesteś ekspertem z fizyki i doświadczonym nauczycielem przygotowującym polskich uczniów do matury z fizyki na poziomie rozszerzonym. Twoja filozofia to absolutne skupienie na fundamentach i rozwiązywanie zadań najprościej, jak to tylko możliwe.

Zasady, których musisz bezwzględnie przestrzegać:
1. ROZPOZNAWANIE INTENCJI UCZNIA:
   - NOWE ZADANIE: Zastosuj rygorystyczną "Minimalistyczną Strukturę Odpowiedzi" (opisana na końcu).
   - PYTANIE DODATKOWE / KONTYNUACJA: Odpowiedz mu w sposób naturalny. Wyjaśnij wątpliwości.
2. SYMBOLE Z POLSKIEJ KARTY WZORÓW CKE (KRYTYCZNE):
   - Prędkość: $v$, $v_0$, Droga: $s$, Przyspieszenie dośrodkowe: $a_{do}$
   - Siła tarcia: $T$ lub $T_k$, $T_s$, Siła sprężystości: $F_s = -kx$
   - Moment siły: $M$ (bezwzględny zakaz używania greckiej litery tau), Praca: $W$
3. TYLKO WZORY FUNDAMENTALNE: Zawsze zaczynaj od absolutnych fundamentów. Zanim zapiszesz równanie, krótko wyjaśnij, Z CZEGO TO WYNIKA.
4. ZAWSZE WYJAŚNIAJ PRZYBLIŻENIA I ZAŁOŻENIA (KRYTYCZNE): Nigdy nie przeskakuj "oczywistych" kroków. Jeśli używasz przybliżeń (np. dla małych kątów wahadła $\\sin\\alpha \\approx \\alpha \\approx \\frac{x}{l}$), MUSISZ to wyraźnie napisać.
5. KOMPAKTOWE OBLICZENIA LICZBOWE: Kiedy podstawiasz liczby do wzoru, rób to w JEDNEJ ciągłej linii, stosując łańcuch znaków równości (zmienna = liczby = kroki = wynik z jednostką). Nie rozbijaj na wiele bloków.
6. FORMATOWANIE MATEMATYKI: Używaj WYŁĄCZNIE standardowego formatu LaTeX. Zawsze otaczaj symbole w tekście pojedynczymi dolarami.

7. ZADANIE: GENEROWANIE RYSUNKU TECHNICZNEGO (SVG) - KRYTYCZNE
Jeśli zadanie dotyczy: dynamiki (siły), kinematyki (rzuty, wykresy), optyki (soczewki, promienie) lub obwodów elektrycznych – TWOIM OBOWIĄZKIEM jest wygenerowanie rysunku technicznego.

WYMAGANIA DOTYCZĄCE RYSUNKU:
1. FORMAT: Wygeneruj czysty kod <svg> z atrybutem viewBox="0 0 400 300".
2. STYLIZACJA (Dark Mode Sci-Fi):
   - Tło: przezroczyste (nie definiuj fill dla całego svg).
   - Linie główne: kolor #00e5ff (neonowy cyjan), grubość 2px.
   - Wektory sił/ruchu: kolor #ff007b (neonowy róż), zakończone wyraźnym grotem.
   - Linie pomocnicze: kolor #444c99 (ciemny fiolet), przerywane (stroke-dasharray="5,5").
   - Tekst/Etykiety: kolor #ffffff, czcionka sans-serif, rozmiar 12px. Do oznaczania kątów używaj standardowych liter (np. alfa, 30°).
3. LOGIKA FIZYCZNA:
   - Wektory muszą odzwierciedlać rzeczywiste kierunki i proporcje.
   - Kąty muszą być zgodne z treścią zadania (użyj transform="rotate(kąt)" lub funkcji trygonometrycznych dla współrzędnych).
4. CZYSTOŚĆ: Nie używaj zewnętrznych bibliotek. Tylko tagi: <line>, <circle>, <rect>, <path>, <text>, <polygon>, <g>.

UMIEJSCOWIENIE DIAGRAMU: 
Kod SVG umieść bezpośrednio w odpowiedzi, otoczony blokiem:
[DIAGRAM_START]
<svg viewBox="0 0 400 300">...</svg>
[DIAGRAM_END]

8. PRZESŁANE ZDJĘCIA ZADAŃ: Odczytaj treść, tabele i wykresy ze zdjęcia, a następnie rozwiąż zadanie.
9. Minimalistyczna Struktura Odpowiedzi (DLA NOWYCH ZADAŃ):
   - 💡 Zrozumienie zjawiska
   - [DIAGRAM_START]...[DIAGRAM_END] (jeśli dotyczy, wygeneruj tutaj SVG)
   - 📝 Dane: Wypisane z oficjalnymi symbolami.
   - 🎯 Szukane: Zdefiniowanie szukanej.
   - 🧠 Rozwiązanie: Krótkie uzasadnienie, wyprowadzenie wzoru końcowego (na literach), a na samym końcu zwięzłe podstawienie liczb w JEDNEJ LINII."""

# --- INICJALIZACJA API ---
# Wpisz swój klucz API Gemini
API_KEY = "AIzaSyBsMKgm4NzMXU-TacIhFXHinG2ckTQEp5M" 
genai.configure(api_key=API_KEY)

# Konfiguracja modelu
generation_config = {
  "temperature": 0.3, # Niska temperatura dla precyzyjnych obliczeń
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT,
    generation_config=generation_config
)

# --- STAN APLIKACJI (Zarządzanie historią) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Inicjalizacja modułu Edu-Core... Cześć! Jestem Twoim prywatnym asystentem z fizyki. Prześlij parametry zadania z fizyki rozszerzonej lub skan z książki, a zainicjuję algorytmy rozwiązywania i wygeneruję schematy wektorowe.", "image": None}
    ]
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- FUNKCJA RENDERUJĄCA TREŚĆ (Markdown + LaTeX + SVG) ---
def render_content(text):
    # Dzielenie tekstu na bloki diagramu i zwykły tekst
    parts = re.split(r'(\[DIAGRAM_START\].*?\[DIAGRAM_END\])', text, flags=re.DOTALL)
    for part in parts:
        if part.startswith('[DIAGRAM_START]') and part.endswith('[DIAGRAM_END]'):
            svg_content = part.replace('[DIAGRAM_START]', '').replace('[DIAGRAM_END]', '').strip()
            # Usuwanie ewentualnych tagów markdown ```xml lub ```svg
            svg_content = re.sub(r'^```(xml|svg|html)?\n?', '', svg_content, flags=re.IGNORECASE)
            svg_content = re.sub(r'\n?```$', '', svg_content, flags=re.IGNORECASE)
            
            # Renderowanie SVG w HTML
            html_string = f'<div class="svg-container">{svg_content}</div>'
            st.markdown(html_string, unsafe_allow_html=True)
        else:
            # Streamlit natywnie obsługuje LaTeX w $ oraz $$
            st.markdown(part)

# --- INTERFEJS UŻYTKOWNIKA ---
st.title("PhysiTutor v2.5")
st.caption("CKE Optimized • Core-Node Ready")

# Renderowanie historii czatu
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(msg["image"], width=300)
        render_content(msg["content"])

# --- POLE WPROWADZANIA I UPLOAD OBRAZU ---
uploaded_file = st.file_uploader("Załącz skan zadania (opcjonalnie)", type=["jpg", "jpeg", "png"])
prompt = st.chat_input("Wprowadź polecenie, dane zadania lub wklej skan...")

if prompt or uploaded_file:
    user_text = prompt if prompt else "Rozwiąż zadanie widoczne na zdjęciu."
    
    # Przetwarzanie obrazu
    img_obj = None
    if uploaded_file:
        img_obj = Image.open(uploaded_file)
    
    # Zapisz wiadomość użytkownika w historii UI
    st.session_state.messages.append({"role": "user", "content": user_text, "image": img_obj})
    
    with st.chat_message("user"):
        if img_obj:
            st.image(img_obj, width=300)
        st.markdown(user_text)

    # Wysłanie zapytania do Gemini
    with st.chat_message("assistant"):
        with st.spinner("Analiza protokołów i generowanie schematów..."):
            try:
                # Przygotowanie danych do wysłania
                content_to_send = [user_text]
                if img_obj:
                    content_to_send.append(img_obj)
                
                # Oczekiwanie na odpowiedź ze strumieniowaniem
                response = st.session_state.chat_session.send_message(content_to_send)
                ai_response = response.text
                
                render_content(ai_response)
                
                # Zapisz odpowiedź AI w historii UI
                st.session_state.messages.append({"role": "assistant", "content": ai_response, "image": None})
                
            except Exception as e:
                st.error(f"⚠️ Problem z połączeniem API: {str(e)}")
