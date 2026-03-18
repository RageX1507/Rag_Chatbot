
def retrieve_docs(index, query, k=2):
    return index.similarity_search(query, k=k)