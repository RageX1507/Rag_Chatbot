from langchain_community.vectorstores import FAISS

def create_faiss_index(docs, embedding):
    return FAISS.from_documents(docs, embedding)

def save_index(index, path):
    index.save_local(path)

def load_index(path, embedding):
    return FAISS.load_local(path, embedding, allow_dangerous_deserialization=True)