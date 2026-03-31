import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- CONFIG ---
st.set_page_config(page_title="AI Ved", page_icon="⚡", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background-color: #0B0F19; color: #ECECF1; }

[data-testid="stSidebarNav"] { display: none; }

.block-container {
    max-width: 800px;
    margin: auto;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Footer fix */
.footer {
    position: fixed;
    bottom: 8px;
    left: 0;
    right: 0;
    text-align: center;
    color: #888;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# --- FOOTER (FIXED) ---
st.markdown('<div class="footer">AI Ved can make mistakes. Check important info.</div>', unsafe_allow_html=True)

# --- TITLE (IMPORTANT FIX) ---
st.markdown("<h2 style='text-align:center;'>⚡ AI Ved</h2>", unsafe_allow_html=True)

# --- API ---
groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
Talk like a real human.
Reply in user's language (Hindi/Hinglish/English).
Keep it short and natural.
Don't repeat.
Don't give fake info.
"""

# --- SESSION ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "mode" not in st.session_state:
    st.session_state.mode = "chat"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ AI Ved")

    if st.button("+ New chat"):
        name = f"Chat {len(st.session_state.chats)+1}"
        st.session_state.chats[name] = []
        st.session_state.current_chat = name
        st.session_state.mode = "chat"
        st.rerun()

    st.write("### Modes")

    if st.button("💬 Chat"):
        st.session_state.mode = "chat"
        st.rerun()

    if st.button("🔍 Real-Time Search"):
        st.session_state.mode = "search"
        st.rerun()

    st.write("### Your Chats")

    for chat in st.session_state.chats:
        if st.button(chat):
            st.session_state.current_chat = chat
            st.rerun()

# --- MAIN ---
chat_history = st.session_state.chats[st.session_state.current_chat]

# SHOW CHAT
for msg in chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# INPUT
prompt = st.chat_input("Ask anything...")

if prompt:
    chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # --- NORMAL CHAT ---
        if st.session_state.mode == "chat":
            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + chat_history,
                temperature=0.7,
                max_tokens=500
            )
            reply = res.choices[0].message.content.strip()

        # --- REAL-TIME SEARCH ---
        else:
            with st.spinner(""):
                results = tavily.search(
                    query=prompt + " latest news india today",
                    search_depth="advanced"
                )["results"][:5]

            res = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a real-time news assistant.

- Use only given data
- No fake news
- Give latest real info
- Talk like human (Hindi/Hinglish)
"""
                    },
                    {
                        "role": "user",
                        "content": f"DATA:\n{results}\n\nQuestion: {prompt}"
                    }
                ],
                temperature=0.5
            )

            reply = res.choices[0].message.content.strip()

        chat_history.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)

    except Exception as e:
        st.error(str(e))