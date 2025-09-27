# LangChain + Streamlit + Ollama Chatbot

A multi-use chatbot powered by **LangChain**, **Streamlit**, and **Ollama**.
Runs fully on local models — no OpenAI or Gemini API required.

---

## 🚀 Features

* **Basic Chatbot** – simple conversations with Ollama LLMs
* **Internet Access** – real-time search answers
* **Document Chat** – query your own files (PDF, text, etc.)
* **SQL Chat** – talk to databases in natural language
* **Website Chat** – interact with live website content
* **MongoDB Support** – store/retrieve knowledge and chats

---

## 🖥 Run Locally

Make sure [Ollama](https://ollama.ai) is installed and a model pulled (e.g., `llama2`, `mistral`).

```bash
# Start app
streamlit run Home.py
```

---

## 📦 Docker

```bash
docker build -t langchain-chatbot .
docker run -p 8501:8501 langchain-chatbot
```

---

## 🔧 Requirements

* Python 3.9+
* Streamlit, LangChain, Ollama
* MongoDB (optional)

```bash
pip install -r requirements.txt
```

---

## 👤 Author

Maintained by **Atharva Chandak**. Contributions welcome!
