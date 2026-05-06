import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def search_docs(query):
    if not os.path.exists("faiss_index"):
        return {"text": "No documents have been uploaded or indexed yet.", "chunks": []}

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    try:
        db = FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        results = db.similarity_search(query, k=6)

        combined = ""
        chunks = []
        for doc in results:
            # PyPDFDirectoryLoader puts the file path in 'source' metadata
            source_path = doc.metadata.get("source", "Unknown Document")
            file_name = os.path.basename(source_path)
            # Clean the text: remove newlines, tabs, and excess whitespace
            clean_content = " ".join(doc.page_content.split())
            
            combined += f"FILE: {file_name}\nCONTENT: {clean_content}\n\n"
            chunks.append({
                "file": file_name,
                "excerpt": clean_content
            })

        return {"text": combined, "chunks": chunks}
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return {"text": "Error loading document index.", "chunks": []}