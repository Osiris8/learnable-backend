from flask_sqlalchemy import SQLAlchemy
import chromadb


db = SQLAlchemy()

chroma_client = chromadb.PersistentClient(path="./chroma_db")

def get_collection(chat_id: int):
    return chroma_client.get_or_create_collection(name=f"chat_{chat_id}")
