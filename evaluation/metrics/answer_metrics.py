from typing import List, Dict, Any

def compute_answer_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes answer keyword match accuracy, factual coverage, and grounding pass rate.
    """
    total = len(results)
    if total == 0:
        return {"accuracy": 0.0, "avg_keyword_coverage": 0.0}

    correct_answers = sum(1 for r in results if r["answer_passed"])
    overall_accuracy = (correct_answers / total) * 100.0

    coverage_scores = [r.get("keyword_coverage", 0.0) for r in results]
    avg_coverage = sum(coverage_scores) / total if total > 0 else 0.0

    grounding_passed = sum(1 for r in results if r.get("grounded", True))
    grounding_rate = (grounding_passed / total) * 100.0 if total > 0 else 0.0

    return {
        "accuracy": round(overall_accuracy, 2),
        "total_evaluated": total,
        "correct_answers": correct_answers,
        "avg_keyword_coverage": round(avg_coverage * 100.0, 2),
        "grounding_pass_rate": round(grounding_rate, 2)
    }
