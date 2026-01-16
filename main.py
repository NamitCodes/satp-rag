from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
# Note: Use 'langchain.chains' unless your specific environment requires 'langchain_classic'
load_dotenv()
try:
    from langchain.chains import RetrievalQA
except ImportError:
    from langchain_classic.chains import RetrievalQA

app = FastAPI(title="SATP RAG API")

# 1. Configuration (AIPipe)
# Paste your token from https://aipipe.org/login
AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")
AIPIPE_BASE_URL = "https://aipipe.org/openai/v1"

# Global variable for the chain
qa_chain = None

class ChatRequest(BaseModel):
    message: str

@app.on_event("startup")
async def startup_event():
    """Load the existing vector database when the server starts."""
    global qa_chain
    
    # Initialize AIPipe Embeddings (must match the model used to create chroma_db)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=AIPIPE_TOKEN,
        base_url=AIPIPE_BASE_URL
    )

    # 2. LOAD the existing Vector Store from disk
    if not os.path.exists("./chroma_db"):
        print("ERROR: ./chroma_db directory not found! Ensure your database is in this folder.")
        return

    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    # 3. Initialize AIPipe Chat Model
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        api_key=AIPIPE_TOKEN,
        base_url=AIPIPE_BASE_URL
    )

    # 4. Create the Retrieval Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10})
    )
    print("✅ RAG System: Existing Chroma DB loaded and ready.")

@app.post("/chat")
async def chat(request: ChatRequest):
    if qa_chain is None:
        raise HTTPException(status_code=503, detail="RAG system is not initialized.")
    
    try:
        # Run the RAG query
        response = qa_chain.invoke(request.message)
        return {"answer": response["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)