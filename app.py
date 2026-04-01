import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import google.generativeai as genai
import speech_recognition as sr

# --- CONFIG ---
st.set_page_config(page_title="Karzon AI", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background:#0E1117; color:white; }

.chat-msg {
    padding:12px 16px;
    border-radius:12px;
    margin-bottom:10px;
    max-width:80%;
}
.user-msg { background:#1f6feb; margin-left:auto; }
.ai-msg { background:#161b22; }

.header { font-size:20px; font-weight:700; padding:10px; }
.footer { position:fixed; bottom:10px; left:10px; font-size:11px; color:#666; }
</style>
""", unsafe_allow_html=True)

# --- API KEYS ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- REAL SEARCH ---
def real_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

        clean = []
        for r in results:
            clean.append(f"{r['title']}: {r['body']}")

        return "\n\n".join(clean)
    except:
        return ""

# --- IMAGE GENERATOR ---
def generate_image(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Create a detailed AI image prompt: {prompt}")
        return response.text
    except:
        return "Image generation failed."

# --- VOICE ---
def voice_to_text():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=5)
            return r.recognize_google(audio)
    except:
        return ""

# --- TURBO ENGINE ---
def karzon_turbo(query):
    context = real_search(query)

    prompt = f"""
    Latest data:
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
        pass

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(prompt)
        return res.text
    except:
        return context

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
            supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            st.session_state.login = True
            st.rerun()
        except:
            st.error("Login failed")

# --- MAIN ---
else:
    with st.sidebar:
        st.markdown("## Karzon AI")

        if st.button("➕ New Chat"):
            st.session_state.messages = []

        st.markdown("### Search")
        search_q = st.text_input("Search anything")
        if search_q:
            st.write(real_search(search_q))

        st.markdown("### Image Creation")
        img_prompt = st.text_input("Describe image")
        if st.button("Generate Image"):
            st.write(generate_image(img_prompt))

        st.markdown("### Voice")
        if st.button("Start Voice Input"):
            text = voice_to_text()
            if text:
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()

        st.markdown("### Your Chats")
        for m in st.session_state.messages[-5:]:
            if m["role"] == "user":
                st.write("💬 " + m["content"][:20])

        if st.button("Logout"):
            st.session_state.login = False
            st.rerun()

    st.markdown('<div class="header">Karzon AI</div>', unsafe_allow_html=True)

    # chat
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-msg user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-msg ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    # input
    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            reply = karzon_turbo(prompt)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

st.markdown('<div class="footer">© 2026 KARZON AI - VED PRAKASH</div>', unsafe_allow_html=True)
