# ChatWiki

Talking with Wikipedia

## What is ChatWiki

ChatWiki is a simple Python application that utilises [embeddings](https://platform.openai.com/docs/guides/embeddings) and [langchain](https://github.com/hwchase17/langchain) to execute queries on Wikipedia content through ChatPGT.

## Why ChatWiki

Unless you have ChatGPT Plus subscription, the data used to train current version of ChatGPT is up until September 2021, it also doesn't have the ability to access internet. To unlock these limitations, this project is created to demo how to use embeddings to query live Wikipedia content.

## How to run the app

### Prerequisite

You have python3 installed or run the following command to install it.
```
brew install python@3.10
```

### Install dependencies

```
pip install -r requirements
```

### Retrieve your OpenAI API key

```
https://platform.openai.com/account/api-keys
```

### Insert OpenAI API key to `.env`

```
echo "OPENAI_API_KEY='your-api-key'" >> ~/.env
```

### Start the application

```
streamlit run app.py
```

![Screenshot](chatwiki-demo.png)