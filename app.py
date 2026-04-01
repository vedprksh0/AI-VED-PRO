import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import google.generativeai as genai
import time

# --- CONFIG ---
st.set_page_config(page_title="Karzon AI", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background:#0E1117; color:#E6EDF3; }
.chat-container { width:70%; margin:auto; }
.chat-msg { padding:14px; border-radius:12px; margin-bottom:12px; }
.user-msg { background:#238636; text-align:right; }
.ai-msg { background:#161B22; }
.header { text-align:center; font-size:26px; font-weight:700; }
.footer { text-align:center; font-size:11px; color:#8B949E; margin-top:20px; }
</style>
""", unsafe_allow_html=True)

# --- API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- SEARCH ---
def real_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
        return "\n".join([r["body"] for r in results])
    except:
        return ""

# --- IMAGE (REAL USING POLLINATIONS API - FREE) ---
def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
    return url

# --- TURBO ---
def karzon_turbo(query):
    context = real_search(query)

    prompt = f"""
    Answer in Hinglish smartly.

    Data:
    {context}

    Question:
    {query}
    """

    try:
        res = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content
    except:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model.generate_content(prompt).text
        except:
            return context

# --- SESSION ---
if "login" not in st.session_state:
    st.session_state.login = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "history" not in st.session_state:
    st.session_state.history = []

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
    with st.sidebar:
        st.markdown("## Karzon AI")

        if st.button("💬 Chat"):
            st.session_state.mode = "chat"

        if st.button("🔍 Search"):
            st.session_state.mode = "search"

        if st.button("🎨 Image"):
            st.session_state.mode = "image"

        if st.button("➕ New Chat"):
            if st.session_state.messages:
                st.session_state.history.append(st.session_state.messages)
            st.session_state.messages = []

        st.markdown("### Your Chats")
        for i, chat in enumerate(reversed(st.session_state.history)):
            if st.button(f"Chat {i+1}"):
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

            reply = karzon_turbo(prompt)

            placeholder = st.empty()
            full = ""

            for word in reply.split():
                full += word + " "
                placeholder.markdown(full)
                time.sleep(0.02)

            st.session_state.messages.append({"role": "assistant", "content": full})
            st.rerun()

    # --- SEARCH MODE ---
    elif st.session_state.mode == "search":
        q = st.text_input("Search anything")
        if q:
            st.write(real_search(q))

    # --- IMAGE MODE ---
    elif st.session_state.mode == "image":
        p = st.text_input("Describe image")
        if st.button("Generate Image"):
            img_url = generate_image(p)
            st.image(img_url, use_column_width=True)

    st.markdown('<div class="footer">© 2026 KARZON AI - VED PRAKASH</div>', unsafe_allow_html=True)
