import requests
from bs4 import BeautifulSoup
from datetime import datetime
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def load_url(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style"]): tag.decompose()
        text = soup.get_text(" ", strip=True)
        title = soup.title.string.strip() if soup.title else "No Title"
        return Document(
            page_content=text,
            metadata={
                "source": url,
                "title": title,
                "date": datetime.today().strftime("%Y-%m-%d")
            }
        )
    except Exception as e:
        print(f"❌ Failed to load {url}: {e}")
        return None

urls = [
    "https://dantri.com.vn/xa-hoi/chinh-thuc-bo-tu-hinh-voi-toi-tham-o-nhan-hoi-lo-20250625083927026.htm",
    "https://vnexpress.net/giam-an-cho-bi-cao-trong-vu-viet-a-4669429.html"
]

docs = filter(None, [load_url(u) for u in urls])
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(list(docs))

db = Chroma(persist_directory="vector_store", embedding_function=embedding)
db.add_documents(chunks)
db.persist()
print("✅ Vector store updated.")
