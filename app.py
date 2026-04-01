import streamlit as st
from groq import Groq
from supabase import create_client, Client
import google.generativeai as genai
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time

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
</style>
""", unsafe_allow_html=True)

# --- API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- CACHE SEARCH ---
@st.cache_data(ttl=600)
def ddg_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        return [r.get("body", "") for r in results]
    except:
        return []

# --- SCRAPING SEARCH ---
@st.cache_data(ttl=600)
def scrape_google(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.google.com/search?q={query}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        texts = []
        for g in soup.find_all("div"):
            t = g.get_text()
            if len(t) > 80:
                texts.append(t)

        return texts[:5]
    except:
        return []

# --- KARZON TURBO SEARCH ---
def karzon_search(query):
    q = query.lower()

    if "nrews" in q:
        q = q.replace("nrews", "news")

    if "news" in q:
        q += " latest breaking news 2026"

    data = []

    # 1. scrape
    data += scrape_google(q)

    # 2. ddg backup
    data += ddg_search(q)

    if not data:
        return "No data"

    return "\n".join(data[:8])

# --- AI ENGINE ---
def karzon_turbo(query):
    context = karzon_search(query)

    prompt = f"""
    You are Karzon AI.

    - Always answer
    - Clean useful info
    - Ignore garbage text
    - Reply in same language (Hinglish/English/Hindi)

    Data:
    {context}

    Question:
    {query}
    """

    # GROQ
    try:
        res = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
        )
        if res.choices[0].message.content:
            return res.choices[0].message.content
    except:
        pass

    # GEMINI
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except:
        pass

    # FINAL FALLBACK
    return "Main available hoon 🙂 bolo kya help chahiye?"

# --- SESSION ---
if "login" not in st.session_state:
    st.session_state.login = False
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        except:
            st.error("Login failed")

# --- MAIN ---
else:
    st.markdown('<div class="header">Karzon AI</div>', unsafe_allow_html=True)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        cls = "user-msg" if msg["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="chat-msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        reply = karzon_turbo(prompt)

        placeholder = st.empty()
        full = ""

        for word in reply.split():
            full += word + " "
            placeholder.markdown(full)
            time.sleep(0.02)

        st.session_state.messages.append({"role": "assistant", "content": full})
        st.rerun()
