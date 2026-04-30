from rag.vector_store import create_vector_db
from rag.retriever import search_docs

pdf_file = "data/annual_report.pdf"

create_vector_db(pdf_file)

query = input("Ask question: ")

search_docs(query)