import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- CONFIG ---
st.set_page_config(page_title="Ai Ved", page_icon="⚡", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background-color: #0E1117; color: white; }
[data-testid="stSidebarNav"] { display: none; }

.block-container { max-width: 900px; margin: auto; }

footer {
    position: fixed;
    bottom: 10px;
    width: 100%;
    text-align: center;
    color: #888;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<footer>Built by Ved Prakash • Since 2026</footer>", unsafe_allow_html=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are a human-like AI assistant.

- Speak naturally like a real person
- Match user's language (Hindi / Hinglish / English)
- Never say you lack real-time data
- If context given → treat it as LIVE info
- Be confident, helpful, and conversational
"""

# --- API ---
groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# --- SESSION ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "mode" not in st.session_state:
    st.session_state.mode = "chat"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Ai Ved")

    if st.button("+ New Chat"):
        name = f"Chat {len(st.session_state.chats)+1}"
        st.session_state.chats[name] = []
        st.session_state.current_chat = name
        st.session_state.mode = "chat"
        st.rerun()

    st.write("### Modes")
    if st.button("💬 Chat"): st.session_state.mode = "chat"; st.rerun()
    if st.button("🔍 Real-Time Search"): st.session_state.mode = "search"; st.rerun()
    if st.button("🎨 Image"): st.session_state.mode = "image"; st.rerun()

    st.write("### Your Chats")
    for c in st.session_state.chats:
        if st.button(c):
            st.session_state.current_chat = c
            st.rerun()

# --- MAIN ---
chat_history = st.session_state.chats[st.session_state.current_chat]

# SHOW HISTORY
for msg in chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# --- STREAMING FUNCTION ---
def stream_text(text):
    for i in range(len(text)):
        yield text[:i+1]

# --- CHAT MODE ---
if st.session_state.mode == "chat":
    prompt = st.chat_input("Ask anything...")

    if prompt:
        chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        try:
            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, *chat_history]
            )

            reply = res.choices[0].message.content
            chat_history.append({"role": "assistant", "content": reply})

            st.chat_message("assistant").write_stream(stream_text(reply))

        except Exception as e:
            st.error(str(e))

# --- SEARCH MODE ---
elif st.session_state.mode == "search":
    prompt = st.chat_input("Search latest news...")

    if prompt:
        st.chat_message("user").write(prompt)

        try:
            with st.spinner("🌍 Searching live data..."):
                results = tavily.search(
                    query=prompt + " latest news 2026",
                    search_depth="advanced"
                )["results"][:5]

            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"""
LIVE DATA:
{results}

User: {prompt}

Answer naturally using this data.
"""
                    }
                ]
            )

            reply = res.choices[0].message.content
            st.chat_message("assistant").write_stream(stream_text(reply))

        except Exception as e:
            st.error(str(e))

# --- IMAGE MODE ---
elif st.session_state.mode == "image":
    st.title("🎨 Image Generator")

    prompt = st.text_input("Describe image")

    if st.button("Generate"):
        if prompt:
            st.image(
                f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024"
            )
        else:
            st.warning("Enter prompt")