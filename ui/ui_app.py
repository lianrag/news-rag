import streamlit as st
import requests

st.set_page_config(page_title="Chat Tin Tức", layout="wide")
st.title("📰 Chat với Tin Tức từ URL (RAG + Gemini)")

user_id = st.text_input("Nhập tên hoặc ID của bạn:", value="user001")
date_filter = st.text_input("Lọc tin theo ngày (YYYY-MM-DD)", value="")

if "chat" not in st.session_state:
    st.session_state.chat = []

query = st.text_input("💬 Nhập câu hỏi...")

if st.button("Gửi") and query:
    res = requests.post("http://backend:8000/ask", json={
        "query": query,
        "user_id": user_id,
        "date_filter": date_filter or None
    }).json()

    st.session_state.chat.append(("Bạn", query))
    st.session_state.chat.append(("Gemini", res["answer"]))

for sender, msg in st.session_state.chat[::-1]:
    st.chat_message(sender).write(msg)
