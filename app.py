import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client

# --- CONFIG ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp { background-color: #0E1117; color: white; }
[data-testid="stSidebarNav"] { display: none; }
.sidebar-title { font-size: 24px; font-weight: bold; padding: 20px 0px; }
.stButton>button {
    width: 100%; border-radius: 8px; border: 1px solid #444;
    background: #212121; color: white; text-align: left; padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- SESSION ---
if "login" not in st.session_state:
    st.session_state.login = False
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- LOGIN ---
if not st.session_state.login:
    st.title("Login")

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
            st.error("Invalid login")

# --- APP ---
else:
    # SIDEBAR
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Ai Ved</div>', unsafe_allow_html=True)

        if st.button("+ Home"):
            st.session_state.page = "Home"; st.rerun()
        if st.button("💬 Simple"):
            st.session_state.page = "Simple"; st.rerun()
        if st.button("🚀 High"):
            st.session_state.page = "High"; st.rerun()
        if st.button("🔍 Search"):
            st.session_state.page = "Search"; st.rerun()
        if st.button("🎨 Image"):
            st.session_state.page = "Image"; st.rerun()

        if st.button("Logout"):
            st.session_state.login = False
            st.rerun()

    # --- HOME ---
    if st.session_state.page == "Home":
        st.title("Ai Ved Pro")

    # --- SIMPLE CHAT ---
    elif st.session_state.page == "Simple":
        st.title("Simple Chat")

        prompt = st.chat_input("Ask anything...")
        if prompt:
            try:
                res = groq.chat.completions.create(
                    model="llama-3.3-8b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.chat_message("assistant").write(res.choices[0].message.content)
            except Exception as e:
                st.error(str(e))

    # --- HIGH CHAT ---
    elif st.session_state.page == "High":
        st.title("High Chat")

        prompt = st.chat_input("Ask complex question...")
        if prompt:
            try:
                res = groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.chat_message("assistant").write(res.choices[0].message.content)
            except Exception as e:
                st.error(str(e))

    # --- SEARCH ---
    elif st.session_state.page == "Search":
        st.title("Deep Search")

        prompt = st.chat_input("Search web...")
        if prompt:
            try:
                with st.status("Searching..."):
                    results = tavily.search(query=prompt, search_depth="advanced")["results"][:3]

                res = groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{
                        "role": "user",
                        "content": f"Context: {results}\nQuery: {prompt}"
                    }]
                )
                st.chat_message("assistant").write(res.choices[0].message.content)

            except Exception as e:
                st.error(str(e))

    # --- IMAGE ---
    elif st.session_state.page == "Image":
        st.title("Image Generator")

        prompt = st.text_input("Enter prompt")

        if st.button("Generate"):
            if prompt:
                st.image(
                    f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024"
                )
            else:
                st.warning("Enter prompt")