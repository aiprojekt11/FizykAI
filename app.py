import streamlit as st
import google.generativeai as genai

st.title("Test Połączenia Gemini")

# Pobranie klucza
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("1. Klucz API wczytany poprawnie.")
except Exception as e:
    st.error(f"Błąd klucza: {e}")

if st.button("Uruchom test"):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Cześć, czy mnie słyszysz?")
        st.write("2. Odpowiedź AI:", response.text)
    except Exception as e:
        st.error(f"3. Błąd połączenia z modelem: {e}")
