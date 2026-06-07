# ai_layer/reasoning_engine.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)


def build_context_from_chunks(chunks):
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_part = f"""
Source {i+1}: {chunk['source_filename']}
Relevance Score: {chunk['hybrid_score']:.4f}
Content: {chunk['text']}
"""
        context_parts.append(context_part)
    return "\n---\n".join(context_parts)


def generate_answer(query, chunks, temperature=0.1):
    print(f"\nGenerating AI answer for: '{query}'")
    context = build_context_from_chunks(chunks)

    system_prompt = """You are ReguMind, an enterprise regulatory intelligence assistant.
Your job is to answer questions based ONLY on the document excerpts provided to you.
Rules you must follow:
1. Answer ONLY from the provided document excerpts
2. Always cite which source your answer comes from
3. If the answer is not in the provided excerpts, say exactly: "I cannot find this information in the provided documents."
4. Never make up information or use your general knowledge
5. Be precise and professional
6. At the end of your answer, list the sources you used"""

    user_prompt = f"""Document excerpts retrieved for your question:
{context}
Question: {query}
Please answer based only on the document excerpts above. Cite your sources."""

    print("Calling Groq Llama 3...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=1000
    )

    answer = response.choices[0].message.content

    result = {
        "query": query,
        "answer": answer,
        "sources_used": list(set([chunk['source_filename'] for chunk in chunks])),
        "chunks_retrieved": len(chunks),
        "model_used": "llama-3.3-70b-versatile"
    }
    print("Answer generated successfully!")
    return result


def get_answer(question, context_chunks, temperature=0.1):
    """
    Alias called by the API.
    Returns just the answer string.
    """
    if not context_chunks:
        return "No relevant documents were found to answer your question."
    result = generate_answer(question, context_chunks, temperature=temperature)
    return result["answer"]


def ask_regumind(query, chunks):
    """
    Original function kept for backward compatibility.
    """
    if not chunks:
        return {
            "query": query,
            "answer": "No relevant documents were found to answer your question.",
            "sources_used": [],
            "chunks_retrieved": 0,
            "model_used": "none"
        }
    return generate_answer(query, chunks)


if __name__ == "__main__":
    print("AI Reasoning Engine ready!")
    print("Using Groq with Llama 3 - Free tier!")