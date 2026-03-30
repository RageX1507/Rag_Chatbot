import streamlit as st
import base64
import time

from main import build_indexes
from chains.rag_chain import handle_query, generate_suggestions


st.set_page_config(
    page_title="Wattmonk AI",
    page_icon="assets/wattmonk.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

header {visibility: visible;}
footer {visibility: hidden;}

.chat-container {
    max-width: 750px;
    margin: auto;
    padding: 10px;
}

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

.suggestion-pill {
    background:#1f2937;
    color:#ffffff;
    padding:8px 14px;
    border-radius:20px;
    text-align:center;
    font-size:13px;
    border:1px solid #374151;
    white-space:nowrap;
}
</style>
""", unsafe_allow_html=True)


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


img_base64 = get_base64_image("assets/wattmonk.png")


st.markdown(f"""
<div class="bot-msg"
style="
text-align:center;
margin: 20px auto;
max-width: 420px;
">

<img src="data:image/png;base64,{img_base64}"
width="160"
style="
display:block;
margin:auto;
padding-top:10px;
filter: drop-shadow(0px 0px 6px rgba(0,0,0,0.3));
"/>

<div style="
font-size:20px;
margin-top:8px;
font-weight:600;
">
Chatbot
</div>

</div>
""", unsafe_allow_html=True)


with st.sidebar:

    st.title("⚙️ Controls")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []

    st.markdown("---")
    st.write("**Model:** Llama-3.1-8b")
    st.write("**Mode:** RAG (NEC + Wattmonk) & General")


@st.cache_resource
def load_system():
    return build_indexes()


nec_index, wattmonk_index = load_system()


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


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


st.markdown("<div class='chat-container'>", unsafe_allow_html=True)


for role, message in st.session_state.chat_history:

    if role == "user":

        st.markdown(
            f"<div class='user-msg'>{message}</div>",
            unsafe_allow_html=True
        )

    else:

        answer = message["answer"]
        source = message["source"]
        confidence = message["confidence"]
        docs = message["docs"]

        st.markdown(
            f"<div class='bot-msg'>{answer}</div>",
            unsafe_allow_html=True
        )

        if source and source != "General Knowledge":

            st.markdown(
                f"""
                <div style="font-size:12px;color:#888;margin-left:10px;">
                Source: {source} | Confidence: {confidence}
                </div>
                """,
                unsafe_allow_html=True
            )

        if docs:

            with st.expander("📄 View Sources"):

                for i, doc in enumerate(docs):

                    st.markdown(f"**Chunk {i+1}:**")

                    st.write(
                        doc.page_content[:300] + "..."
                    )

        if answer:

            suggestions = generate_suggestions(answer)

            if suggestions:

                cols = st.columns(len(suggestions))

                for i, s in enumerate(suggestions):

                    cols[i].markdown(
                        f"""
                        <div class="suggestion-pill">
                            {s}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


st.markdown("</div>", unsafe_allow_html=True)


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
