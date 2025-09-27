import os
import openai
import streamlit as st
from datetime import datetime
from streamlit.logger import get_logger
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

logger = get_logger('Langchain-Chatbot')


# Decorator for chat history
def enable_chat_history(func):
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)
    return execute


# Display message in Streamlit chat
def display_msg(msg, author):
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)


# Ask user for their OpenAI API key if they choose to use it
def choose_custom_openai_key():
    with st.sidebar.expander("🔑 OpenAI API Settings", expanded=True):
        openai_api_key = st.text_input(
            label="Enter OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Get your key from: https://platform.openai.com/account/api-keys"
        )
        if not openai_api_key:
            st.warning("Please add your OpenAI API key to continue.")
            st.stop()

        try:
            client = openai.OpenAI(api_key=openai_api_key)
            available_models = [
                {"id": i.id, "created": datetime.fromtimestamp(i.created)}
                for i in client.models.list()
                if str(i.id).startswith("gpt")
            ]
            available_models = sorted(available_models, key=lambda x: x["created"])
            model_list = [i["id"] for i in available_models]

            model = st.selectbox(
                label="Select GPT Model",
                options=model_list,
                help="Choose the GPT model you want to use",
            )
        except openai.AuthenticationError as e:
            st.error(e.body["message"])
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    return model, openai_api_key


# Configure LLM (Ollama default + optional OpenAI API)
def configure_llm():
    with st.sidebar.expander("🧠 Select Language Model", expanded=True):
        llm_options = ["Local Ollama (llama3.2:1b)", "Use my OpenAI API key"]
        llm_choice = st.radio(
            label="Choose LLM",
            options=llm_options,
            help="Local Ollama is recommended for offline use. OpenAI API requires your API key."
        )

        if llm_choice == "Local Ollama (llama3.2:1b)":
            llm = ChatOllama(model="llama3.2:1b", base_url=st.secrets["OLLAMA_ENDPOINT"])
        else:
            model, api_key = choose_custom_openai_key()
            llm = ChatOpenAI(model_name=model, temperature=0, streaming=True, api_key=api_key)

    return llm


# Log QA interactions
def print_qa(cls, question, answer):
    log_str = "\nUsecase: {}\nQuestion: {}\nAnswer: {}\n" + "------"*10
    logger.info(log_str.format(cls.__name__, question, answer))


# Embedding model
@st.cache_resource
def configure_embedding_model():
    embedding_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return embedding_model


# Sync session
def sync_st_session():
    for k, v in st.session_state.items():
        st.session_state[k] = v
