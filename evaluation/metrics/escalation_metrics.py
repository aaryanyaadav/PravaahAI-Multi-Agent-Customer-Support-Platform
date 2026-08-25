from typing import List, Dict, Any

def compute_escalation_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes Escalation precision, recall, FPR, FNR, and Ticket creation accuracy.
    """
    total = len(results)
    if total == 0:
        return {"accuracy": 0.0, "ticket_accuracy": 0.0}

    correct_esc = sum(1 for r in results if r["escalation_passed"])
    overall_esc_accuracy = (correct_esc / total) * 100.0

    correct_tickets = sum(1 for r in results if r["ticket_passed"])
    ticket_accuracy = (correct_tickets / total) * 100.0

    tp = sum(1 for r in results if r["expected_escalation"] and r["actual_escalation"])
    fp = sum(1 for r in results if not r["expected_escalation"] and r["actual_escalation"])
    fn = sum(1 for r in results if r["expected_escalation"] and not r["actual_escalation"])
    tn = sum(1 for r in results if not r["expected_escalation"] and not r["actual_escalation"])

    precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 100.0
    recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 100.0
    fpr = (fp / (fp + tn)) * 100.0 if (fp + tn) > 0 else 0.0
    fnr = (fn / (fn + tp)) * 100.0 if (fn + tp) > 0 else 0.0

    # Conversational suppression rate (0 tickets created on smalltalk/gibberish)
    conv_items = [r for r in results if r.get("category") == "conversational"]
    conv_suppression_rate = 100.0
    if conv_items:
        suppressed_count = sum(1 for r in conv_items if r["actual_tickets"] == 0)
        conv_suppression_rate = (suppressed_count / len(conv_items)) * 100.0

    return {
        "escalation_accuracy": round(overall_esc_accuracy, 2),
        "ticket_creation_accuracy": round(ticket_accuracy, 2),
        "conversational_ticket_suppression_rate": round(conv_suppression_rate, 2),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "false_positive_rate": round(fpr, 2),
        "false_negative_rate": round(fnr, 2)
    }
