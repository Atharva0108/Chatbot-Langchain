import utils
import streamlit as st
import time
from streaming import StreamHandler
from langchain.chains import ConversationChain

# Page configuration
st.set_page_config(page_title="Basic Chatbot", page_icon="🤖", layout="wide")

# Header (clean and centered)
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color:#1e7ebf;">Basic AI Chatbot</h1>
    <p style="color:#666; font-size:16px;">Chat with the AI using Ollama or your own API key</p>
</div>
""", unsafe_allow_html=True)


class BasicChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    def setup_chain(self):
        return ConversationChain(llm=self.llm, verbose=False)

    @utils.enable_chat_history
    def main(self):
        chain = self.setup_chain()
        user_query = st.chat_input(placeholder="Type your question here...")
        if user_query:
            utils.display_msg(user_query, 'user')
            with st.chat_message("assistant"):
                placeholder = st.empty()

                # Animated "typing dots"
                for _ in range(6):  # short cycle (adjustable)
                    for dots in ["", ".", "..", "..."]:
                        placeholder.markdown(f"<span style='color:#666; font-size:16px;'>Thinking{dots}</span>", unsafe_allow_html=True)
                        time.sleep(0.4)

                # Stream response (replaces dots)
                st_cb = StreamHandler(placeholder)
                result = chain.invoke(
                    {"input": user_query},
                    {"callbacks": [st_cb]}
                )
                response = result["response"]
                st.session_state.messages.append({"role": "assistant", "content": response})
                utils.print_qa(BasicChatbot, user_query, response)


if __name__ == "__main__":
    obj = BasicChatbot()
    obj.main()
