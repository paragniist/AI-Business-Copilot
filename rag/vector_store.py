import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def add_to_vector_db(pdf_path):
    """
    Rebuilds the entire vector DB from the data directory so that it 
    exactly mirrors the current files (removing old/deleted files).
    """
    data_dir = "data"
    
    # Use PyPDFDirectoryLoader to load all PDFs currently in the data directory
    loader = PyPDFDirectoryLoader(data_dir)
    docs = loader.load()

    # If the directory is empty or has no PDFs, remove the old index
    if not docs:
        if os.path.exists("faiss_index"):
            shutil.rmtree("faiss_index")
        print("No documents found. Vector DB cleared.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Completely overwrite the old DB to purge deleted files
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local("faiss_index")
    print("Vector DB completely rebuilt from data/ directory 🔥")