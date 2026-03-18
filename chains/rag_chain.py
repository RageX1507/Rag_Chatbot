from retriever.retriever import retrieve_docs
from llm.groq import call_llm
from router.intent import classify_query


def generate_rag_response(query, docs, source):

    # Build context safely
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""

    # Hybrid prompt (RAG + General)
    prompt = f"""
You are a helpful AI assistant.

Use the context if relevant.
Answer confidently and directly.

Do NOT say "based on context".
Do NOT be overly cautious.

Context:
{context[:1500]}

Question: {query}

Answer:
"""

    response = call_llm(prompt).strip()

    # Fallback (VERY IMPORTANT)
    if not response or len(response) < 5:
        response = call_llm(f"Answer clearly: {query}")

    # Confidence
    if docs:
        scores = [doc.metadata.get("score", 0.5) for doc in docs]
        confidence = round(min(1.0, sum(scores)/len(scores)), 2)
    else:
        confidence = 0.3

    return {
        "answer": response,
        "source": source if docs else "General Knowledge",
        "docs": docs,
        "confidence": confidence
    }


def handle_query(query, nec_index, wattmonk_index):

    # Handle greetings
    if query.lower().strip() in ["hi", "hello", "hey"]:
        return {
            "answer": "Hey 👋 How can I help you today?",
            "source": "",
            "docs": [],
            "confidence": 1.0
        }

    intent = classify_query(query)

    if intent == "general":
        response = call_llm(f"Answer clearly: {query}")
        return {
            "answer": response,
            "source": "General Knowledge",
            "docs": [],
            "confidence": 0.4
        }

    elif intent == "nec":
        docs = retrieve_docs(nec_index, query)
        return generate_rag_response(query, docs, "NEC")

    elif intent == "wattmonk":
        docs = retrieve_docs(wattmonk_index, query)
        return generate_rag_response(query, docs, "Wattmonk")

    else:
        response = call_llm(f"Answer clearly: {query}")
        return {
            "answer": response,
            "source": "General Knowledge",
            "docs": [],
            "confidence": 0.3
        }
def generate_suggestions(query):
    prompt = f"""
Generate 3 short follow-up questions for:
{query}
"""

    try:
        output = call_llm(prompt)
        suggestions = [q.strip("- ").strip() for q in output.split("\n") if q.strip()]
        return suggestions[:3]
    except:
        return []