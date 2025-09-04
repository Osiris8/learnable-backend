import chromadb
import ollama
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def get_collection(chat_id: int):
    return chroma_client.get_or_create_collection(
        name=f"chat_{chat_id}",
        metadata={"dimension": 768})

def embed_text(text: str):
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]