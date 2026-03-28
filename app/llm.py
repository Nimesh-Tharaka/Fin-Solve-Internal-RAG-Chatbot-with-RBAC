import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer(question: str, context: str):
    system_prompt = """
You are an internal FinSolve assistant.

Rules:
1. Answer only from the provided context.
2. Do not make up facts.
3. If the answer is not clearly in the context, say you do not know.
4. Keep the answer professional and slightly detailed.
5. Summarize clearly in 2 to 5 sentences.
6. Do not mention information outside authorized context.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content