import streamlit as st
import random
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. CONFIG & GOOGLE VERIFICATION ---
st.set_page_config(page_title="Karzon AI", page_icon="🌐", layout="wide")

# Google Search Console Verification Tag
st.markdown('<head><meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" /></head>', unsafe_allow_html=True)

# --- 2. PROFESSIONAL DARK UI (STABLE & CLEAN) ---
st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363D; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Header Box */
        .header-box { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; border-bottom: 1px solid #30363D; background: #0E1117; position: sticky; top: 0; z-index: 99; }
        .upgrade-btn { border: 2px solid #FAFAFA; border-radius: 20px; padding: 5px 15px; font-weight: 800; font-size: 13px; color: #FAFAFA; cursor: pointer; text-decoration: none; }

        /* Welcome Text */
        .welcome-area { text-align: center; margin-top: 10vh; margin-bottom: 30px; }
        .welcome-title { font-size: 36px; font-weight: 800; color: #FAFAFA; }

        /* Round Input Box */
        .stChatInputContainer { border: 2px solid #30363D !important; border-radius: 40px !important; width: 80% !important; margin: 0 auto !important; background: #161B22 !important; }
        
        /* Sidebar Elements */
        .side-item { font-size: 16px; font-weight: 600; padding: 12px 0; color: #C9D1D9; border-bottom: 1px solid #30363D; cursor: pointer; }
        .history-label { font-size: 12px; color: #8B949E; margin-top: 30px; font-weight: 700; text-transform: uppercase; }
        .history-item { font-size: 13px; color: #8B949E; padding: 8px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .footer-ved { position: fixed; bottom: 20px; left: 15px; font-size: 11px; font-weight: 900; color: #8B949E; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONNECTIONS ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Bhai, Secrets check karo! API key ya Supabase details missing hain.")

# --- 4. ENGINE: KARZON TURBO (LIFETIME SEARCH) ---
def karzon_turbo_engine(query):
    try:
        # Search for 2026 data
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(f"{query} latest news April 2026", max_results=3)]
        context = "\n".join(results)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        sys_instr = "You are Karzon AI, created by Ved Prakash. Today is April 1, 2026. Answer in Hinglish/English naturally. Use LaTeX for math."
        response = model.generate_content(f"{sys_instr}\n\nWeb Data: {context}\n\nUser: {query}")
        return response.text
    except Exception as e:
        # Fallback to internal knowledge if search fails
        res = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":query}])
        return "Bhai, web connection thoda slow hai par main jawab de raha hoon:\n\n" + res.choices[0].message.content

# --- 5. SESSION STATES ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "welcome_msg" not in st.session_state:
    st.session_state.welcome_msg = random.choice(["What's the mission today, Ved?", "How can I help you?", "Karzon AI is ready."])

# --- 6. AUTH SYSTEM (SIGN IN & SIGN UP) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Karzon AI</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                try:
                    supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.logged_in = True
                    st.rerun()
                except: st.error("Email or Password galat hai!")
        with tab2:
            n_email = st.text_input("New Email")
            n_pass = st.text_input("New Password", type="password")
            if st.button("Join Karzon AI", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": n_email, "password": n_pass})
                    st.success("Account ban gaya! Sign In tab par jao.")
                except: st.error("Registration failed.")

# --- 7. MAIN DASHBOARD ---
else:
    with st.sidebar:
        st.markdown('<div style="font-size:24px; font-weight:900; color:white;">Karzon AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-item">🔍 Search chat</div>', unsafe_allow_html=True)
        if st.button("📝 New chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown('<div class="side-item">🎨 Image creation</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="history-label">Your chats</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.chat_history[-6:]):
            st.markdown(f'<div class="history-item">💬 {h}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('<div class="footer-ved">© 2026, BUILT BY<br>VED PRAKASH</div>', unsafe_allow_html=True)

    # Header
    st.markdown('<div class="header-box"><div>Karzon AI</div><div class="upgrade-btn">Upgrade</div></div>', unsafe_allow_html=True)

    # Welcome Area
    if not st.session_state.messages:
        st.markdown(f'<div class="welcome-area"><div class="welcome-title">{st.session_state.welcome_msg}</div></div>', unsafe_allow_html=True)
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

    # Bottom Input
    if p := st.chat_input("Ask Karzon AI anything..."):
        # Save only the first message of a session to history
        if not st.session_state.messages:
            st.session_state.chat_history.append(p[:30])
        
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            with st.spinner("Karzon Turbo is thinking..."):
                ans = karzon_turbo_engine(p)
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

st.markdown('<div style="text-align:center; font-size:11px; color:#8B949E; margin-top:20px; padding-bottom:20px;">Karzon AI can make mistakes. Check important info.</div>', unsafe_allow_html=True)
