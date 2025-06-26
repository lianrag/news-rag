from fastapi import FastAPI
from pydantic import BaseModel
import json, os
from datetime import datetime
from langchain_community.chat_models import ChatGoogleGenerativeAI
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.embeddings import GoogleGenerativeAIEmbeddings

app = FastAPI()

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
db = Chroma(persist_directory="vector_store", embedding_function=embedding)

history_file = "history_store.json"
if not os.path.exists(history_file):
    with open(history_file, "w") as f:
        json.dump({}, f)

class QueryRequest(BaseModel):
    query: str
    user_id: str
    date_filter: str = None

@app.post("/ask")
def ask_question(data: QueryRequest):
    retriever = db.as_retriever(search_kwargs={"k": 4})
    if data.date_filter:
        retriever.search_kwargs["filter"] = {"date": data.date_filter}

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    res = qa_chain(data.query)

    with open(history_file) as f:
        history = json.load(f)
    history.setdefault(data.user_id, []).append({
        "q": data.query,
        "a": res["result"],
        "time": str(datetime.now()),
    })
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    return {
        "answer": res["result"],
        "sources": [doc.metadata["source"] for doc in res["source_documents"]]
    }
