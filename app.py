import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client

# --- 1. SEO & GOOGLE VERIFICATION (TERA CODE) ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

st.markdown(f"""
    <head>
        <meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" />
    </head>
    <style>
        .stApp {{ background-color: #0E1117; color: white; }}
        [data-testid="stSidebarNav"] {{ display: none; }}
        .sidebar-title {{ font-size: 26px; font-weight: bold; padding: 20px 0px; color: #10a37f; }}
        .stButton>button {{ width: 100%; border-radius: 8px; border: 1px solid #333; background: #1A1A1A; color: white; text-align: left; }}
        .stButton>button:hover {{ border-color: #10a37f; background: #2D2D2D !important; }}
        .fixed-disclaimer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0E1117; color: #777; text-align: center; font-size: 11px; padding: 10px 0; z-index: 999; border-top: 1px solid #222; }}
        .footer-text {{ position: fixed; bottom: 60px; left: 20px; font-size: 12px; color: #555; }}
        .history-item {{ font-size: 13px; color: #aaa; padding: 5px 0; border-bottom: 1px solid #222; }}
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNECTIONS ---
url, key = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SESSION STATE (MEMORY & HISTORY) ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "Chat"
if "messages" not in st.session_state: st.session_state.messages = [] 
if "search_history" not in st.session_state: st.session_state.search_history = [] # Search history store

# --- 4. LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Sign in to Ai Ved</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        email = st.text_input("Email", placeholder="user@example.com")
        password = st.text_input("Password", type="password")
        if st.button("Continue"):
            try:
                supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.logged_in = True
                st.rerun()
            except: st.error("Login Failed.")

# --- 5. MAIN APP ---
else:
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Ai Ved</div>', unsafe_allow_html=True)
        if st.button("💬 Ask Ai Ved"): st.session_state.page = "Chat"; st.rerun()
        if st.button("🔍 Real-Time Search"): st.session_state.page = "Search"; st.rerun()
        if st.button("🎨 Image Studio"): st.session_state.page = "Image"; st.rerun()
        
        st.write("---")
        st.subheader("Recent Searches")
        # Display Search History in Sidebar
        for item in reversed(st.session_state.search_history[-5:]): # Last 5 searches
            st.markdown(f'<div class="history-item">🔍 {item}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.button("+ New Chat"):
            st.session_state.messages = []
            st.rerun()
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown(f"""<div class="footer-text">Since 2026<br><b>Built by Ved Prakash</b></div>""", unsafe_allow_html=True)

    # --- CHAT ENGINE ---
    if st.session_state.page == "Chat":
        st.title("Ask Ai Ved")
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]): st.markdown(message["content"])

        if prompt := st.chat_input("How can I help you today?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.search_history.append(prompt) # Saving to history
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                response = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=history)
                full_res = response.choices[0].message.content
                st.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            st.rerun()

    # --- REAL-TIME SEARCH ---
    elif st.session_state.page == "Search":
        st.title("Real-Time Web Search")
        search_query = st.chat_input("Search live news...")
        if search_query:
            st.session_state.search_history.append(search_query) # Saving search query
            with st.spinner("Accessing global web data..."):
                results = tavily.search(query=search_query, search_depth="advanced", max_results=5)
                context = "\n".join([f"Source {i+1}: {r['content']}" for i, r in enumerate(results['results'])])
            
            with st.chat_message("assistant"):
                res = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": "Use provided context to answer."},
                              {"role": "user", "content": f"Context: {context}\n\nQuestion: {search_query}"}]
                )
                st.markdown(res.choices[0].message.content)

    # --- IMAGE STUDIO ---
    elif st.session_state.page == "Image":
        st.title("Image Studio")
        img_desc = st.text_input("Describe your art...")
        if st.button("Generate Art"):
            st.session_state.search_history.append(img_desc) # Saving prompt
            with st.spinner("Painting..."):
                url = f"https://pollinations.ai/p/{img_desc.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux"
                st.image(url, caption=f"Result: {img_desc}")

    st.markdown('<div class="fixed-disclaimer">Ai Ved can make mistakes. Check important info.</div>', unsafe_allow_html=True)