import streamlit as st
import random
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. CONFIG & GOOGLE VERIFICATION ---
st.set_page_config(page_title="Karzon AI", page_icon="🌐", layout="wide")
st.markdown('<head><meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" /></head>', unsafe_allow_html=True)

# --- 2. THE "NO-CHAMAK" PREMIUM UI (DARK & CLEAN) ---
st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #E6EDF3; font-family: 'Inter', sans-serif; }
        [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363D; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Sidebar Elements */
        .side-item { font-size: 16px; font-weight: 600; padding: 12px 0; color: #C9D1D9; border-bottom: 1px solid #30363D; cursor: pointer; display: block; }
        .history-label { font-size: 11px; color: #8B949E; margin-top: 30px; font-weight: 700; text-transform: uppercase; }
        .history-item { font-size: 13px; color: #8B949E; padding: 8px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        /* Professional Header */
        .header-box { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; border-bottom: 1px solid #30363D; background: #0E1117; position: sticky; top: 0; z-index: 99; }
        .upgrade-btn { border: 2px solid #FAFAFA; border-radius: 20px; padding: 5px 18px; font-weight: 800; font-size: 13px; color: #FAFAFA; text-decoration: none; }

        /* Message Bubbles (Fixed Colors) */
        [data-testid="stChatMessage"] { border-radius: 15px; border: 1px solid #30363D !important; margin-bottom: 15px; background: #161B22 !important; color: #E6EDF3 !important; }
        
        /* Input Box (Rounded) */
        .stChatInputContainer { border: 2px solid #30363D !important; border-radius: 40px !important; width: 80% !important; margin: 0 auto !important; background: #161B22 !important; }

        .footer-ved { position: fixed; bottom: 15px; left: 15px; font-size: 10px; font-weight: 900; color: #484F58; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONNECTIONS ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Bhai, Secrets mein Keys check karo!")

# --- 4. KARZON TURBO SEARCH (IMPROVED) ---
def karzon_turbo_search(query):
    try:
        search_query = f"{query} latest news updates 2026"
        with DDGS() as ddgs:
            # We filter for top 3 clean results
            results = [r['body'] for r in ddgs.text(search_query, max_results=3)]
        return "\n".join(results)
    except:
        return "Search is currently silent. Relying on neural database."

# --- 5. SESSION & AUTH ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 6. AUTH SYSTEM (CLEAN) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Karzon AI</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        t1, t2 = st.tabs(["Sign In", "Create Account"])
        with t1:
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                try:
                    supabase.auth.sign_in_with_password({"email": e, "password": p})
                    st.session_state.logged_in = True
                    st.rerun()
                except: st.error("Email or Password galat hai.")
        with t2:
            ne = st.text_input("New Email")
            np = st.text_input("New Password", type="password")
            if st.button("Join Karzon AI", use_container_width=True):
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("Account Ready! Go to Sign In.")

# --- 7. MAIN INTERFACE ---
else:
    with st.sidebar:
        st.markdown('<div style="font-size:24px; font-weight:900;">Karzon AI</div>', unsafe_allow_html=True)
        st.write("---")
        if st.button("📝 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown('<div class="side-item">🔍 Search Chat</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-item">🎨 Image Creation</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="history-label">Your History</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.chat_history[-6:]):
            st.markdown(f'<div class="history-item">💬 {h}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('<div class="footer-ved">© 2026, BUILT BY<br>VED PRAKASH</div>', unsafe_allow_html=True)

    # Header
    st.markdown('<div class="header-box"><div>Karzon AI</div><div class="upgrade-btn">Upgrade</div></div>', unsafe_allow_html=True)

    # Main Area
    if not st.session_state.messages:
        st.markdown("<h2 style='text-align:center; margin-top:20vh; color:#C9D1D9;'>What can I do for you, Ved?</h2>", unsafe_allow_html=True)
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Chat Input
    if p := st.chat_input("Ask Karzon AI anything..."):
        if not st.session_state.messages:
            st.session_state.chat_history.append(p[:25])
        
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # Fetching data for 2026
                context = karzon_turbo_search(p)
                model = genai.GenerativeModel('gemini-1.5-flash')
                instr = f"Today is April 1, 2026. You are Karzon AI, built by Ved Prakash. Answer in natural Hinglish. Use search context for latest news. Math in LaTeX."
                response = model.generate_content(f"{instr}\n\nData: {context}\n\nQuestion: {p}")
                ans = response.text
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

st.markdown('<div style="text-align:center; font-size:11px; color:#8B949E; margin-top:30px; padding-bottom:20px;">Karzon AI can make mistakes. Check important info.</div>', unsafe_allow_html=True)
