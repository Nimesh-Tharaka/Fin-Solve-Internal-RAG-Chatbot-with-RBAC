from app.retriever import retrieve_documents
from app.llm import generate_answer
from app.guardrails import check_guardrails


def ask_chatbot(question: str, role: str):
    guardrail_result = check_guardrails(question)

    if guardrail_result["blocked"]:
        return {
            "answer": guardrail_result["reason"],
            "sources": [],
            "status": "blocked"
        }

    docs = retrieve_documents(question, role)

    if not docs:
        return {
            "answer": "No authorized or relevant information found for your role.",
            "sources": [],
            "status": "no_access_or_no_match"
        }

    context = "\n\n".join([doc.page_content for doc in docs])
    sources = list({doc.metadata.get("source") for doc in docs})

    answer = generate_answer(question, context)

    return {
        "answer": answer,
        "sources": sources,
        "status": "success"
    }