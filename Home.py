import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Smart AI Chatbot Hub",
    page_icon='🤖',
    layout='wide'
)

# Main header with subtitle
st.markdown("""
<div style="text-align: center;">
    <h1 style="color:#1e7ebf;">Smart AI Chatbot Hub</h1>
    <p style="color:#555;">Explore interactive chatbots powered by Langchain and AI models. Try conversations, document queries, and more!</p>
</div>
""", unsafe_allow_html=True)

# Interactive links with logos
st.markdown("""
<div style="display:flex; justify-content:center; gap:30px; margin-bottom:25px;">
    <a href="https://github.com/Atharva0108/Chatbot-Langchain" target="_blank" 
       style="text-decoration:none; display:flex; align-items:center; gap:10px; 
              background-color:#24292f; color:white; padding:10px 20px; border-radius:8px; font-weight:bold; transition: transform 0.2s;">
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/github.svg" width="24px" height="24px">
        GitHub Repository
    </a>
    <a href="https://www.linkedin.com/in/atharva-chandak-b00a441b3" target="_blank" 
       style="text-decoration:none; display:flex; align-items:center; gap:10px; 
              background-color:#0A66C2; color:white; padding:10px 20px; border-radius:8px; font-weight:bold; transition: transform 0.2s;">
        <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/linkedin.svg" width="24px" height="24px">
        Atharva Chandak
    </a>
</div>

<style>
a:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# Introduction section with improved readability
st.markdown("""
<div style="background-color:#1e1e1e; color:#f5f5f5; padding:25px; border-radius:10px; line-height:1.8; font-size:16px;">
Langchain is a versatile framework that simplifies building AI-powered applications. With it, creating chatbots becomes easy and efficient.  

Here are some chatbot implementations you can explore:

- <strong>Basic Chatbot</strong>: Engage in natural conversations with AI.
- <strong>Chatbot with Internet Access</strong>: Stay up-to-date by asking about recent events.
- <strong>Chat with Your Documents</strong>: Get answers from your own files.
- <strong>Chat with SQL/MongoDB Database</strong>: Query your data using natural language.
- <strong>Chat with Websites</strong>: Interact with website content seamlessly.

Select a chatbot section to start exploring!
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; margin-top:30px; color:#888;">
Made by Atharva Chandak | Powered by Langchain & AI
</div>
""", unsafe_allow_html=True)
