"""
inference.py — CLI entry point for judges.
Reads a JSON list of queries, runs the RAG pipeline, writes results to JSON.

Usage:
    python inference.py --input test.json --output results.json

Input format:
    [{"id": "q1", "query": "Portland cement manufacturer"}, ...]

Output format:
    [{"id": "q1", "retrieved_standards": ["IS 269", "IS 8112"], "latency_seconds": 1.2}, ...]
"""

import argparse
import json
import sys
import os
import time
import traceback

# Make sure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rag_pipeline import get_recommendations


def run_inference(input_path: str, output_path: str):
    print(f"\n{'='*60}")
    print(f"  BIS Standards Inference Runner")
    print(f"{'='*60}")
    print(f"  Input  : {input_path}")
    print(f"  Output : {output_path}")
    print(f"{'='*60}\n")

    # ── Load input ────────────────────────────────────────────────────────────
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            queries = json.load(f)
        if not isinstance(queries, list):
            queries = [queries]
        print(f"[INFO] Loaded {len(queries)} queries from {input_path}\n")
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in input file: {e}")
        sys.exit(1)

    # ── Process each query ────────────────────────────────────────────────────
    results = []
    for i, item in enumerate(queries, 1):
        qid   = item.get("id", f"q{i}")
        query = item.get("query", "")

        print(f"[{i}/{len(queries)}] ID={qid} | Query: {query[:80]}...")

        try:
            if not query.strip():
                raise ValueError("Empty query string")

            t0 = time.time()
            result = get_recommendations(query, top_k=5)
            latency = round(time.time() - t0, 3)

            # Extract IS codes from recommendations
            standards = [
                rec.get("standard_code", "Unknown")
                for rec in result.get("recommendations", [])
                if rec.get("standard_code", "Unknown") != "Unknown"
            ]

            results.append({
                "id": qid,
                "retrieved_standards": standards,
                "latency_seconds": result.get("latency_seconds", latency),
            })
            print(f"       ✓ Found {len(standards)} standards: {standards}")

        except Exception as e:
            # NEVER crash — log error and return empty result
            print(f"       ✗ Error: {e}")
            traceback.print_exc()
            results.append({
                "id": qid,
                "retrieved_standards": [],
                "latency_seconds": 0.0,
                "error": str(e),
            })

        print()

    # ── Write output ──────────────────────────────────────────────────────────
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"{'='*60}")
        print(f"  ✅ Results written to: {output_path}")
        print(f"  📊 Total queries processed: {len(results)}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write output: {e}")
        # Print to stdout as fallback
        print(json.dumps(results, indent=2))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="BIS Standards Inference Runner for Hackathon Judges"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input JSON file with queries",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/results.json",
        help="Path to output JSON file for results",
    )
    args = parser.parse_args()
    run_inference(args.input, args.output)


if __name__ == "__main__":
    main()
