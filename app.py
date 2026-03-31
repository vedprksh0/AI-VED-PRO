import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client
import os

# --- 1. NEXT-GEN UI & SEO ---
st.set_page_config(page_title="Ai Ved Pro | Multi-Engine AI", page_icon="⚡", layout="wide")

st.markdown("""
    <head>
        <meta name="description" content="Ai Ved Pro - Integrated AI Architecture.">
        <meta name="google-site-verification" content="<meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" />
    </head>
    <style>
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        .stButton>button { border: 2px solid #00F2FF; background: transparent; color: #00F2FF; border-radius: 15px; }
        .stButton>button:hover { background: #00F2FF !important; color: #000 !important; box-shadow: 0 0 20px #00F2FF; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNECTIONS ---
url, key = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SESSION & AUTH ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

def login_user(e, p):
    try:
        supabase.auth.sign_in_with_password({"email": e, "password": p})
        st.session_state.logged_in = True
        st.rerun()
    except: st.error("Access Denied: Invalid Credentials")

# --- 4. INTERFACE ---
if not st.session_state.logged_in:
    st.title("🛡️ Ai Ved Pro - Security Portal")
    t1, t2 = st.tabs(["Authorize", "Register"])
    with t1:
        e, p = st.text_input("Email"), st.text_input("Password", type="password")
        if st.button("Unlock System"): login_user(e, p)
    with t2:
        ne, np = st.text_input("New Email"), st.text_input("New Password", type="password")
        if st.button("Create Digital Identity"):
            supabase.auth.sign_up({"email": ne, "password": np})
            st.success("Identity Created. Log in now.")

else:
    # --- PRO SIDEBAR (MODES SELECTION) ---
    st.sidebar.title("🎮 Engine Control")
    mode = st.sidebar.radio("Select Mode:", 
        ["Simple Chat (Fast)", "High Chat (Smart)", "Deep Web Search", "Image Studio (Neon)"])
    
    if st.sidebar.button("Terminate Session"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"⚡ {mode}")
    
    # Message Display
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Input command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # --- FEATURE 1: SIMPLE CHAT (Fast & Direct) ---
            if mode == "Simple Chat (Fast)":
                res = groq_client.chat.completions.create(model="llama3-8b-8192", messages=[{"role":"user","content":prompt}])
                response = res.choices[0].message.content

            # --- FEATURE 2: HIGH CHAT (Deep Reasoning) ---
            elif mode == "High Chat (Smart)":
                res = groq_client.chat.completions.create(model="llama3-70b-8192", messages=[{"role":"user","content":prompt}])
                response = res.choices[0].message.content

            # --- FEATURE 3: DEEP WEB SEARCH (Tavily + Groq) ---
            elif mode == "Deep Web Search":
                with st.status("Scanning global data nodes...", expanded=False) as s:
                    data = tavily.search(query=prompt, search_depth="advanced")['results']
                    s.update(label="Intelligence Synthesized", state="complete")
                res = groq_client.chat.completions.create(model="llama3-70b-8192", messages=[{"role":"user","content":f"Context: {data}\nQuery: {prompt}"}])
                response = res.choices[0].message.content

            # --- FEATURE 4: IMAGE STUDIO (Using Placeholder/API) ---
            elif mode == "Image Studio (Neon)":
                response = f"🎨 Generating neon visual for: **{prompt}**\n\n*(Note: Bhai, image API yahan connect kar sakte ho, abhi main placeholder generate kar raha hoon)*"
                st.image(f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux")

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})