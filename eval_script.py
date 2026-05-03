"""
eval_script.py — Evaluation harness for the BIS RAG pipeline.
Runs a predefined set of test queries and scores the results.
Usage: python eval_script.py
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rag_pipeline import get_recommendations

# ── Test Queries ──────────────────────────────────────────────────────────────
TEST_QUERIES = [
    {
        "id": "q1",
        "query": "I manufacture Portland cement OPC 53 grade for structural construction.",
        "expected_codes": ["IS 269", "IS 8112", "IS 12269"],
    },
    {
        "id": "q2",
        "query": "We produce TMT steel reinforcement bars for building construction.",
        "expected_codes": ["IS 1786", "IS 432"],
    },
    {
        "id": "q3",
        "query": "Our company makes fly ash bricks and building blocks for masonry.",
        "expected_codes": ["IS 12894", "IS 3495"],
    },
    {
        "id": "q4",
        "query": "We supply ready-mix concrete for slabs, columns and beams.",
        "expected_codes": ["IS 456", "IS 4926"],
    },
    {
        "id": "q5",
        "query": "I produce coarse and fine aggregates for concrete mixing.",
        "expected_codes": ["IS 383"],
    },
]


def evaluate():
    print(f"\n{'='*65}")
    print(f"  BIS RAG Pipeline — Evaluation Report")
    print(f"{'='*65}\n")

    total_precision = 0.0
    results_log = []

    for item in TEST_QUERIES:
        qid      = item["id"]
        query    = item["query"]
        expected = [c.upper().replace(" ", "") for c in item["expected_codes"]]

        print(f"[{qid}] {query[:70]}...")
        t0 = time.time()
        result = get_recommendations(query, top_k=5)
        elapsed = time.time() - t0

        recs = result.get("recommendations", [])
        retrieved_codes = [r.get("standard_code", "").upper().replace(" ", "") for r in recs]

        # Precision: how many expected codes appear in retrieved
        hits = sum(
            1 for exp in expected
            if any(exp in ret or ret in exp for ret in retrieved_codes)
        )
        precision = hits / len(expected) if expected else 0.0
        total_precision += precision

        print(f"      Expected : {item['expected_codes']}")
        print(f"      Retrieved: {[r.get('standard_code') for r in recs]}")
        print(f"      Precision: {precision:.0%}  |  Latency: {elapsed:.2f}s\n")

        results_log.append({
            "id": qid,
            "query": query,
            "expected": item["expected_codes"],
            "retrieved": [r.get("standard_code") for r in recs],
            "precision": round(precision, 3),
            "latency_seconds": round(elapsed, 3),
        })

    avg_precision = total_precision / len(TEST_QUERIES)

    print(f"{'='*65}")
    print(f"  📊 Overall Mean Precision : {avg_precision:.1%}")
    print(f"  📝 Queries evaluated      : {len(TEST_QUERIES)}")
    print(f"{'='*65}\n")

    # Save results
    out_path = "data/eval_results.json"
    os.makedirs("data", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"mean_precision": round(avg_precision, 3), "results": results_log}, f, indent=2)
    print(f"  Results saved to: {out_path}\n")


if __name__ == "__main__":
    evaluate()
