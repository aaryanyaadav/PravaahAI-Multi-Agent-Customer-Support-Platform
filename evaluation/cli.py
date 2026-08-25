import argparse
import json
import os
import sys

# Ensure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from evaluation.datasets.generate_datasets import generate_benchmark_datasets
from evaluation.runners.batch_runner import BatchEvaluator
from evaluation.reports.generator import generate_evaluation_reports

def main():
    parser = argparse.ArgumentParser(
        description="Industry-Grade Evaluation Framework CLI for Customer Support Multi-Agent AI System."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Path to evaluation dataset JSON (defaults to evaluation/datasets/benchmark_100.json)."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of queries to evaluate."
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter evaluation to a specific category (e.g. crm, billing, ticket, knowledge, refund, escalation, conversational)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom directory to store run artifacts."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed execution traces."
    )

    args = parser.parse_args()

    # Determine dataset path
    dataset_file = args.dataset
    if not dataset_file:
        dataset_file = os.path.join(os.path.dirname(__file__), "datasets", "benchmark_100.json")

    # Generate dataset if it does not exist
    if not os.path.exists(dataset_file):
        print(f"Dataset not found at {dataset_file}. Auto-generating from database CSVs...")
        generate_benchmark_datasets(os.path.dirname(dataset_file))

    with open(dataset_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Execute batch evaluation
    evaluator = BatchEvaluator(verbose=args.verbose)
    results = evaluator.run_batch(dataset, limit=args.limit, category=args.category)

    # Generate reports and persist artifacts
    run_dir = generate_evaluation_reports(results, output_dir=args.output_dir)

    print("\n" + "="*65)
    print(f"EVALUATION RUN COMPLETE")
    print(f"Results saved to: {run_dir}")
    print(f"  - Summary KPIs:     {os.path.join(run_dir, 'summary_metrics.json')}")
    print(f"  - Per-Query Traces: {os.path.join(run_dir, 'raw_results.json')}")
    print(f"  - Executive Report: {os.path.join(run_dir, 'evaluation_report.md')}")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
