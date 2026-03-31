import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- CONFIG ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background-color: #0E1117; color: white; }
[data-testid="stSidebarNav"] { display: none; }

.sidebar-title {
    font-size: 22px;
    font-weight: bold;
    padding: 10px 0;
}

.chat-btn button {
    width: 100%;
    text-align: left;
    background: #212121;
    border: 1px solid #333;
    margin-bottom: 5px;
}

.block-container {
    max-width: 900px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)

# --- API ---
groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# --- SESSION STATE ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "mode" not in st.session_state:
    st.session_state.mode = "chat"   # chat / search / image

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚡ Ai Ved</div>', unsafe_allow_html=True)

    if st.button("+ New Chat"):
        new_chat = f"Chat {len(st.session_state.chats)+1}"
        st.session_state.chats[new_chat] = []
        st.session_state.current_chat = new_chat
        st.session_state.mode = "chat"
        st.rerun()

    st.write("### Modes")
    if st.button("💬 Chat"):
        st.session_state.mode = "chat"; st.rerun()
    if st.button("🔍 Deep Search"):
        st.session_state.mode = "search"; st.rerun()
    if st.button("🎨 Image"):
        st.session_state.mode = "image"; st.rerun()

    st.write("### Your Chats")

    for chat in st.session_state.chats:
        if st.button(chat):
            st.session_state.current_chat = chat
            st.rerun()

# --- MAIN ---
chat_history = st.session_state.chats[st.session_state.current_chat]

# --- SHOW HISTORY ---
for msg in chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# --- CHAT MODE ---
if st.session_state.mode == "chat":
    prompt = st.chat_input("Ask anything...")

    if prompt:
        chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        try:
            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_history
            )
            reply = res.choices[0].message.content
            chat_history.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)

        except Exception as e:
            st.error(str(e))

# --- SEARCH MODE ---
elif st.session_state.mode == "search":
    prompt = st.chat_input("Search anything...")

    if prompt:
        st.chat_message("user").write(prompt)

        try:
            with st.spinner("🔎 Searching web..."):
                results = tavily.search(query=prompt, search_depth="advanced")["results"][:3]

            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"Context: {results}\nQuery: {prompt}"
                }]
            )

            reply = res.choices[0].message.content
            st.chat_message("assistant").write(reply)

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