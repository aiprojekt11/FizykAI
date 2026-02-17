import streamlit as st
import google.generativeai as genai

st.title("🔍 Skaner Modeli Google")

# 1. Konfiguracja
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("✅ Klucz API działa!")
except Exception as e:
    st.error(f"Błąd klucza: {e}")

# 2. Pobieranie listy modeli
if st.button("Pokaż dostępne modele"):
    try:
        st.info("Pytam serwery Google o listę...")
        
        # To jest ta funkcja, o którą prosił błąd
        models_iterator = genai.list_models()
        
        found_any = False
        st.write("### Twoja lista modeli:")
        
        for m in models_iterator:
            # Szukamy tylko modeli, które umieją pisać tekst (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                st.code(f"Nazwa: {m.name}")
                found_any = True
                
        if not found_any:
            st.warning("Połączono, ale lista modeli jest pusta. To może być problem z uprawnieniami klucza.")
            
    except Exception as e:
        st.error(f"Błąd podczas pobierania listy: {e}")
