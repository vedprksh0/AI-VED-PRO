import streamlit as st
import random
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. CONFIG & GOOGLE VERIFICATION ---
st.set_page_config(page_title="Karzon AI", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")

# Google Search Console Verification Tag
st.markdown('<head><meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" /></head>', unsafe_allow_html=True)

# --- 2. PREMIUM STABLE DARK CSS (Fixes Chamak) ---
# Yahan maine text color safe white (#FAFAFA) rakha hai taaki sab saaf dikhe.
st.markdown("""
    <style>
        /* Base Styling */
        .stApp { background-color: #0E1117; color: #FAFAFA; font-family: 'Inter', sans-serif; }
        
        /* Sidebar Styling (Clean and Dark) */
        [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363D; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Header & Upgrade Button */
        .header-box { display: flex; justify-content: space-between; align-items: center; padding: 10px 5%; border-bottom: 1px solid #30363D; background: #0E1117; position: sticky; top: 0; z-index: 99; }
        .upgrade-btn { border: 2px solid #FAFAFA; border-radius: 20px; padding: 5px 15px; font-weight: 800; font-size: 13px; color: #FAFAFA; cursor: pointer; transition: 0.3s; }
        .upgrade-btn:hover { background: #FAFAFA; color: #000; }

        /* Welcome Text Center */
        .welcome-area { text-align: center; margin-top: 10vh; margin-bottom: 30px; }
        .welcome-title { font-size: 38px; font-weight: 800; color: #FAFAFA; letter-spacing: -1.5px; }

        /* Round Input Box (Gemini Style) */
        .stChatInputContainer { border: 2.5px solid #FAFAFA !important; border-radius: 40px !important; width: 80% !important; margin: 0 auto !important; }
        .stChatInput { color: #FAFAFA !important; }
        
        /* Message Styling */
        [data-testid="stChatMessage"] { background-color: #161B22; border-radius: 12px; border: 1px solid #30363D; color: #FAFAFA !important; margin-bottom: 15px; }
        [data-testid="stChatMessage"] p { color: #FAFAFA !important; }

        /* Sidebar Elements */
        .side-item { font-size: 16px; font-weight: 600; padding: 10px 0; color: #C9D1D9; border-bottom: 1px solid #30363D; cursor: pointer; }
        .history-item { font-size: 13px; color: #8B949E; padding: 5px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }
        .footer-ved { position: fixed; bottom: 15px; left: 15px; font-size: 11px; font-weight: 900; color: #8B949E; }
        
        /* Auth Fix for Tabs */
        div[data-testid="stTabs"] button { color: #C9D1D9 !important; border-bottom: 2px solid transparent !important; }
        div[data-testid="stTabs"] button[aria-selected="true"] { color: #FAFAFA !important; border-bottom: 2px solid #FAFAFA !important; font-weight: bold; }
        
        /* Text inputs in Dark Mode */
        div[data-baseweb="input"] input { color: #FAFAFA !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONNECTIONS & ENGINES ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Bhai, Secrets check karo, koi key miss ho rahi hai local laptop par error aa jayega!")

# --- 4. ENGINE LOGIC (KARZON TURBO FREEDOM) ---
def karzon_turbo_search(query):
    try:
        # Infinity Free Search: Internet Scan
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
        return "\n".join(results)
    except:
        return "Using internal knowledge as web connection is unstable."

# --- 5. SESSION STATES ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "welcome_text" not in st.session_state:
    st.session_state.welcome_text = random.choice([
        "What are you working on?", "How can I help you today, Ved?", 
        "Karzon AI is ready. Mission?", "Let's build something big."
    ])

# --- 6. AUTH SYSTEM (SIGN IN & SIGN UP) - FIXED VISIBILITY ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Karzon AI</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])
        
        with auth_tab1:
            st.markdown("<h4 style='color:#C9D1D9;'>Welcome back, Ved!</h4>", unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.logged_in = True
                    st.rerun()
                except: st.error("Account not found. Please Create Account first.")
        
        with auth_tab2:
            st.markdown("<h4 style='color:#C9D1D9;'>Join Karzon AI</h4>", unsafe_allow_html=True)
            new_email = st.text_input("New Email", key="reg_email")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Join Karzon AI", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    st.success("Account created successfully! Now go to 'Sign In' tab.")
                except: st.error("Registration failed. Check details or email may exist.")

# --- 7. MAIN DASHBOARD ---
else:
    # Sidebar (drawing layout with history)
    with st.sidebar:
        st.markdown('<div style="font-size:24px; font-weight:800; margin-bottom:20px; color:#FAFAFA;">Karzon AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-item">🔍 Search chat</div>', unsafe_allow_html=True)
        if st.button("📝 New chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.welcome_text = random.choice(["Next task, Ved?", "What's up?"])
            st.rerun()
        st.markdown('<div class="side-item">🎨 Image creation</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top:20px; font-size:12px; text-transform:uppercase; color:#8B949E; font-weight:700;">Your chats</div>', unsafe_allow_html=True)
        # Displaying last 5 chats from history
        for h in reversed(st.session_state.chat_history[-5:]):
            st.markdown(f'<div class="history-item">💬 {h}</div>', unsafe_allow_html=True)
        
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('<div class="footer-ved">© 2026, BUILT BY<br>VED PRAKASH</div>', unsafe_allow_html=True)

    # Header
    st.markdown('<div class="header-box"><div>Karzon AI</div><div class="upgrade-btn">Upgrade</div></div>', unsafe_allow_html=True)

    # Main Welcome Screen
    if not st.session_state.messages:
        st.markdown(f'<div class="welcome-area"><div class="welcome-title">{st.session_state.welcome_text}</div></div>', unsafe_allow_html=True)
    else:
        for m in st.session_state.messages:
            # We enforce safe text coloring for all messages
            with st.chat_message(m["role"]): st.markdown(f'<div style="color:#FAFAFA !important;">{m["content"]}</div>', unsafe_allow_html=True)

    # Bottom Input & Router Logic
    if p := st.chat_input("Ask Karzon AI anything..."):
        # Save to sidebar history
        if p[:30] not in st.session_state.chat_history:
            st.session_state.chat_history.append(p[:30])
        
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(f'<div style="color:#FAFAFA !important;">{p}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Karzon Turbo is analyzing..."):
                try:
                    # 1. Fetch Context (Free Lifetime Search)
                    context = karzon_turbo_search(p)
                    
                    # 2. Process with Gemini (High Intelligence)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    # System Instruction for world-class assistant
                    sys_instr = "You are Karzon AI, a world-class assistant created by Ved Prakash. Solve math with step-by-step LaTeX. Use Hinglish/English naturally."
                    response = model.generate_content(f"{sys_instr}\n\nWeb Data Context: {context}\n\nUser: {p}")
                    full_res = response.text
                except:
                    # Priority Backup: Use internal knowledge from Groq
                    full_res = "Bhai, Krazon Turbo abhi thoda connection struggle kar raha hai, par main main theek hun. Aapko kuch help chahiye integrated knowledge se?\n\n" + groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":p}]).choices[0].message.content

                st.markdown(f'<div style="color:#FAFAFA !important;">{full_res}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
        st.rerun()

# --- 8. FOOTER WITH VISIBILITY FIX ---
st.markdown('<div style="text-align:center; font-size:11px; color:#8B949E; margin-top:20px; padding-bottom: 20px;">Karzon AI can make mistakes. Check important info.</div>', unsafe_allow_html=True)
