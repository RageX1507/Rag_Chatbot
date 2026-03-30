import streamlit as st
import base64
from main import build_indexes
from chains.rag_chain import handle_query, generate_suggestions
# Page config
st.set_page_config(
    page_title="Wattmonk AI",
    page_icon="assets/wattmonk.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>

/* Layout */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

/* Keep header for sidebar toggle */
header {visibility: visible;}
footer {visibility: hidden;}

/* Sidebar toggle always visible */
[data-testid="collapsedControl"] {
    display: block !important;
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 9999;
    background-color: #262626;
    padding: 6px 10px;
    border-radius: 8px;
}

[data-testid="collapsedControl"] button {
    color: white !important;
}

/* Chat container */
.chat-container {
    max-width: 750px;
    margin: auto;
    padding: 10px;
}

/* USER MESSAGE */
.user-msg {
    background-color: #2f80ed;
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px 0;

    max-width: 60%;
    margin-left: auto;
    margin-right: 10px;

    text-align: right;
    word-wrap: break-word;
}

/* BOT MESSAGE */
.bot-msg {
    background-color: #262626;
    color: #eaeaea;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px 0;

    max-width: 65%;
    margin-left: 10px;
    margin-right: auto;

    text-align: left;
    border: 1px solid #333;
    word-wrap: break-word;
}

/* Hover */
.user-msg:hover, .bot-msg:hover {
    transform: scale(1.01);
    transition: 0.2s ease;
}

/* Responsive input */
.stChatInput {
    position: fixed;
    bottom: 20px;
    width: min(700px, calc(100% - 300px));
    left: calc(50% + 100px);
    transform: translateX(-50%);
}

/* When sidebar collapsed */
[data-testid="stSidebar"][aria-expanded="false"] ~ div .stChatInput {
    width: min(700px, calc(100% - 100px));
    left: 50%;
}

</style>
""", unsafe_allow_html=True)

# Load logo
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64_image("assets/wattmonk.png")

# HEADER 
st.markdown(f"""
<div style="text-align:center; margin-top:30px; margin-bottom:20px;">

<img src="data:image/png;base64,{img_base64}" width="160"
style="display:block; margin:auto; padding-top:10px;
filter: drop-shadow(0px 0px 8px rgba(255,200,0,0.4));"/>

<div style="font-size:20px; color:#eaeaea; margin-top:8px; font-weight:500;">
Chatbot
</div>

</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Controls")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []

    st.markdown("---")
    st.write("**Model:** Llama-3.1-8b")
    st.write("**Mode:** RAG (NEC + Wattmonk) & General")

# Load system
@st.cache_resource
def load_system():
    return build_indexes()

nec_index, wattmonk_index = load_system()

# Memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input
query = st.chat_input("Ask me anything...")

if query:
    st.session_state.chat_history.append(("user", query))

    with st.spinner("Thinking... 🤔"):
        response = handle_query(
    query,
    nec_index,
    wattmonk_index,
    st.session_state.chat_history
)

    st.session_state.chat_history.append(("bot", response))

# Chat display
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='user-msg'>{message}</div>", unsafe_allow_html=True)
    else:
        answer = message["answer"]
        source = message["source"]
        confidence = message["confidence"]
        docs = message["docs"]

        st.markdown(f"<div class='bot-msg'>{answer}</div>", unsafe_allow_html=True)

# Show source + confidence 
        if source and source != "General Knowledge":
            st.markdown(f"""
            <div style="font-size:12px;color:#888;margin-left:10px;">
            Source: {source} | Confidence: {confidence}
            </div>
            """, unsafe_allow_html=True)

# Show citations
        if docs:
            with st.expander("📄 View Sources"):
                for i, doc in enumerate(docs):
                    st.markdown(f"**Chunk {i+1}:**")
                    st.write(doc.page_content[:300] + "...")
# Suggestions

suggestions = generate_suggestions(query)
if suggestions:

    st.markdown(
        "<div style='margin-left:10px;'>",
        unsafe_allow_html=True
    )

    for s in suggestions:

        if st.button(
            s,
            key=f"suggestion_{s}"
        ):

            st.session_state.chat_history.append(
                ("user", s)
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )
st.markdown("</div>", unsafe_allow_html=True)
import time

def stream_text(text, speed=0.01):
    placeholder = st.empty()
    output = ""

    for char in text:
        output += char
        placeholder.markdown(
            f"<div class='bot-msg'>{output}</div>",
            unsafe_allow_html=True
        )
        time.sleep(speed)
