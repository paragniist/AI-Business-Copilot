import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def search_docs(query):
    if not os.path.exists("faiss_index"):
        return "No documents have been uploaded or indexed yet."

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    try:
        db = FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        results = db.similarity_search(query, k=4)

        combined = ""
        for doc in results:
            combined += doc.page_content + "\n\n"

        return combined
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return "Error loading document index."