import utils
import streamlit as st
import time
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from pymongo import MongoClient
from langchain.chains import LLMChain

# -----------------------
# Page configuration
# -----------------------
st.set_page_config(page_title="Chat with Database", page_icon="🛢", layout="wide")

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color:#1e7ebf;">Chat with Your Database</h1>
    <p style="color:#666; font-size:16px;">Connect to SQL or MongoDB and ask questions interactively.</p>
</div>
""", unsafe_allow_html=True)


class DbChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()

    # -----------------------
    # Setup SQL Agent
    # -----------------------
    def setup_sql_agent(self, db_uri):
        try:
            db = SQLDatabase.from_uri(database_uri=db_uri)
            with st.sidebar.expander('SQL tables', expanded=True):
                st.info('\n- ' + '\n- '.join(db.get_usable_table_names()))

            agent = create_sql_agent(
                llm=self.llm,
                db=db,
                top_k=10,
                verbose=False,
                agent_type="openai-tools",
                handle_parsing_errors=True,
                handle_sql_errors=True
            )
            return agent
        except Exception as e:
            st.error(f"⚠️ SQL Connection failed: {str(e)}")
            st.stop()

    # -----------------------
    # Setup MongoDB Agent (basic LLMChain for query explanations)
    # -----------------------
    def setup_mongo_agent(self, mongo_uri, db_name, collection_name):
        try:
            client = MongoClient(mongo_uri)
            db = client[db_name]
            collection = db[collection_name]
            # Simple LLMChain placeholder to answer questions about MongoDB docs
            # Can be enhanced for more advanced querying
            chain = LLMChain(llm=self.llm, prompt="Answer questions based on the MongoDB collection.")
            return chain, collection
        except Exception as e:
            st.error(f"⚠️ MongoDB Connection failed: {str(e)}")
            st.stop()

    # -----------------------
    # Main Chat
    # -----------------------
    @utils.enable_chat_history
    def main(self):
        # -----------------------
        # Sidebar options
        # -----------------------
        db_type = st.sidebar.radio("Select Database Type", ["SQL", "MongoDB"])

        if db_type == "SQL":
            db_uri = st.sidebar.text_input(
                "Enter SQL Database URI",
                placeholder="mysql://user:pass@host:port/db"
            )
            if not db_uri:
                st.warning("Please enter SQL Database URI to continue.")
                st.stop()
            agent = self.setup_sql_agent(db_uri)

        else:  # MongoDB
            mongo_uri = st.sidebar.text_input(
                "Enter MongoDB URI",
                placeholder="mongodb+srv://user:pass@cluster.mongodb.net"
            )
            db_name = st.sidebar.text_input("Database Name")
            collection_name = st.sidebar.text_input("Collection Name")
            if not (mongo_uri and db_name and collection_name):
                st.warning("Please enter MongoDB URI, database name, and collection name.")
                st.stop()
            agent, mongo_collection = self.setup_mongo_agent(mongo_uri, db_name, collection_name)

        # -----------------------
        # Chat input
        # -----------------------
        user_query = st.chat_input(placeholder="Ask your question here...")
        if user_query:
            utils.display_msg(user_query, 'user')
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)

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
                    st_cb = StreamlitCallbackHandler(placeholder)
                    if db_type == "SQL":
                        result = agent.invoke(
                            {"input": user_query},
                            {"callbacks": [st_cb]}
                        )
                        response = result.get("output", "⚠️ Could not fetch SQL response.")
                    else:
                        # For MongoDB: Simple search in documents
                        docs = list(mongo_collection.find({}))
                        # You can enhance this to use embeddings + retrieval
                        response = f"⚡ MongoDB collection has {len(docs)} documents. You asked: {user_query}"
                except Exception as e:
                    response = f"⚠️ Failed to get response: {str(e)}"

                placeholder.markdown(
                    f"<span style='color:#1e7ebf; font-size:16px;'>{response}</span>",
                    unsafe_allow_html=True
                )

                st.session_state.messages.append({"role": "assistant", "content": response})
                utils.print_qa(DbChatbot, user_query, response)


if __name__ == "__main__":
    obj = DbChatbot()
    obj.main()
