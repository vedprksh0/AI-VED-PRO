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
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
except Exception as e:
    st.error("Secrets missing! Please add GOOGLE_API_KEY, GROQ_API_KEY, TAVILY_API_KEY, etc.")

# --- TAVILY SEARCH (REPLACED DDGS FOR STABILITY) ---
def real_search(query):
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
        if not results:
            return "No internet data."
        return "\n".join([r.get("content", "") for r in results])
    except:
        return "Search skip ho gaya."

# --- IMAGE ---
def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

# --- AI ENGINE (FIXED FALLBACK) ---
def karzon_turbo(query):
    context = real_search(query)

    prompt = f"""
    You are Karzon AI.
    RULES:
    - Always reply in Hinglish + English.
    - Use this Context if helpful: {context}
    Question: {query}
    """

    # 1. First Attempt: Groq
    try:
        res = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            timeout=10.0
        )
        return res.choices[0].message.content
    except:
        # 2. Second Attempt: Gemini (Fallback)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except:
            return "Dono servers busy hain. Please check API Limits!"

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

# --- MAIN ---
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
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            cls = "user-msg" if msg["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="chat-msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if prompt := st.chat_input("Ask anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Streaming UI inside Original Style
            reply = karzon_turbo(prompt)
            placeholder = st.empty()
            full = ""
            for word in reply.split():
                full += word + " "
                # Keeping the style exactly as requested
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
                result = karzon_turbo(f"Latest news summary about: {query}")
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)

    # --- IMAGE MODE ---
    elif st.session_state.mode == "image":
        p = st.text_input("Describe image")
        if st.button("Generate Image"):
            st.image(generate_image(p), use_column_width=True)

    st.markdown('<div class="footer">© 2026 KARZON AI - VED PRAKASH</div>', unsafe_allow_html=True)
