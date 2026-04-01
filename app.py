import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import google.generativeai as genai
import time

# --- CONFIG ---
st.set_page_config(page_title="Karzon AI", layout="wide")

# --- STYLE (Exactly your UI) ---
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

# --- API ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Secrets configuration mein issue hai. Please check API keys.")

# --- SEARCH (FIXED FOR 2026 STABILITY) ---
def real_search(query):
    try:
        q = query.lower()
        if "nrews" in q: q = q.replace("nrews", "news")
        
        # Generator logic fix for DDGS 5.0+
        results = list(DDGS().text(f"{q} latest news 2026", max_results=3))
        
        if not results:
            return "No internet context found."
        
        return "\n".join([r.get("body", "") for r in results])
    except:
        return "Search currently unavailable."

# --- IMAGE ---
def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

# --- AI ENGINE (RELIABLE FALLBACK) ---
def karzon_turbo(query):
    context = real_search(query)

    prompt = f"""
    You are Karzon AI.
    RULES:
    - Always reply (never empty)
    - If no data → answer from your knowledge
    - Reply in same language as user
    - Prefer Hinglish + English

    Context: {context}
    Question: {query}
    """

    # Try Groq (Primary)
    try:
        res = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content
    except Exception:
        # Fallback to Gemini (Secondary)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            return "Dono servers busy hain dost. Thodi der baad try karo! (Check Groq/Gemini Limits)"

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
        except:
            st.error("Login failed. Please check credentials.")

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

    # --- CHAT ---
    if st.session_state.mode == "chat":
        # Display existing messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            cls = "user-msg" if msg["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="chat-msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Input area
        if prompt := st.chat_input("Ask anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Show the UI update before the slow API call
            st.markdown(f'<div class="chat-container"><div class="chat-msg user-msg">{prompt}</div></div>', unsafe_allow_html=True)
            
            # Get AI response
            reply = karzon_turbo(prompt)
            
            # Streaming UI effect
            placeholder = st.empty()
            full = ""
            for word in reply.split():
                full += word + " "
                placeholder.markdown(f'<div class="chat-container"><div class="chat-msg ai-msg">{full}▌</div></div>', unsafe_allow_html=True)
                time.sleep(0.01)
            placeholder.markdown(f'<div class="chat-container"><div class="chat-msg ai-msg">{full}</div></div>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full})
            st.rerun()

    # --- NEWS ---
    elif st.session_state.mode == "news":
        query = st.text_input("Search news")
        if query:
            with st.spinner("Searching..."):
                result = karzon_turbo(f"Latest news about: {query}")
                st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)

    # --- IMAGE ---
    elif st.session_state.mode == "image":
        p = st.text_input("Describe image")
        if st.button("Generate Image"):
            with st.spinner("Generating..."):
                img_url = generate_image(p)
                st.image(img_url, use_column_width=True)

    st.markdown('<div class="footer">© 2026 KARZON AI - VED PRAKASH</div>', unsafe_allow_html=True)
