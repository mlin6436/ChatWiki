import dotenv
import os
import streamlit as st
import requests
import wikipedia
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def search_wiki(topic):
    # get page summary
    summary = wikipedia.summary(topic, sentences = 5)

    # scrap page content
    url = f"https://en.wikipedia.org/wiki/{topic}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find(id = "mw-content-text")
    p_set = content.find_all('p')
    content_text = ""
    for p in p_set:
        content_text += p.text

    return content_text, summary

def create_prompt():
    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

topic = st.text_input("Enter a topic to search wiki")

# Bug: deal with DisambiguationError when search "thing"
if topic:
    with st.spinner("Searching wiki..."):
        content, summary = search_wiki(topic)
    st.success("Finished searching.")
    st.write(summary)

    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 2000,
        chunk_overlap = 200,
        length_function = len
    )
    chunks = text_splitter.split_text(content)
    embeddings = OpenAIEmbeddings(openai_api_key = openai_api_key)
    knowledge_base = FAISS.from_texts(chunks, embeddings)
    
    query = st.text_input("Your question:")
    response = ""
    if query:
        with st.spinner("Running query..."):
            docs = knowledge_base.similarity_search(query)
            
            llm = OpenAI(openai_api_key = openai_api_key, temperature = 0.7)
            chain = load_qa_chain(llm, chain_type = "stuff", prompt = create_prompt())
            response = chain.run(input_documents = docs, question = query)

        st.success("Completed query.")
        st.write("Answer: ", response)