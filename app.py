import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client
import os

# --- 1. SEO & PAGE CONFIG (Google Search ke liye) ---
st.set_page_config(
    page_title="Ai Ved Pro | Bihar's First Smart AI Chatbot",
    page_icon="🤖",
    layout="wide",
)

# Google Metadata (Taaki Google ise pehchane)
st.markdown("""
    <head>
        <meta name="description" content="Ai Ved Pro is Bihar's first AI chatbot for JEE, BSEB students. Built by Ved from Dharupur, Bihar.">
        <meta name="keywords" content="Ai Ved, Ai Ved Pro, Bihar AI, Ved AI, Dharupur AI, Best AI for JEE students">
    </head>
""", unsafe_allow_html=True)

# --- 2. DATABASE & API CONNECTIONS ---
# Iske liye tumhare Streamlit Secrets mein saari Keys honi chahiye
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. LOGIN / SIGNUP LOGIC ---
def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.rerun()
    except:
        st.error("Login Fail: Email ya Password galat hai!")

def signup_user(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        st.success("Account ban gaya! Ab Login karo.")
    except Exception as e:
        st.error(f"Sign-up Fail: {e}")

# --- 5. UI LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Ai Ved - Welcome Area")
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
    st.sidebar.title(f"👋 Welcome, {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

    st.title("🤖 Ai Ved Pro - Bihar's Smartest AI")
    st.info("Main abhi Internet (Tavily) se bhi juda hoon aur Groq se bhi!")

    # Chat History dikhao
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    user_input = st.chat_input("Pucho bhai, kya jaanna hai?")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Ved bhai, ruko... internet par dhoond raha hoon..."):
                # 1. Search on Internet (Tavily)
                search_result = tavily.search(query=user_input, search_depth="advanced")
                context = search_result['results']
                
                # 2. Generate Answer with Groq
                prompt = f"System: Use this context to answer: {context}\nUser: {user_input}"
                completion = groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}]
                )
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})