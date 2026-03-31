import streamlit as st
import os
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

# --- STEP 1: LOAD SECURE KEYS ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize Clients
try:
    client = Groq(api_key=GROQ_API_KEY)
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
except Exception:
    st.error("⚠️ API Keys missing! Check your .env file.")

# --- STEP 2: COOL GLASS-MORPHISM UI (TERA PURANA STYLE) ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070A; color: #E6EDF3; }
    [data-testid="stSidebar"] { background-color: #0D1117; border-right: 1px solid #30363D; }
    .chat-bubble { padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #30363D; }
    .user-msg { background-color: #1F2937; border-left: 4px solid #007BFF; }
    .ai-msg { background-color: rgba(255, 255, 255, 0.02); border-left: 4px solid #00FF88; line-height: 1.7; }
    
    /* Tera Cool Rotating Logo Animation */
    @keyframes rotate-glow {
        0% { transform: rotate(0deg); box-shadow: 0 0 15px #007BFF; }
        100% { transform: rotate(360deg); box-shadow: 0 0 15px #00FF88; }
    }
    .loading-logo { 
        width: 50px; height: 50px; border-radius: 50%; 
        margin: 20px auto; animation: rotate-glow 1.5s linear infinite;
        border: 2px solid transparent;
        background: linear-gradient(#05070A, #05070A) padding-box,
                    linear-gradient(45deg, #007BFF, #00FF88) border-box;
    }

    .main-title {
        font-size: 3.5rem; font-weight: 800;
        background: linear-gradient(45deg, #007BFF, #00FF88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- STEP 3: SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- STEP 4: SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🚀 Ai Ved Navigation</h2>", unsafe_allow_html=True)
    app_mode = st.selectbox("Switch Service", ["💬 Smart Assistant", "🎨 Image Studio"])
    
    st.divider()
    if app_mode == "💬 Smart Assistant":
        use_web_search = st.toggle("Enable Live Web Search", value=True)
    
    if st.button("🗑️ Clear My Stuff", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- STEP 5: SMART ASSISTANT LOGIC ---
if app_mode == "💬 Smart Assistant":
    st.markdown('<p class="main-title">Ai Ved</p>', unsafe_allow_html=True)

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            role_class = "user-msg" if message["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

    # Input area
    query = st.chat_input("Ask Ai Ved...")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-bubble user-msg">{query}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant"):
            # Tera Cool Loader
            placeholder = st.empty()
            placeholder.markdown('<div class="loading-logo"></div><p style="text-align:center; color:#00FF88;">Searching & Thinking...</p>', unsafe_allow_html=True)

            try:
                context = ""
                if use_web_search:
                    search_data = tavily.search(query=query, search_depth="advanced")
                    context = "\n".join([r.get('content') for r in search_data.get('results', [])[:3]])
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are Ai Ved. Reply in user's language. Use Markdown."},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
                    ],
                    stream=True
                )

                placeholder.empty() # Loader hata do jab answer aaye
                full_res = ""
                res_area = st.empty()
                
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_area.markdown(f'<div class="chat-bubble ai-msg">{full_res}</div>', unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "content": full_res})

            except Exception as e:
                placeholder.empty()
                st.error(f"Error: {e}")

# --- STEP 6: IMAGE STUDIO LOGIC ---
elif app_mode == "🎨 Image Studio":
    st.markdown('<p class="main-title">Image Studio</p>', unsafe_allow_html=True)
    st.write("### Create High-Quality Art for Free")
    
    img_prompt = st.text_area("Describe your visual idea:", placeholder="Example: A futuristic city in Bihar, hyper-realistic, 8k")
    
    if st.button("Generate Masterpiece ✨", use_container_width=True):
        if img_prompt:
            with st.spinner("Ai Ved is painting..."):
                clean_p = img_prompt.replace(" ", "%20")
                img_url = f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true"
                
                st.divider()
                st.image(img_url, use_column_width=True)
                st.link_button("📥 Download This Image", img_url, use_container_width=True)
        else:
            st.warning("Please type something first!")

# --- FOOTER ---
st.markdown("<div style='text-align:center; margin-top:50px; opacity:0.3; font-size:0.8rem;'>© 2026 | Built by Ved Parkash</div>", unsafe_allow_html=True)