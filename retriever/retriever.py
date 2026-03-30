def retrieve_docs(index, query, k=4):

    print("Query:", query)

    results = index.similarity_search_with_score(
        query,
        k=k
    )

    docs = []

    for doc, score in results:

        # Convert distance → confidence score
        confidence_score = float(1 / (1 + score))

        doc.metadata["score"] = confidence_score

        docs.append(doc)

    print("Retrieved documents:", len(docs))

    return docs
