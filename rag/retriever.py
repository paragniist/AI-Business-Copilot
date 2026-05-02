from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def search_docs(query):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    ## Retreiver used to search the database for relevant documents based on the query
    results = db.similarity_search(query, k=3)

    combined = ""

    for doc in results:
        combined += doc.page_content + "\n\n"

    return combined