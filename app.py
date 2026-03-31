import streamlit as st
from groq import Groq
from tavily import TavilyClient
from supabase import create_client, Client

# --- 1. SEO & GOOGLE VERIFICATION ---
st.set_page_config(page_title="Ai Ved Pro", page_icon="⚡", layout="wide")

st.markdown(f"""
    <head>
        <meta name="google-site-verification" content="Jt9DVZe2CIYVCVioXQBo-pO_mWQF-v0Lirpha0NE74A" />
    </head>
    <style>
        .stApp {{ background-color: #0E1117; color: white; }}
        /* Hide default streamlit navigation */
        [data-testid="stSidebarNav"] {{ display: none; }}
        
        /* Sidebar Branding Style */
        .sidebar-title {{ 
            font-size: 26px; 
            font-weight: bold; 
            padding: 20px 0px; 
            color: #10a37f; 
            letter-spacing: 1px;
        }}
        
        /* Professional Button Styling */
        .stButton>button {{
            width: 100%;
            border-radius: 8px;
            border: 1px solid #333;
            background: #1A1A1A;
            color: white;
            text-align: left;
            padding: 12px 15px;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background: #2D2D2D !important;
            border-color: #10a37f;
        }}
        
        /* Branding Footer */
        .footer-text {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            font-size: 12px;
            color: #555;
            line-height: 1.5;
        }}
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND CONNECTIONS ---
url, key = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "page" not in st.session_state: st.session_state.page = "Chat"

# --- 3. AUTHENTICATION GATE ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Sign in to Ai Ved</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        email = st.text_input("Email Address", placeholder="e.g. user@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Continue"):
            try:
                supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.logged_in = True
                st.rerun()
            except:
                st.error("Authentication failed. Please check your credentials.")

# --- 4. MAIN DASHBOARD ---
else:
    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Ai Ved</div>', unsafe_allow_html=True)
        
        if st.button("💬 Ask Ai Ved"): 
            st.session_state.page = "Chat"
            st.rerun()
        if st.button("🔍 Real-Time Search"): 
            st.session_state.page = "Search"
            st.rerun()
        if st.button("🎨 Image Studio"): 
            st.session_state.page = "Image"
            st.rerun()
        
        st.divider()
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.rerun()
            
        # THE BRANDING FOOTER
        st.markdown("""
            <div class="footer-text">
                Since 2026<br>
                <b>Built by Ved Prakash</b><br>
                All Rights Reserved.
            </div>
        """, unsafe_allow_html=True)

    # --- CONTENT ENGINES ---
    
    # 4a. CHAT ENGINE
    if st.session_state.page == "Chat":
        st.title("Ask Ai Ved")
        st.info("Powered by Next-Gen Neural Networks")
        
        user_input = st.chat_input("How can I help you today?")
        if user_input:
            with st.chat_message("user"): 
                st.write(user_input)
            
            # Using the most stable high-speed model
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[{"role": "user", "content": user_input}]
            )
            
            with st.chat_message("assistant"): 
                st.write(response.choices[0].message.content)

    # 4b. REAL-TIME SEARCH ENGINE
    elif st.session_state.page == "Search":
        st.title("Real-Time Search")
        st.write("Get live updates from across the web.")
        
        search_query = st.chat_input("Search for live news, weather, or sports...")
        if search_query:
            with st.status("Scanning global data sources..."):
                results = tavily.search(query=search_query, search_depth="advanced")
                context = "\n".join([f"{r['title']}: {r['content']}" for r in results['results']])
            
            ai_res = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are Ai Ved. Provide an accurate answer based on the real-time context provided."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {search_query}"}
                ]
            )
            st.chat_message("assistant").write(ai_res.choices[0].message.content)

    # 4c. IMAGE GENERATION STUDIO
    elif st.session_state.page == "Image":
        st.title("Image Studio")
        st.write("Convert your text into high-quality digital art.")
        
        image_desc = st.text_input("Describe the image you want to create...", placeholder="e.g. A futuristic city in 2050 with flying cars")
        if st.button("Generate Art"):
            if image_desc:
                with st.spinner("Processing your imagination..."):
                    img_url = f"https://pollinations.ai/p/{image_desc.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux"
                    st.image(img_url, caption=f"Generated Artifact: {image_desc}")
            else:
                st.warning("Please enter a description first.")