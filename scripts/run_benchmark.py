#!/usr/bin/env python3
"""
MapBench.Live - Benchmark Runner Script
Command-line interface for running benchmarks
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.evaluator import run_benchmark


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run MapBench.Live benchmarks"
    )
    
    parser.add_argument(
        "--models",
        type=str,
        help="Comma-separated list of model IDs to benchmark (e.g., 'gpt-4o,gemini-2-flash')"
    )
    
    parser.add_argument(
        "--tasks",
        type=str,
        help="Comma-separated list of task IDs to run (e.g., 'weather-madrid-2024-06,election-us-2024')"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="data/results",
        help="Output directory for results (default: data/results)"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Parse model and task lists
    model_ids = None
    if args.models:
        model_ids = [m.strip() for m in args.models.split(",") if m.strip()]
    
    task_ids = None
    if args.tasks:
        task_ids = [t.strip() for t in args.tasks.split(",") if t.strip()]
    
    # Run the benchmark
    try:
        asyncio.run(run_benchmark(model_ids=model_ids, task_ids=task_ids))
        print("\nBenchmark completed successfully!")
    except Exception as e:
        print(f"\nError running benchmark: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()