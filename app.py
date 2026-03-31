import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="🤖", layout="wide")

# --- DATABASE CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- SESSION STATE FOR LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- LOGIN / SIGNUP FUNCTIONS ---
def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.rerun()
    except Exception as e:
        st.error("Login Fail: Email ya Password galat hai!")

def signup_user(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        st.success("Account ban gaya! Ab Login karo.")
    except Exception as e:
        st.error(f"Sign-up Fail: {e}")

# --- UI LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Ai Ved - Login Area")
    tab1, tab2 = st.tabs(["Login", "Sign-up"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login_user(email, password)
            
    with tab2:
        new_email = st.text_input("Naya Email")
        new_password = st.text_input("Naya Password", type="password")
        if st.button("Create Account"):
            signup_user(new_email, new_password)

else:
    # --- ASLI AI DASHBOARD (LOGIN HONE KE BAAD) ---
    st.sidebar.title(f"Welcome, {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🤖 Ai Ved Pro - Bihar's Smartest AI")
    
    # Yahan tumhara purana AI wala code (Groq chat aur Image Studio) aayega
    user_input = st.chat_input("Pucho bhai, kya puchna hai?")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        
        # Groq Call (Basic Example)
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": user_input}]
        )
        with st.chat_message("assistant"):
            st.write(completion.choices[0].message.content)