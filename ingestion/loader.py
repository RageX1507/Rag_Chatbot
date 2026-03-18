from langchain_community.document_loaders import PyPDFLoader

def load_documents(folder_path):
    docs = []
    import os

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, file))
            loaded_docs = loader.load()

            for doc in loaded_docs:
                doc.metadata["source"] = file 

            docs.extend(loaded_docs)

    return docs