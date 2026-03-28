from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.roles import ROLE_ACCESS

CHROMA_DIR = "chroma_store"


def get_retriever_for_role(role: str):
    allowed_departments = ROLE_ACCESS.get(role, [])

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    return vectordb, allowed_departments


def retrieve_documents(query: str, role: str, k: int = 4):
    vectordb, allowed_departments = get_retriever_for_role(role)

    results = vectordb.similarity_search(query, k=10)

    filtered = [
        doc for doc in results
        if doc.metadata.get("department") in allowed_departments
    ]

    return filtered[:k]