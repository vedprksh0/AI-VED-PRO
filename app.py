import streamlit as st
from groq import Groq
from supabase import create_client, Client
import google.generativeai as genai
import time
import requests

# --- CONFIG ---
st.set_page_config(page_title="Karzon AI", layout="wide")

# --- STYLE (Exactly your Original UI) ---
st.markdown("""
<style>
.stApp { background:#0E1117; color:#E6EDF3; }
.chat-container { width:70%; margin:auto; }

.chat-msg {
    padding:14px;
    border-radius:10px;
    margin-bottom:12px;
}
.user-msg { background:#21262D; text-align:right; }
.ai-msg { background:#161B22; }

.card {
    background:#161B22;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
    border:1px solid #30363D;
}

.header { text-align:center; font-size:26px; font-weight:700; }
.footer { text-align:center; font-size:11px; color:#8B949E; margin-top:20px; }
</style>
""", unsafe_allow_html=True)

# --- API INITIALIZATION ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    # Tavily optional setting to prevent crash
    TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", None)
except Exception as e:
    st.error("Secrets missing! Check GOOGLE_API_KEY, GROQ_API_KEY, etc.")

# --- TAVILY SEARCH (FAST & STABLE) ---
def real_search(query):
    if not TAVILY_API_KEY:
        return "Search disabled (No API Key)."
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": 3
        }
        response = requests.post(url, json=payload, timeout=5)
        results = response.json().get("results", [])
        return "\n".join([r.get("content", "") for r in results])
    except:
        return "Search skip ho gaya."

# --- IMAGE ---
def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

# --- AI ENGINE (THE REAL FIX) ---
def karzon_turbo(query):
    # Context fetch (Safe mode)
    context = real_search(query)

    prompt = f"""
    You are Karzon AI. 
    Rules: Reply in Hinglish. 
    Context: {context}
    User Question: {query}
    """

    # 1. Try Groq
    try:
        res = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            timeout=10.0
        )
        return res.choices[0].message.content
    except Exception as e1:
        # 2. Try Gemini as Fallback
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            # Show actual error if both fail (Debugging)
            return f"Technical Error! Groq: {str(e1)[:30]} | Gemini: {str(e2)[:30]}"

# --- SESSION ---
if "login" not in st.session_state: st.session_state.login = False
if "messages" not in st.session_state: st.session_state.messages = []
if "mode" not in st.session_state: st.session_state.mode = "chat"
if "history" not in st.session_state: st.session_state.history = []

# --- LOGIN ---
if not st.session_state.login:
    st.title("Karzon AI")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.login = True
            st.rerun()
        except: st.error("Login failed")

# --- MAIN INTERFACE ---
else:
    with st.sidebar:
        st.markdown("## Karzon AI")
        if st.button("💬 Chat"): st.session_state.mode = "chat"
        if st.button("📰 News"): st.session_state.mode = "news"
        if st.button("🎨 Image"): st.session_state.mode = "image"
        
        if st.button("➕ New Chat"):
            if st.session_state.messages:
                st.session_state.history.append(st.session_state.messages)
            st.session_state.messages = []
            st.rerun()

        st.markdown("### Your Chats")
        for i, chat in enumerate(reversed(st.session_state.history)):
            if st.button(f"Chat {len(st.session_state.history)-i}"):
                st.session_state.messages = chat
                st.session_state.mode = "chat"
                st.rerun()

        if st.button("Logout"):
            st.session_state.login = False
            st.rerun()

    st.markdown('<div class="header">Karzon AI</div>', unsafe_allow_html=True)

    # --- CHAT MODE ---
    if st.session_state.mode == "chat":
        # Container to show old messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            cls = "user-msg" if msg["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="chat-msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Input Area
        if prompt := st.chat_input("Ask anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Temporary UI update to show user message immediately
            st.markdown(f'<div class="chat-container"><div class="chat-msg user-msg">{prompt}</div></div>', unsafe_allow_html=True)
            
            # AI Response
            reply = karzon_turbo(prompt)
            
            # Typing Animation inside original style
            placeholder = st.empty()
            full = ""
            for word in reply.split():
                full += word + " "
                placeholder.markdown(f'<div class="chat-container"><div class="chat-msg ai-msg">{full}▌</div></div>', unsafe_allow_html=True)
                time.sleep(0.01)
            placeholder.markdown(f'<div class="chat-container"><div class="chat-msg ai-msg">{full}</div></div>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full})
            st.rerun()

    # --- NEWS MODE ---
    elif st.session_state.mode == "news":
        query = st.text_input("Search news")
        if query:
            with st.spinner("Fetching..."):
                result = karzon_turbo(f"Latest news about: {query}")
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)

    # --- IMAGE MODE ---
    elif st.session_state.mode == "image":
        p = st.text_input("Describe image")
        if st.button("Generate Image"):
            with st.spinner("Creating..."):
                st.image(generate_image(p), use_column_width=True)

    st.markdown('<div class="footer">© 2026 KARZON AI - VED PRAKASH</div>', unsafe_allow_html=True)
