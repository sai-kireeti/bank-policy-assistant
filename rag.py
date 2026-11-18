"""Simple RAG search for the Bank Policy Assistant.

This file loads small policy text files, splits them into short chunks,
and finds the best chunk for a question. It uses TF-IDF scoring.
It needs no API key and no extra library. It runs with plain Python.

How RAG works in this project:
1. Load the policy files from the data folder.
2. Split each file into small chunks, one paragraph at a time.
3. For a question, score every chunk with TF-IDF and pick the best one.
4. Return that chunk as the answer, with its source file name.
"""

import math
import os
import re
import sys
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "when", "how",
    "can", "do", "does", "did", "i", "you", "he", "she", "it", "we", "they",
    "my", "your", "his", "her", "our", "their", "this", "that", "these",
    "those", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "or", "and", "if", "then", "should", "will", "be", "am", "me", "us",
}


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def load_chunks(data_dir=DATA_DIR):
    """Load every .txt file in data/ and split it into paragraph chunks."""
    chunks = []
    if not os.path.isdir(data_dir):
        return chunks
    for name in sorted(os.listdir(data_dir)):
        if not name.endswith(".txt"):
            continue
        path = os.path.join(data_dir, name)
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        # Split on blank lines. Each paragraph is one chunk.
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for para in paragraphs:
            # Skip the sample-data notice line, it is not policy content.
            if para.startswith("SAMPLE DATA"):
                continue
            # Skip short title lines such as "Card Payments Policy".
            # They match question words but hold no answer.
            if len(para.split()) < 8:
                continue
            chunks.append({"text": para, "source": name, "tokens": tokenize(para)})
    return chunks


class PolicySearch:
    def __init__(self, data_dir=DATA_DIR):
        self.chunks = load_chunks(data_dir)
        self.idf = self._build_idf()

    def _build_idf(self):
        total = len(self.chunks) or 1
        doc_freq = Counter()
        for chunk in self.chunks:
            for word in set(chunk["tokens"]):
                doc_freq[word] += 1
        idf = {}
        for word, freq in doc_freq.items():
            idf[word] = math.log((1 + total) / (1 + freq)) + 1.0
        return idf

    def _score(self, query_tokens, chunk_tokens):
        if not chunk_tokens:
            return 0.0
        counts = Counter(chunk_tokens)
        length = len(chunk_tokens)
        score = 0.0
        for word in query_tokens:
            if word in counts:
                tf = counts[word] / length
                score += tf * self.idf.get(word, 1.0)
        return score

    def ask(self, question):
        """Return the best answer chunk and its source for a question."""
        query_tokens = tokenize(question or "")
        if not query_tokens:
            return {
                "answer": "Please type a clear question about a banking policy.",
                "source": None,
                "score": 0.0,
            }
        best = None
        best_score = 0.0
        for chunk in self.chunks:
            score = self._score(query_tokens, chunk["tokens"])
            if score > best_score:
                best_score = score
                best = chunk
        if best is None or best_score == 0.0:
            return {
                "answer": "I could not find a clear answer in the sample policy files. Please try different words.",
                "source": None,
                "score": 0.0,
            }
        return {"answer": best["text"], "source": best["source"], "score": round(best_score, 4)}


# Optional LLM hook.
# The app runs fully without any LLM key, using the local search above.
# If you want a more natural answer, set one of these environment variables
# and write the call inside this function:
#   ANTHROPIC_API_KEY  for Claude
#   OPENAI_API_KEY     for OpenAI
# A safe pattern is: send the best chunk from PolicySearch.ask() plus the
# user question to the LLM, and ask it to answer only from that chunk.
# Do not send any real customer data to an LLM in a real project.
def build_llm_answer(question, context_chunk):
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    # LLM call is not enabled in this simple version.
    # Return None so the caller uses the local search answer.
    return None


_search = None


def ask(question):
    global _search
    if _search is None:
        _search = PolicySearch()
    result = _search.ask(question)
    llm_answer = build_llm_answer(question, result["answer"])
    if llm_answer:
        result["answer"] = llm_answer
    return result


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]).strip() or "What happens if a customer does not know a charge on the card?"
    result = ask(q)
    print(f"Question: {q}")
    print(f"Answer: {result['answer']}")
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']}")
