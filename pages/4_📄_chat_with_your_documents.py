import os
import utils
import streamlit as st
import time
from streaming import StreamHandler

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------
# Page configuration
# -----------------------
st.set_page_config(page_title="Chat with Documents", page_icon="📄", layout="wide")

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color:#1e7ebf;">Chat with Your Documents</h1>
    <p style="color:#666; font-size:16px;">Upload PDFs and ask questions. Get answers referencing the content.</p>
</div>
""", unsafe_allow_html=True)


class CustomDocChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()
        self.embedding_model = utils.configure_embedding_model()

    def save_file(self, file):
        folder = 'tmp'
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_path = f'./{folder}/{file.name}'
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
        return file_path

    @st.spinner('Analyzing documents...')
    def setup_qa_chain(self, uploaded_files):
        # Load documents
        docs = []
        for file in uploaded_files:
            file_path = self.save_file(file)
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())
        
        # Split documents and store in vector db
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        vectordb = DocArrayInMemorySearch.from_documents(splits, self.embedding_model)

        # Define retriever
        retriever = vectordb.as_retriever(
            search_type='mmr',
            search_kwargs={'k':2, 'fetch_k':4}
        )

        # Setup memory for contextual conversation        
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            output_key='answer',
            return_messages=True
        )

        # Setup LLM and QA chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=False
        )
        return qa_chain

    @utils.enable_chat_history
    def main(self):

        # Sidebar for PDF uploads
        uploaded_files = st.sidebar.file_uploader(
            label='Upload PDF files',
            type=['pdf'],
            accept_multiple_files=True
        )
        if not uploaded_files:
            st.warning("Please upload PDF documents to start chatting!")
            st.stop()

        user_query = st.chat_input(placeholder="Ask your question based on uploaded documents...")

        if uploaded_files and user_query:
            try:
                qa_chain = self.setup_qa_chain(uploaded_files)
            except Exception as e:
                st.error(f"⚠️ Error processing documents: {str(e)}")
                st.stop()

            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):
                placeholder = st.empty()

                # Typing animation
                for dots in ["", ".", "..", "..."]:
                    placeholder.markdown(
                        f"<span style='color:#666; font-size:16px;'>Processing{dots}</span>",
                        unsafe_allow_html=True
                    )
                    time.sleep(0.3)

                try:
                    st_cb = StreamHandler(placeholder)
                    result = qa_chain.invoke(
                        {"question": user_query},
                        {"callbacks": [st_cb]}
                    )
                    response = result.get("answer", "⚠️ Couldn’t fetch a proper answer.")

                except Exception as e:
                    response = f"⚠️ Failed to get response: {str(e)}"

                # Display answer
                placeholder.markdown(
                    f"<span style='color:#1e7ebf; font-size:16px;'>{response}</span>",
                    unsafe_allow_html=True
                )

                st.session_state.messages.append({"role": "assistant", "content": response})
                utils.print_qa(CustomDocChatbot, user_query, response)

                # Display references in interactive popovers
                if 'source_documents' in result:
                    for idx, doc in enumerate(result['source_documents'], 1):
                        filename = os.path.basename(doc.metadata['source'])
                        page_num = doc.metadata.get('page', 'N/A')
                        ref_title = f":blue[Reference {idx}: *{filename} - page {page_num}*]"
                        with st.expander(ref_title):
                            st.write(doc.page_content)


if __name__ == "__main__":
    obj = CustomDocChatbot()
    obj.main()
