import utils
import streamlit as st
import time
import re
from langchain_community.utilities import GoogleSerperAPIWrapper

# -----------------------
# Page configuration
# -----------------------
st.set_page_config(page_title="Internet Access Chatbot", page_icon="🌐", layout="wide")

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color:#1e7ebf;">AI Chatbot with Internet Access</h1>
    <p style="color:#666; font-size:16px;">Ask questions about recent events with precise real-time answers</p>
</div>
""", unsafe_allow_html=True)


class InternetChatbot:

    def __init__(self):
        utils.sync_st_session()
        # Initialize Serper API
        self.search_tool = GoogleSerperAPIWrapper(api_key=st.secrets["SERPER_API_KEY"])

    def process_response(self, query: str, raw_response: str) -> str:
        """
        Extract precise answers from Serper output for common query types:
        - Time/Date in India
        - Gold rates
        """
        if not raw_response:
            return "⚠️ No results found."

        query_lower = query.lower()

        # -------------------
        # Handle Time Queries
        # -------------------
        if "time in india" in query_lower or "current time in india" in query_lower:
            time_match = re.search(r'(\d{1,2}:\d{2}\s?(AM|PM|IST)?)', raw_response, re.IGNORECASE)
            if time_match:
                return f"The current time in India is {time_match.group(1)} IST."

        # -------------------
        # Handle Date Queries
        # -------------------
        if "date in india" in query_lower or "today's date" in query_lower:
            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},?\s\d{4}', raw_response)
            if date_match:
                return f"Today's date in India is {date_match.group(0)}."

        # -------------------
        # Handle Gold Rate Queries
        # -------------------
        if "gold rate" in query_lower or "price of gold" in query_lower:
            # Look for patterns like ₹11,488 per gram
            gold_match = re.findall(r'₹[\d,]+', raw_response)
            if gold_match:
                return f"The current gold rates in India are: {', '.join(gold_match[:3])}."

        # -------------------
        # Generic fallback
        # -------------------
        # Take first 2 sentences
        sentences = raw_response.split(". ")
        if len(sentences) > 2:
            return ". ".join(sentences[:2]) + "..."
        return raw_response

    @utils.enable_chat_history
    def main(self):
        user_query = st.chat_input(placeholder="Type your question here...")

        if user_query:
            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):
                placeholder = st.empty()

                # Typing animation
                for dots in ["", ".", "..", "..."]:
                    placeholder.markdown(
                        f"<span style='color:#666; font-size:16px;'>Searching{dots}</span>",
                        unsafe_allow_html=True
                    )
                    time.sleep(0.3)

                try:
                    # Directly call Serper API
                    raw_response = self.search_tool.run(user_query)
                    response = self.process_response(user_query, raw_response)

                except Exception as e:
                    response = f"⚠️ Search failed: {str(e)}"

                # Display the final response
                placeholder.markdown(
                    f"<span style='color:#1e7ebf; font-size:16px;'>{response}</span>",
                    unsafe_allow_html=True
                )

                # Save response to session state
                st.session_state.messages.append({"role": "assistant", "content": response})
                utils.print_qa(InternetChatbot, user_query, response)


if __name__ == "__main__":
    obj = InternetChatbot()
    obj.main()
