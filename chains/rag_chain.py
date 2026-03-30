from retriever.retriever import retrieve_docs
from llm.groq import call_llm
from router.intent import classify_query


def rewrite_query_with_history(query, history):

    if not history:
        return query


    recent_history = history[-2:]

    history_text = "\n".join(
        [
            f"{role}: {msg}"
            for role, msg in recent_history
            if role == "user"
        ]
    )

    prompt = f"""
You are an assistant that rewrites follow-up questions.

Conversation:
{history_text}

Current Question:
{query}

Rewrite the question so it is fully self-contained.

Only return the rewritten question.
Do not explain.
"""

    try:

        rewritten = call_llm(prompt)

        if rewritten:
            print("Rewritten Query:", rewritten)
            return rewritten

    except Exception:
        pass

    return query


def generate_rag_response(query, docs, source):

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    ) if docs else ""

    prompt = f"""
You are a professional technical assistant.

Rules:

1) Use provided information when relevant
2) If information is insufficient, answer using knowledge
3) Be concise and confident
4) Never mention the word "context"
5) Prefer bullet points when helpful

Information:
{context[:1500]}

Question:
{query}

Answer:
"""

    response = call_llm(prompt).strip()

    
    if not response or len(response) < 5:

        response = call_llm(
            f"Answer clearly and directly: {query}"
        )


    if docs:

        scores = [
            doc.metadata.get("score", 0.5)
            for doc in docs
        ]

        confidence = round(
            min(1.0, sum(scores) / len(scores)),
            2
        )

    else:

        confidence = 0.3

    return {
        "answer": response,
        "source": source if docs else "General Knowledge",
        "docs": docs,
        "confidence": confidence
    }



def handle_query(
    query,
    nec_index,
    wattmonk_index,
    chat_history=None
):

    
    if query.lower().strip() in ["hi", "hello", "hey"]:

        return {
            "answer": "Hey 👋 How can I help you today?",
            "source": "",
            "docs": [],
            "confidence": 1.0
        }



    rewritten_query = rewrite_query_with_history(
        query,
        chat_history
    )

    intent = classify_query(rewritten_query)

    print("Detected intent:", intent)

    

    if intent == "general":

        response = call_llm(
            f"Answer clearly and directly: {rewritten_query}"
        )

        return {
            "answer": response,
            "source": "General Knowledge",
            "docs": [],
            "confidence": 0.4
        }


    elif intent == "nec":

        docs = retrieve_docs(
            nec_index,
            rewritten_query
        )

        return generate_rag_response(
            rewritten_query,
            docs,
            "NEC"
        )


    elif intent == "wattmonk":

        docs = retrieve_docs(
            wattmonk_index,
            rewritten_query
        )

        return generate_rag_response(
            rewritten_query,
            docs,
            "Wattmonk"
        )

    else:

        response = call_llm(
            f"Answer clearly and directly: {rewritten_query}"
        )

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

        suggestions = [
            q.strip("- ").strip()
            for q in output.split("\n")
            if q.strip()
        ]

        return suggestions[:3]

    except Exception:

        return []
