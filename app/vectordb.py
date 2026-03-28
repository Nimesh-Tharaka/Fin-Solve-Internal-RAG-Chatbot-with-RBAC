from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.loaders import load_all_documents

CHROMA_DIR = "chroma_store"


def build_vector_db():
    raw_docs = load_all_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    docs = []
    for item in raw_docs:
        chunks = splitter.split_text(item["content"])
        for chunk in chunks:
            docs.append(
                Document(
                    page_content=chunk,
                    metadata=item["metadata"]
                )
            )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vectordb