# hallucination/detector.py
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)


def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences


def check_sentence_support(sentence, chunks):
    context = "\n---\n".join([chunk['text'] for chunk in chunks])
    prompt = f"""You are a fact-checking assistant.
Your job is to check if the following statement is supported by the provided context.

Context from documents:
{context}

Statement to check:
{sentence}

Is this statement directly supported by the context above?
Answer with ONLY one word: YES or NO"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=10
    )
    answer = response.choices[0].message.content.strip().upper()
    return "YES" in answer


def detect_hallucination(ai_answer, chunks):
    print("\nRunning hallucination detection...")
    sentences = split_into_sentences(ai_answer)
    print(f"Checking {len(sentences)} sentences...")

    supported = []
    unsupported = []

    for i, sentence in enumerate(sentences):
        print(f"  Checking sentence {i+1}/{len(sentences)}...")
        is_supported = check_sentence_support(sentence, chunks)
        if is_supported:
            supported.append(sentence)
        else:
            unsupported.append(sentence)

    total = len(sentences)
    confidence_score = len(supported) / total if total > 0 else 0.0

    if confidence_score >= 0.9:
        verdict = "HIGH CONFIDENCE - Answer is well supported"
    elif confidence_score >= 0.7:
        verdict = "MEDIUM CONFIDENCE - Most claims supported"
    elif confidence_score >= 0.5:
        verdict = "LOW CONFIDENCE - Some claims unsupported"
    else:
        verdict = "VERY LOW CONFIDENCE - Answer may contain hallucinations"

    report = {
        "confidence_score": round(confidence_score, 4),
        "total_sentences": total,
        "supported_count": len(supported),
        "unsupported_count": len(unsupported),
        "supported_sentences": supported,
        "unsupported_sentences": unsupported,
        "verdict": verdict,
        "hallucination_detected": len(unsupported) > 0
    }

    print(f"Confidence score: {confidence_score:.2%}")
    print(f"Verdict: {verdict}")
    return report


def check_hallucination(ai_answer, chunks):
    """
    Alias called by the API.
    """
    return detect_hallucination(ai_answer, chunks)


if __name__ == "__main__":
    print("Hallucination Detector is ready!")