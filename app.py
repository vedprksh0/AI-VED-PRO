import streamlit as st
from groq import Groq
from supabase import create_client, Client
import google.generativeai as genai
import time
import requests

# --- CONFIG ---
st.set_page_config(page_title="Karzon AI", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background:#0E1117; color:#E6EDF3; }
.chat-container { width:70%; margin:auto; }
.chat-msg { padding:14px; border-radius:10px; margin-bottom:12px; }
.user-msg { background:#21262D; text-align:right; }
.ai-msg { background:#161B22; }
.header { text-align:center; font-size:26px; font-weight:700; }
.footer { text-align:center; font-size:11px; color:#8B949E; margin-top:20px; }
</style>
""", unsafe_allow_html=True)

# --- API ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", None)
except Exception as e:
    st.error("Secrets missing!")

# --- SEARCH ---
def real_search(query):
    if not TAVILY_API_KEY: return "No Search Key."
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}
        response = requests.post(url, json=payload, timeout=5)
        return "\n".join([r.get("content", "") for r in response.json().get("results", [])])
    except: return "Search failed."

# --- AI ENGINE ---
def karzon_turbo(query):
    context = real_search(query)
    prompt = f"User: {query}\nContext: {context}\nInstructions: You are Karzon AI. Answer in Hinglish."
    try:
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            timeout=10.0
        )
        return res.choices[0].message.content
    except:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            return model.generate_content(prompt).text
        except: return "Server busy. Try again."

# --- SESSION ---
if "login" not in st.session_state: st.session_state.login = False
if "messages" not in st.session_state: st.session_state.messages = []
if "mode" not in st.session_state: st.session_state.mode = "chat"
if "history" not in st.session_state: st.session_state.history = []

# --- APP LOGIC ---
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
else:
    with st.sidebar:
        st.header("Karzon AI")
        if st.button("💬 Chat"): st.session_state.mode = "chat"
        if st.button("📰 News"): st.session_state.mode = "news"
        if st.button("🎨 Image"): st.session_state.mode = "image"
        if st.button("➕ New"):
            st.session_state.messages = []
            st.rerun()

    st.markdown('<div class="header">Karzon AI</div>', unsafe_allow_html=True)

    # --- YE HAI LINE 141 KA FIX ---
    if st.session_state.mode == "chat":
        for msg in st.session_state.messages:
            cls = "user-msg" if msg["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="chat-msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)

        if prompt := st.chat_input("Ask..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            reply = karzon_turbo(prompt)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

    elif st.session_state.mode == "news":
        q = st.text_input("News topic")
        if q: st.write(karzon_turbo(f"News about {q}"))

    elif st.session_state.mode == "image":
        p = st.text_input("Image prompt")
        if st.button("Generate"):
            st.image(f"https://image.pollinations.ai/prompt/{p.replace(' ', '%20')}")

    st.markdown('<div class="footer">© 2026 KARZON AI</div>', unsafe_allow_html=True)
