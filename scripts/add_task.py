#!/usr/bin/env python3
"""
MapBench.Live - Add Task Script
Helper script to add new tasks to the benchmark
"""

import argparse
import json
import sys
from pathlib import Path
import shutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="Add a new task to MapBench.Live"
    )
    
    parser.add_argument(
        "--id",
        type=str,
        required=True,
        help="Unique identifier for the task (e.g., 'weather-london-2024-07')"
    )
    
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to the map image file"
    )
    
    parser.add_argument(
        "--context",
        type=str,
        help="Optional context or title for the map"
    )
    
    parser.add_argument(
        "--type",
        type=str,
        choices=["weather", "election", "transit", "urban", "planning", "other"],
        default="other",
        help="Type of map task"
    )
    
    parser.add_argument(
        "--questions",
        type=str,
        nargs="+",
        help="Questions in format 'question|answer|type' (type is optional)"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Validate image exists
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file '{args.image}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Prepare task directory
    tasks_dir = Path("data/tasks")
    tasks_dir.mkdir(exist_ok=True)
    
    # Copy image to tasks directory
    image_filename = f"{args.id}{image_path.suffix}"
    target_image_path = tasks_dir / image_filename
    shutil.copy2(image_path, target_image_path)
    
    # Parse questions
    questions = []
    if args.questions:
        for q_str in args.questions:
            parts = q_str.split("|")
            if len(parts) < 2:
                print(f"Warning: Skipping invalid question format: {q_str}")
                continue
            
            question = {
                "q": parts[0].strip(),
                "a": parts[1].strip()
            }
            
            if len(parts) >= 3:
                question["type"] = parts[2].strip()
            else:
                question["type"] = "short_answer"
            
            questions.append(question)
    
    # Create task JSON
    task_data = {
        "id": args.id,
        "map_image": image_filename,
        "type": args.type,
        "questions": questions
    }
    
    if args.context:
        task_data["context"] = args.context
    
    # Save task JSON
    task_json_path = tasks_dir / f"{args.id}.json"
    with open(task_json_path, 'w') as f:
        json.dump(task_data, f, indent=2)
    
    print(f"Task '{args.id}' added successfully!")
    print(f"- Image: {target_image_path}")
    print(f"- Metadata: {task_json_path}")
    print(f"- Questions: {len(questions)}")


if __name__ == "__main__":
    main()