from retriever.retriever import retrieve_docs
from llm.groq import call_llm
from router.intent import classify_query


def rewrite_query_with_history(query, history):

    try:

        if not history:
            return query

        user_messages = [
            msg for role, msg in history
            if role == "user"
        ]

        if len(user_messages) < 2:
            return query

        previous_question = user_messages[-2]

        short_query_words = [
            "its",
            "it",
            "this",
            "that",
            "they",
            "those",
            "these",
            "guidelines",
            "requirements",
            "rules",
            "details"
        ]

        needs_rewrite = (
            len(query.split()) <= 5
            or query.lower() in short_query_words
        )

        if not needs_rewrite:
            return query

        prompt = f"""
Rewrite the follow-up question into a complete standalone question.

Previous question:
{previous_question}

Current question:
{query}

Resolve references like:

its
it
this
that
they
those
guidelines
requirements
rules

Example:

Previous: What is NEC?
Current: its guidelines
Rewrite: What are the NEC guidelines?

Return ONLY the rewritten question.
"""

        rewritten = call_llm(prompt).strip()

        if rewritten:

            print("Previous:", previous_question)
            print("Original:", query)
            print("Rewritten:", rewritten)

            return rewritten

    except Exception as e:

        print("Rewrite error:", e)

    return query


def generate_rag_response(query, docs, source):

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    ) if docs else ""

    prompt = f"""
You are a professional technical assistant.

Use provided information when relevant.
If information is insufficient, answer using knowledge.
Be concise and confident.

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

    print("Final Query Used:", rewritten_query)

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
Generate exactly 3 short follow-up questions.

Rules:

- Relevant
- Under 10 words
- No numbering
- No explanation

Topic:

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
