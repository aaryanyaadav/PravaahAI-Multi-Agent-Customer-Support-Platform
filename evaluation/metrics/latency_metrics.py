import statistics
from typing import List, Dict, Any

def compute_latency_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes latency statistics (p50, p90, p99, mean, max) and token telemetry.
    """
    latencies = [r.get("duration_seconds", 0.0) for r in results if r.get("duration_seconds") is not None]
    tokens = [r.get("tokens_used", 0) for r in results if r.get("tokens_used") is not None]

    if not latencies:
        return {
            "p50_seconds": 0.0,
            "p90_seconds": 0.0,
            "p99_seconds": 0.0,
            "mean_seconds": 0.0,
            "total_tokens": 0,
            "avg_tokens_per_query": 0.0
        }

    latencies_sorted = sorted(latencies)
    n = len(latencies_sorted)

    p50 = latencies_sorted[int(n * 0.50)] if n > 0 else 0.0
    p90 = latencies_sorted[min(int(n * 0.90), n - 1)] if n > 0 else 0.0
    p99 = latencies_sorted[min(int(n * 0.99), n - 1)] if n > 0 else 0.0

    return {
        "p50_seconds": round(p50, 3),
        "p90_seconds": round(p90, 3),
        "p99_seconds": round(p99, 3),
        "mean_seconds": round(statistics.mean(latencies), 3),
        "min_seconds": round(min(latencies), 3),
        "max_seconds": round(max(latencies), 3),
        "total_tokens": sum(tokens),
        "avg_tokens_per_query": round(sum(tokens) / len(tokens), 1) if tokens else 0.0
    }
