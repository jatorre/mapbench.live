"""
MapBench.Live - Evaluator
Main evaluation orchestrator that wraps task ↔ model ↔ score loop
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

from .runner import ModelRunner, Task
from .scorer import Scorer


class Evaluator:
    def __init__(self, 
                 models_config_path: str = "data/models.yaml",
                 tasks_dir: str = "data/tasks",
                 results_dir: str = "data/results"):
        self.runner = ModelRunner(models_config_path)
        self.scorer = Scorer()
        self.tasks_dir = Path(tasks_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def load_tasks(self, task_ids: Optional[List[str]] = None) -> List[Task]:
        """Load tasks from the tasks directory"""
        tasks = []
        
        # Load all JSON task files
        task_files = list(self.tasks_dir.glob("*.json"))
        
        for task_file in task_files:
            with open(task_file, 'r') as f:
                task_data = json.load(f)
            
            # Skip if task_ids specified and this isn't in the list
            if task_ids and task_data['id'] not in task_ids:
                continue
            
            task = Task(
                id=task_data['id'],
                map_image=task_data['map_image'],
                context=task_data.get('context'),
                questions=task_data.get('questions', []),
                type=task_data.get('type')
            )
            tasks.append(task)
        
        return tasks
    
    async def evaluate_model(self, model_id: str, tasks: List[Task]) -> Dict[str, Any]:
        """Evaluate a single model on all tasks"""
        all_scores = []
        all_results = []
        
        for task in tasks:
            # Run the model on the task
            eval_result = await self.runner.run_model(model_id, task)
            
            if eval_result.error:
                print(f"Error evaluating {model_id} on {task.id}: {eval_result.error}")
                continue
            
            # Score the results
            scores = await self.scorer.score_evaluation_result(eval_result.__dict__)
            all_scores.extend(scores)
            all_results.append(eval_result)
        
        # Calculate aggregate scores
        aggregate = self.scorer.calculate_aggregate_score(all_scores)
        
        return {
            "model_id": model_id,
            "timestamp": datetime.utcnow().isoformat(),
            "aggregate_scores": aggregate,
            "detailed_results": all_results,
            "detailed_scores": all_scores
        }
    
    async def evaluate_all_models(self, 
                                 tasks: Optional[List[Task]] = None,
                                 model_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate all (or specified) models on all (or specified) tasks"""
        
        # Load tasks if not provided
        if tasks is None:
            tasks = self.load_tasks()
        
        # Get model IDs to evaluate
        if model_ids is None:
            model_ids = list(self.runner.models.keys())
        
        # Run evaluations in parallel
        evaluation_tasks = [
            self.evaluate_model(model_id, tasks) 
            for model_id in model_ids
        ]
        
        results = await asyncio.gather(*evaluation_tasks)
        
        # Create leaderboard
        leaderboard = self._create_leaderboard(results)
        
        # Save results
        self._save_evaluation_results(results, leaderboard)
        
        return {
            "leaderboard": leaderboard,
            "detailed_results": results,
            "evaluation_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "num_models": len(model_ids),
                "num_tasks": len(tasks),
                "task_ids": [t.id for t in tasks],
                "model_ids": model_ids
            }
        }
    
    def _create_leaderboard(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a leaderboard from evaluation results"""
        leaderboard = []
        
        for result in results:
            model_id = result["model_id"]
            scores = result["aggregate_scores"]
            
            entry = {
                "rank": 0,  # Will be updated after sorting
                "model_id": model_id,
                "overall_score": round(scores["overall"] * 100, 2),
                "total_questions": scores["total_questions"],
                "last_updated": result["timestamp"]
            }
            
            # Add per-task scores
            for task_id, score in scores.get("by_task", {}).items():
                entry[f"score_{task_id}"] = round(score * 100, 2)
            
            leaderboard.append(entry)
        
        # Sort by overall score (descending)
        leaderboard.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Assign ranks
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        return leaderboard
    
    def _save_evaluation_results(self, results: List[Dict[str, Any]], leaderboard: List[Dict[str, Any]]):
        """Save evaluation results and leaderboard"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        for result in results:
            model_id = result["model_id"]
            filename = f"eval_{model_id}_{timestamp}.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2, default=str)
        
        # Save leaderboard
        leaderboard_file = self.results_dir / f"leaderboard_{timestamp}.json"
        with open(leaderboard_file, 'w') as f:
            json.dump(leaderboard, f, indent=2)
        
        # Also save as latest leaderboard
        latest_leaderboard = self.results_dir / "leaderboard_latest.json"
        with open(latest_leaderboard, 'w') as f:
            json.dump(leaderboard, f, indent=2)
    
    def get_latest_leaderboard(self) -> Optional[Dict[str, Any]]:
        """Get the latest leaderboard"""
        latest_file = self.results_dir / "leaderboard_latest.json"
        if latest_file.exists():
            with open(latest_file, 'r') as f:
                return json.load(f)
        return None


async def run_benchmark(model_ids: Optional[List[str]] = None, 
                       task_ids: Optional[List[str]] = None):
    """Main entry point for running benchmarks"""
    evaluator = Evaluator()
    
    print(f"Starting benchmark evaluation...")
    if model_ids:
        print(f"Models: {', '.join(model_ids)}")
    else:
        print("Models: All registered models")
    
    if task_ids:
        print(f"Tasks: {', '.join(task_ids)}")
    else:
        print("Tasks: All available tasks")
    
    results = await evaluator.evaluate_all_models(
        model_ids=model_ids,
        tasks=evaluator.load_tasks(task_ids) if task_ids else None
    )
    
    print("\n=== LEADERBOARD ===")
    for entry in results["leaderboard"]:
        print(f"{entry['rank']}. {entry['model_id']}: {entry['overall_score']}%")
    
    return results


if __name__ == "__main__":
    # Example: Run benchmark for specific models
    # asyncio.run(run_benchmark(model_ids=["gpt-4o", "gpt-4o-mini"]))
    pass