from groq import Groq
from dotenv import load_dotenv
import os
import time
from retriever import retrieve

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

print(f"Groq API key loaded: {api_key[:8]}...")

client = Groq(api_key=api_key)

def get_recommendations(query: str, top_k: int = 5) -> dict:
    start = time.time()
    
    # Step 1: Retrieve from FAISS
    results = retrieve(query, top_k=top_k)
    
    if not results:
        return {
            "query": query,
            "recommendations": [],
            "latency_seconds": round(time.time() - start, 2),
            "raw_results": []
        }
    
    # Step 2: Build context from retrieved chunks
    context = "\n\n".join([
        f"Standard: {r['standard_code']} - {r['standard_title']}\nContent: {r['content']}"
        for r in results
    ])
    
    # Step 3: Call Groq LLM
    prompt = f"""You are a BIS standards expert.

MANUFACTURER PRODUCT: {query}

BIS STANDARDS CONTEXT:
{context}

STRICT RULES:
- Only use standards from the context below
- Match standards SPECIFICALLY to this product: {query}
- Different products need different standards
- If product is unrelated to building materials, return empty recommendations array

Respond ONLY with this exact JSON format, no extra text:
{{
  "recommendations": [
    {{
      "standard_code": "IS 269",
      "standard_title": "Ordinary Portland Cement",
      "rationale": "Applies because...",
      "confidence": 90
    }}
  ]
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        
        import json
        raw = response.choices[0].message.content
        # Clean JSON from markdown if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        
        parsed = json.loads(raw)
        recs = parsed.get("recommendations", [])
        
    except Exception as e:
        print(f"[WARN] Groq API error: {e}")
        # Fallback to empty recommendations
        recs = []

    # Inject page numbers back into recommendations from retrieved results
    code_to_page = {r["standard_code"]: r["page_number"] for r in results}
    for rec in recs:
        code = rec.get("standard_code", "Unknown")
        rec["page_number"] = code_to_page.get(code, 0)
        try:
            rec["confidence"] = int(rec.get("confidence", 50))
        except (ValueError, TypeError):
            rec["confidence"] = 50

    latency = round(time.time() - start, 2)
    
    return {
        "query": query,
        "recommendations": recs,
        "latency_seconds": latency,
        "raw_results": results  # Return raw FAISS results for fallback
    }

if __name__ == "__main__":
    q = "I manufacture Portland cement for construction"
    import json
    print(json.dumps(get_recommendations(q), indent=2))
