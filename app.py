import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client

# --- 1. SEO & GOOGLE VERIFICATION ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

st.markdown(f"""
    <head>
        <meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" />
    </head>
    <style>
        .stApp {{ background-color: #0E1117; color: white; }}
        /* Sidebar Logo/Name Style */
        [data-testid="stSidebarNav"] {{ display: none; }}
        .sidebar-title {{
            font-size: 24px;
            font-weight: bold;
            padding: 20px 0px;
            color: #FFFFFF;
        }}
        /* ChatGPT Style Buttons */
        .stButton>button {{
            width: 100%;
            border-radius: 8px;
            border: 1px solid #444;
            background: #212121;
            color: white;
            text-align: left;
            padding: 10px 15px;
        }}
        .stButton>button:hover {{
            background: #2D2D2D !important;
            border-color: #10a37f;
        }}
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNECTIONS ---
url, key = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_page" not in st.session_state: st.session_state.current_page = "Home"

# --- 3. LOGIN INTERFACE ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>Sign in to Ai Ved</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.button("Continue"):
            try:
                supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.logged_in = True
                st.rerun()
            except: st.error("Invalid Credentials")

# --- 4. MAIN INTERFACE (SIDEBAR NAME LEFT SIDE) ---
else:
    # LEFT SIDEBAR NAME & NAVIGATION
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Ai Ved</div>', unsafe_allow_html=True)
        
        if st.button("+ New Chat / Home"):
            st.session_state.current_page = "Home"
            st.rerun()
            
        st.write("---") # Divider
        
        if st.button("💬 Simple Chat"): st.session_state.current_page = "Simple"; st.rerun()
        if st.button("🚀 High Chat"): st.session_state.current_page = "High"; st.rerun()
        if st.button("🔍 Deep Search"): st.session_state.current_page = "Search"; st.rerun()
        if st.button("🎨 Image Studio"): st.session_state.current_page = "Image"; st.rerun()
        
        st.write("---")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- CENTER CONTENT ---
    if st.session_state.current_page == "Home":
        st.title("Ai Ved Pro")
        st.subheader("How can I help you today?")
        st.info("Select an engine from the left sidebar to start a new session.")

    else:
        # --- MODE 1: SIMPLE CHAT ---
        if st.session_state.current_page == "Simple":
            st.title("Simple Chat")
            prompt = st.chat_input("Ask anything...")
            if prompt:
                res = groq_client.chat.completions.create(model="llama3-8b-8192", messages=[{"role":"user","content":prompt}])
                st.chat_message("assistant").write(res.choices[0].message.content)

        # --- MODE 2: HIGH CHAT ---
        elif st.session_state.current_page == "High":
            st.title("High Chat (Powered by Llama 70B)")
            prompt = st.chat_input("Ask a complex question...")
            if prompt:
                res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}])
                st.chat_message("assistant").write(res.choices[0].message.content)

        # --- MODE 3: DEEP SEARCH ---
        elif st.session_state.current_page == "Search":
            st.title("Deep Web Search")
            prompt = st.chat_input("Search the real-time web...")
            if prompt:
                with st.status("Searching live web..."):
                    data = tavily.search(query=prompt, search_depth="advanced")['results']
                res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Context: {data}\nQuery: {prompt}"}])
                st.chat_message("assistant").write(res.choices[0].message.content)

        # --- MODE 4: IMAGE STUDIO ---
        elif st.session_state.current_page == "Image":
            st.title("Image Studio")
            prompt = st.text_input("Describe your imagination...")
            if st.button("Generate"):
                st.image(f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux")