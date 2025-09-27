import os
import utils
import requests
import traceback
import validators
import streamlit as st
from streaming import StreamHandler
from bs4 import BeautifulSoup
import time

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch

# Page configuration
st.set_page_config(page_title="ChatWebsite", page_icon="🔗", layout="wide")

st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color:#1e7ebf;">Chat with Website</h1>
    <p style="color:#666; font-size:16px;">Interact with website contents in real-time</p>
</div>
""", unsafe_allow_html=True)


class ChatbotWeb:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()
        self.embedding_model = utils.configure_embedding_model()

    def scrape_website(self, url):
        """Scrape visible text and metadata from website"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get title
            title = soup.title.string.strip() if soup.title else "No title found"

            # Extract visible text
            texts = soup.stripped_strings
            visible_text = " ".join(texts)

            # Count internal links (approximate number of pages)
            links = [a['href'] for a in soup.find_all('a', href=True)]
            page_count = len(links)

            return {"title": title, "text": visible_text, "pages": page_count, "url": url}

        except Exception as e:
            traceback.print_exc()
            return {"title": "Error", "text": "", "pages": 0, "url": url}

    @st.cache_resource(show_spinner='Analyzing websites', ttl=3600)
    def setup_vectordb(_self, websites):
        docs = []
        for url in websites:
            data = _self.scrape_website(url)
            if data['text']:
                metadata = {"source": data['url'], "title": data['title'], "pages": data['pages']}
                docs.append(Document(page_content=data['text'], metadata=metadata))

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectordb = DocArrayInMemorySearch.from_documents(splits, _self.embedding_model)
        return vectordb

    def setup_qa_chain(self, vectordb):
        retriever = vectordb.as_retriever(search_type='mmr', search_kwargs={'k': 2, 'fetch_k': 4})
        memory = ConversationBufferMemory(memory_key='chat_history', output_key='answer', return_messages=True)
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm, retriever=retriever, memory=memory,
            return_source_documents=True, verbose=False
        )
        return qa_chain

    @utils.enable_chat_history
    def main(self):
        if "websites" not in st.session_state:
            st.session_state["websites"] = []

        web_url = st.sidebar.text_area(
            label='Enter Website URL',
            placeholder="https://example.com"
        )

        if st.sidebar.button(":heavy_plus_sign: Add Website"):
            if not web_url or not (web_url.startswith('http') and validators.url(web_url)):
                st.sidebar.error("Invalid URL! Please enter a valid website URL.", icon="⚠️")
            else:
                st.session_state["websites"].append(web_url.strip())

        if st.sidebar.button("Clear"):
            st.session_state["websites"] = []

        websites = list(set(st.session_state["websites"]))
        if not websites:
            st.error("Please enter at least one valid website URL to continue!")
            st.stop()
        else:
            st.sidebar.info("Websites - \n - {}".format('\n - '.join(websites)))

        vectordb = self.setup_vectordb(websites)
        qa_chain = self.setup_qa_chain(vectordb)

        user_query = st.chat_input(placeholder="Ask me anything!")
        if user_query:
            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):
                placeholder = st.empty()

                for dots in ["", ".", "..", "..."]:
                    placeholder.markdown(
                        f"<span style='color:#666;'>Searching{dots}</span>", unsafe_allow_html=True
                    )
                    time.sleep(0.3)

                try:
                    st_cb = StreamHandler(placeholder)
                    result = qa_chain.invoke({"question": user_query}, {"callbacks": [st_cb]})
                    response = result.get("answer", "⚠️ Couldn’t fetch a proper response.")
                except Exception as e:
                    response = f"⚠️ Failed to fetch response: {str(e)}"

                placeholder.markdown(f"<span style='color:#1e7ebf;'>{response}</span>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})
                utils.print_qa(ChatbotWeb, user_query, response)

                for idx, doc in enumerate(result.get('source_documents', []), 1):
                    ref_title = f":blue[Reference {idx}: *{doc.metadata.get('title','Unknown')}*]"
                    with st.popover(ref_title):
                        st.caption(doc.page_content[:500] + "...")  # show first 500 chars


if __name__ == "__main__":
    obj = ChatbotWeb()
    obj.main()
