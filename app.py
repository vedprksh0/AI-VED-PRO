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

# --- 2. PREMIUM CSS (GEMINI/FIESTA STYLE) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #000; }
        [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #EEE; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Header & Upgrade */
        .header-box { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; border-bottom: 1px solid #F0F0F0; background: white; position: sticky; top: 0; z-index: 99; }
        .upgrade-btn { border: 2px solid #000; border-radius: 20px; padding: 5px 15px; font-weight: 800; font-size: 13px; cursor: pointer; transition: 0.3s; }
        .upgrade-btn:hover { background: #000; color: #FFF; }

        /* Welcome Text */
        .welcome-area { text-align: center; margin-top: 10vh; margin-bottom: 30px; }
        .welcome-title { font-size: 36px; font-weight: 800; color: #222; }

        /* Round Input Box */
        .stChatInputContainer { border: 2.5px solid #000 !important; border-radius: 40px !important; width: 80% !important; margin: 0 auto !important; }
        
        /* Sidebar Elements */
        .side-item { font-size: 16px; font-weight: 600; padding: 10px 0; color: #333; border-bottom: 1px solid #F0F0F0; }
        .history-item { font-size: 13px; color: #666; padding: 5px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .footer-ved { position: fixed; bottom: 15px; left: 15px; font-size: 11px; font-weight: 900; color: #999; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONNECTIONS ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. ENGINE: KARZON TURBO (LIFETIME SEARCH) ---
def karzon_turbo_engine(query):
    try:
        with DDGS() as ddgs:
            search_data = [r['body'] for r in ddgs.text(query, max_results=3)]
        context = "\n".join(search_data)
        model = genai.GenerativeModel('gemini-1.5-flash')
        sys_prompt = "You are Karzon AI, a world-class assistant. Answer in Hinglish/English. Solve Math in LaTeX."
        response = model.generate_content(f"{sys_prompt}\n\nWeb Data: {context}\n\nUser: {query}")
        return response.text
    except Exception as e:
        return "Bhai, Krazon Turbo abhi thoda busy hai, par main bina search kiye jawab de raha hoon: \n" + groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":query}]).choices[0].message.content

# --- 5. SESSION STATES ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "welcome_msg" not in st.session_state:
    st.session_state.welcome_msg = random.choice(["What are you working on?", "How can I help you today, Ved?", "Ready for the mission?"])

# --- 6. AUTH SYSTEM (SIGN IN & SIGN UP) ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Karzon AI</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])
        
        with auth_tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.logged_in = True
                    st.rerun()
                except: st.error("Account not found. Please Create Account first.")
        
        with auth_tab2:
            new_email = st.text_input("New Email", key="reg_email")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Join Karzon AI", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    st.success("Account created successfully! Now go to 'Sign In' tab.")
                except: st.error("Registration failed. Check your details.")

# --- 7. MAIN DASHBOARD ---
else:
    # Sidebar (Drawing Layout)
    with st.sidebar:
        st.markdown('<div style="font-size:22px; font-weight:900;">Karzon AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-item">🔍 Search chat</div>', unsafe_allow_html=True)
        if st.button("📝 New chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown('<div class="side-item">🎨 Image creation</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown("**Your chats**")
        for h in reversed(st.session_state.chat_history[-5:]):
            st.markdown(f'<div class="history-item">💬 {h}</div>', unsafe_allow_html=True)
        
        if st.button("Sign Out"):
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
        if p[:30] not in st.session_state.chat_history:
            st.session_state.chat_history.append(p[:30])
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            with st.spinner("Karzon Turbo is analyzing..."):
                ans = karzon_turbo_engine(p)
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
