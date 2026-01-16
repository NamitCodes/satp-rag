from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
# This specifically requires the 'langchain' package
from langchain_classic.chains import RetrievalQA

load_dotenv()
app = FastAPI(title="SATP RAG Chat API")
# 1. Setup AIPipe Credentials
# Replace 'your-aipipe-token' with the token from https://aipipe.org/login
AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")
AIPIPE_BASE_URL = "https://aipipe.org/openai/v1"

# 2. Initialize AIPipe-backed LLM and Embeddings
# AIPipe acts as a proxy, so we point the base_url to their endpoint
llm = ChatOpenAI(
    model="gpt-4o-mini", 
    api_key=AIPIPE_TOKEN,
    base_url=AIPIPE_BASE_URL
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=AIPIPE_TOKEN,
    base_url=AIPIPE_BASE_URL
)

def build_rag():
    # 3. Load the satp-data.txt file
    if not os.path.exists("satp-data.txt"):
        print("Error: satp-data.txt not found.")
        return
        
    loader = TextLoader("satp-data.txt")
    documents = loader.load()

    # 4. Chunk the data
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # 5. Create Vector Store (Chroma)
    print("Creating vector store...")
    vectorstore = Chroma.from_documents(
        documents=texts, 
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    # 6. Setup Retrieval Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    
    return qa_chain

# Usage
if __name__ == "__main__":
    rag = build_rag()
    if rag:
        query = "What is the main summary of the SATP data?"
        response = rag.invoke(query)
        print(f"\nAI Response:\n{response['result']}")
