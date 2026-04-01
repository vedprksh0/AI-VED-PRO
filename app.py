import streamlit as st
import random
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import google.generativeai as genai
from datetime import datetime

# --- 1. CONFIG ---
st.set_page_config(page_title="Karzon AI", page_icon="⚡", layout="wide")

# --- 2. ULTRA-PREMIUM DARK CSS (No More Chamak) ---
st.markdown("""
    <style>
        /* Global Background - Deep Dark */
        .stApp {
            background: #050505;
            color: #E0E0E0;
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Streamlit Branded Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Sidebar - Glass Effect */
        [data-testid="stSidebar"] {
            background-color: #0A0A0A !important;
            border-right: 1px solid #1E1E1E;
        }
        
        /* Professional Chat Bubbles (Gemini Style) */
        .stChatMessage {
            background-color: transparent !important;
            border: none !important;
            margin-bottom: 20px !important;
        }
        
        /* User Message Container */
        div[data-testid="stChatMessage"]:nth-child(even) {
            background-color: #1A1A1A !important;
            border-radius: 15px !important;
            padding: 15px !important;
        }

        /* Assistant Message Container */
        div[data-testid="stChatMessage"]:nth-child(odd) {
            background-color: transparent !important;
            padding: 15px !important;
        }

        /* Search Bar - Floating & Rounded */
        .stChatInputContainer {
            border: 1px solid #333 !important;
            border-radius: 50px !important;
            background: #111 !important;
            width: 70% !important;
            bottom: 30px !important;
        }

        /* Buttons & Sidebar Items */
        .stButton>button {
            border-radius: 20px;
            background: #1E1E1E;
            color: white;
            border: 1px solid #333;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: white;
            color: black;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #050505; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

        /* Branding Footer */
        .brand-footer {
            position: fixed;
            bottom: 10px;
            left: 20px;
            font-size: 10px;
            color: #555;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & ENGINES ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def get_2026_news(query):
    try:
        # Force 2026 Logic
        with DDGS() as ddgs:
            # Adding "2026 current" to ensure latest data
            search_query = f"{query} news April 2026 updates"
            results = [r['body'] for r in ddgs.text(search_query, max_results=3)]
        return "\n".join(results)
    except:
        return "Real-time search unavailable. Using neural knowledge."

# --- 4. AUTH & SESSION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 5. INTERFACE ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 100px; letter-spacing: -2px;'>Karzon AI</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        t1, t2 = st.tabs(["Log In", "Create Account"])
        with t1:
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.button("Access Karzon AI", use_container_width=True):
                try:
                    supabase.auth.sign_in_with_password({"email": e, "password": p})
                    st.session_state.logged_in = True
                    st.rerun()
                except: st.error("Invalid credentials.")
        with t2:
            ne = st.text_input("New Email")
            np = st.text_input("New Password", type="password")
            if st.button("Register Account", use_container_width=True):
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("Account created! Log in now.")

else:
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='letter-spacing:-1px;'>Karzon AI</h2>", unsafe_allow_html=True)
        if st.button("+ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.write("")
        st.markdown("<p style='font-size:10px; color:#555;'>RECENT SESSIONS</p>", unsafe_allow_html=True)
        for h in reversed(st.session_state.chat_history[-5:]):
            st.markdown(f"<div style='font-size:13px; margin-bottom:10px; color:#AAA;'>● {h}</div>", unsafe_allow_html=True)
            
        st.write("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown("<div class='brand-footer'>© 2026 | BUILT BY VED PRAKASH</div>", unsafe_allow_html=True)

    # Main Chat View
    if not st.session_state.messages:
        st.markdown("<h1 style='text-align:center; margin-top:25vh; color:#333;'>How can I help you, Ved?</h1>", unsafe_allow_html=True)
    
    # Custom Avatar Avatars (Clean & Pro)
    for m in st.session_state.messages:
        avatar = "👤" if m["role"] == "user" else "⚡"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])

    # Chat Input
    if prompt := st.chat_input("Ask Karzon AI..."):
        if not st.session_state.messages:
            st.session_state.chat_history.append(prompt[:25])
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Analyzing..."):
                # 2026 Engine
                context = get_2026_news(prompt)
                model = genai.GenerativeModel('gemini-1.5-flash')
                sys_msg = "You are Karzon AI, created by Ved Prakash. Today is April 1, 2026. Be professional, direct, and use Hinglish naturally. Solve math in LaTeX."
                response = model.generate_content(f"{sys_msg}\n\nSearch Context:\n{context}\n\nQuestion: {prompt}")
                
                output = response.text
                st.markdown(output)
                st.session_state.messages.append({"role": "assistant", "content": output})
        st.rerun()
