import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client
import os

# --- 1. SEO & GOOGLE VERIFICATION ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

# Google Tag aur Simple CSS
st.markdown("""
    <head>
        <meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" />
    </head>
    <style>
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        /* Simple ChatGPT Style Buttons */
        .stButton>button { 
            border: 1px solid #444; 
            background: #212121; 
            color: white; 
            border-radius: 8px; 
            width: 100%;
        }
        .stButton>button:hover { border-color: #10a37f; color: #10a37f; }
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
    except: st.error("Invalid email or password")

# --- 4. INTERFACE ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>Sign in to Ai Ved</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        t1, t2 = st.tabs(["Login", "Sign up"])
        with t1:
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.button("Continue"): login_user(e, p)
        with t2:
            ne = st.text_input("New Email")
            np = st.text_input("New Password", type="password")
            if st.button("Create Account"):
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("Account created! Now login.")
else:
    # --- MAIN APP (SIMPLE & CLEAN) ---
    st.sidebar.title("Ai Ved Pro")
    mode = st.sidebar.selectbox("Choose Engine:", 
        ["Simple Chat", "High Chat", "Deep Search", "Image Studio"])
    
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

    # Chat History
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            if mode == "Simple Chat":
                res = groq_client.chat.completions.create(model="llama3-8b-8192", messages=[{"role":"user","content":prompt}])
                response = res.choices[0].message.content

            elif mode == "High Chat":
                res = groq_client.chat.completions.create(model="llama3-70b-8192", messages=[{"role":"user","content":prompt}])
                response = res.choices[0].message.content

            elif mode == "Deep Search":
                with st.status("Searching the web...", expanded=False) as s:
                    data = tavily.search(query=prompt, search_depth="advanced")['results']
                    s.update(label="Search complete", state="complete")
                res = groq_client.chat.completions.create(model="llama3-70b-8192", messages=[{"role":"user","content":f"Context: {data}\nQuery: {prompt}"}])
                response = res.choices[0].message.content

            elif mode == "Image Studio":
                response = f"🎨 Generating image for: **{prompt}**"
                st.image(f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux")

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})