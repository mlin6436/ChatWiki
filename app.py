import dotenv
import os
import streamlit as st
import streamlit_chat as st_chat
import requests
import wikipedia
import time
from bs4 import BeautifulSoup
from datetime import datetime
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def search_wiki(topic):
    summary = wikipedia.summary(topic, sentences = 5)

    url = f"https://en.wikipedia.org/wiki/{topic}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find(id = "mw-content-text")
    p_set = content.find_all('p')
    content_text = ""
    for p in p_set:
        content_text += p.text

    return url, summary, content_text

def create_embeddings(content):
    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 2000,
        chunk_overlap = 200,
        length_function = len
    )
    chunks = text_splitter.split_text(content)
    embeddings = OpenAIEmbeddings(openai_api_key = openai_api_key)
    
    FAISS.from_texts(chunks, embeddings).save_local("./")
    return FAISS.load_local("./", embeddings)

def get_response(query, knowledge_base):
    docs = knowledge_base.similarity_search(query)
    search_context = query + "\n\n"
    for doc in docs:
        search_context += doc.page_content + "\n\n"
    messages.append(HumanMessage(content = search_context))
    response = chatOpenAI(messages).content
    messages.pop()
    messages.append(HumanMessage(content = query))
    messages.append(AIMessage(content = response))

    return response

chatOpenAI = ChatOpenAI(temperature = 0.7, openai_api_key = openai_api_key)
messages = [SystemMessage(content = "You are a Q&A bot and you will answer all the questions that the user has. Just say that you don't know, don't try to make up an answer.")]
topic = st.text_input("Enter a topic to prepare wiki content for Q&A")
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
# Improvement: deal with DisambiguationError when search "thing"
# Improvement: embeddings are re-generated every time user asked a question
# Improvement: limited memory
if topic:
    with st.spinner("Searching wiki..."):
        url, summary, content = search_wiki(topic)
    st.write("Wikipedia content loaded from: " + url)
    st.write("Summary: " + summary)
    knowledge_base = create_embeddings(content)
    
    query = st.text_input("Ask your question here:")
    response = ""
    if query:
        chat_history = st.session_state.chat_history
        chat_history.append({'user': 'user', 'time': datetime.now().strftime("%X"), 'text': query})
        response = get_response(query, knowledge_base)
        chat_history.append({'user': 'bot', 'time': datetime.now().strftime("%X"), 'text': response})
        st.session_state.chat_history = chat_history

        for message in st.session_state.chat_history:
            if message['user'] == 'user':
                st_chat.message(f"You ({message['time']}): {message['text']}", is_user=True, key=int(time.time_ns()))
            else:
                st_chat.message(f"ChatWiki ({message['time']}): {message['text']}", key=int(time.time_ns()))