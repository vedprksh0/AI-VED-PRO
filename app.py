import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

# --- CUSTOM UI ---
st.markdown("""
<style>
.stApp { background-color: #0E1117; color: white; }
[data-testid="stSidebarNav"] { display: none; }
.sidebar-title {
    font-size: 24px;
    font-weight: bold;
    padding: 20px 0px;
    color: #FFFFFF;
}
.stButton>button {
    width: 100%;
    border-radius: 8px;
    border: 1px solid #444;
    background: #212121;
    color: white;
    text-align: left;
    padding: 10px 15px;
}
.stButton>button:hover {
    background: #2D2D2D !important;
    border-color: #10a37f;
}
</style>
""", unsafe_allow_html=True)

# --- CONNECTIONS ---
url, key = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# --- LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>Sign in to Ai Ved</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Continue"):
            try:
                supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.logged_in = True
                st.rerun()
            except Exception as e:
                st.error("Login failed")

# --- MAIN APP ---
else:
    # SIDEBAR
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Ai Ved</div>', unsafe_allow_html=True)

        if st.button("+ New Chat / Home"):
            st.session_state.current_page = "Home"
            st.rerun()

        st.write("---")

        if st.button("💬 Simple Chat"):
            st.session_state.current_page = "Simple"
            st.rerun()

        if st.button("🚀 High Chat"):
            st.session_state.current_page = "High"
            st.rerun()

        if st.button("🔍 Deep Search"):
            st.session_state.current_page = "Search"
            st.rerun()

        if st.button("🎨 Image Studio"):
            st.session_state.current_page = "Image"
            st.rerun()

        st.write("---")

        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- HOME ---
    if st.session_state.current_page == "Home":
        st.title("Ai Ved Pro")
        st.subheader("How can I help you today?")
        st.info("Select an engine from sidebar")

    # --- SIMPLE CHAT ---
    elif st.session_state.current_page == "Simple":
        st.title("Simple Chat")

        prompt = st.chat_input("Ask anything...")
        if prompt:
            try:
                res = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.chat_message("assistant").write(res.choices[0].message.content)
            except Exception as e:
                st.error(str(e))

    # --- HIGH CHAT ---
    elif st.session_state.current_page == "High":
        st.title("High Chat")

        prompt = st.chat_input("Ask complex question...")
        if prompt:
            try:
                res = groq_client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.chat_message("assistant").write(res.choices[0].message.content)
            except Exception as e:
                st.error(str(e))

    # --- DEEP SEARCH ---
    elif st.session_state.current_page == "Search":
        st.title("Deep Search")

        prompt = st.chat_input("Search web...")
        if prompt:
            try:
                with st.status("Searching..."):
                    data = tavily.search(query=prompt, search_depth="advanced")["results"][:3]

                res = groq_client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[{
                        "role": "user",
                        "content": f"Context: {data}\nQuery: {prompt}"
                    }]
                )

                st.chat_message("assistant").write(res.choices[0].message.content)

            except Exception as e:
                st.error(str(e))

    # --- IMAGE ---
    elif st.session_state.current_page == "Image":
        st.title("Image Studio")

        prompt = st.text_input("Describe image")

        if st.button("Generate"):
            if prompt:
                st.image(
                    f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux"
                )
            else:
                st.warning("Enter prompt")