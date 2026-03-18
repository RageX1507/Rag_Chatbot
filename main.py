from ingestion.loader import load_documents
from ingestion.splitter import split_documents
from ingestion.embedder import get_embeddings
from vectorstore.faiss_db import create_faiss_index

def build_indexes():
    nec_docs = load_documents("data/nec_docs")
    wattmonk_docs = load_documents("data/wattmonk_docs")

    nec_chunks = split_documents(nec_docs)
    watt_chunks = split_documents(wattmonk_docs)

    embedding = get_embeddings()

    nec_index = create_faiss_index(nec_chunks, embedding)
    watt_index = create_faiss_index(watt_chunks, embedding)

    return nec_index, watt_index