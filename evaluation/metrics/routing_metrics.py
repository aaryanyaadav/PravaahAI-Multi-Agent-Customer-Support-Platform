from typing import List, Dict, Any

def compute_routing_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes top-1 routing accuracy, per-agent precision, recall, F1, and confusion matrix.
    """
    total = len(results)
    if total == 0:
        return {"accuracy": 0.0, "total": 0}

    correct = sum(1 for r in results if r["routing_passed"])
    overall_accuracy = (correct / total) * 100.0

    # Collect all unique agents
    all_agents = sorted(list(set(
        [r["expected_agent"] for r in results] + [r["actual_primary_agent"] for r in results]
    )))

    # Build confusion matrix: conf_matrix[expected][actual]
    confusion_matrix = {exp: {act: 0 for act in all_agents} for exp in all_agents}
    for r in results:
        exp = r["expected_agent"]
        act = r["actual_primary_agent"]
        confusion_matrix[exp][act] += 1

    # Per-agent metrics
    per_agent = {}
    for agent in all_agents:
        tp = confusion_matrix[agent][agent]
        fp = sum(confusion_matrix[other][agent] for other in all_agents if other != agent)
        fn = sum(confusion_matrix[agent][other] for other in all_agents if other != agent)
        support = sum(confusion_matrix[agent].values())

        precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        per_agent[agent] = {
            "support": support,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1_score": round(f1, 2)
        }

    return {
        "accuracy": round(overall_accuracy, 2),
        "total_evaluated": total,
        "correct_routed": correct,
        "per_agent_metrics": per_agent,
        "confusion_matrix": confusion_matrix
    }
