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
                 results_dir: str = "data/results",
                 use_cache: bool = True):
        self.runner = ModelRunner(models_config_path, use_cache=use_cache)
        # Pass OpenAI API key to scorer for consistent GPT-based evaluation
        import os
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.scorer = Scorer(api_key=openai_api_key)
        self.tasks_dir = Path(tasks_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def load_tasks(self, task_ids: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Task]:
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
        
        # Apply limit if specified
        if limit and len(tasks) > limit:
            import random
            random.shuffle(tasks)
            tasks = tasks[:limit]
        
        return tasks
    
    async def evaluate_model(self, model_id: str, tasks: List[Task], force_refresh: bool = False) -> Dict[str, Any]:
        """Evaluate a single model on all tasks"""
        all_scores = []
        all_results = []
        
        for task in tasks:
            # Run the model on the task
            eval_result = await self.runner.run_model(model_id, task, force_refresh=force_refresh)
            
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
                                 model_ids: Optional[List[str]] = None,
                                 task_ids: Optional[List[str]] = None,
                                 limit: Optional[int] = None,
                                 force_refresh: bool = False) -> Dict[str, Any]:
        """Evaluate all (or specified) models on all (or specified) tasks"""
        
        # Load tasks if not provided
        if tasks is None:
            tasks = self.load_tasks(task_ids=task_ids, limit=limit)
        
        # Get model IDs to evaluate
        if model_ids is None:
            model_ids = list(self.runner.models.keys())
        
        # Run evaluations in parallel
        evaluation_tasks = [
            self.evaluate_model(model_id, tasks, force_refresh=force_refresh) 
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
            
            # Calculate average timing and cost from detailed results
            detailed_results = result.get("detailed_results", [])
            total_time = 0
            total_cost = 0
            total_tokens = 0
            result_count = 0
            
            for detailed_result in detailed_results:
                if hasattr(detailed_result, 'execution_time') and detailed_result.execution_time:
                    total_time += detailed_result.execution_time
                    result_count += 1
                if hasattr(detailed_result, 'estimated_cost') and detailed_result.estimated_cost:
                    total_cost += detailed_result.estimated_cost
                if hasattr(detailed_result, 'input_tokens') and detailed_result.input_tokens:
                    total_tokens += detailed_result.input_tokens
                if hasattr(detailed_result, 'output_tokens') and detailed_result.output_tokens:
                    total_tokens += detailed_result.output_tokens
            
            avg_time = total_time / result_count if result_count > 0 else 0
            
            entry = {
                "rank": 0,  # Will be updated after sorting
                "model_id": model_id,
                "overall_score": round(scores["overall"] * 100, 2),
                "total_questions": scores.get("total_questions", 0),
                "last_updated": result["timestamp"],
                "avg_time_seconds": round(avg_time, 2),
                "total_cost_usd": round(total_cost, 4),
                "total_tokens": total_tokens
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
                       task_ids: Optional[List[str]] = None,
                       limit: Optional[int] = None,
                       use_cache: bool = True,
                       force_refresh: bool = False):
    """Main entry point for running benchmarks"""
    evaluator = Evaluator(use_cache=use_cache)
    
    print(f"Starting benchmark evaluation...")
    if model_ids:
        print(f"Models: {', '.join(model_ids)}")
    else:
        print("Models: All registered models")
    
    if task_ids:
        print(f"Tasks: {', '.join(task_ids)}")
    else:
        print("Tasks: All available tasks")
    
    # Cache settings info
    if use_cache:
        if force_refresh:
            print("Cache: Enabled (forcing refresh)")
        else:
            print("Cache: Enabled")
    else:
        print("Cache: Disabled")
    
    results = await evaluator.evaluate_all_models(
        model_ids=model_ids,
        task_ids=task_ids,
        limit=limit,
        force_refresh=force_refresh
    )
    
    print("\n=== LEADERBOARD ===")
    print(f"{'Rank':<4} {'Model':<20} {'Score':<8} {'Time(s)':<8} {'Cost($)':<10} {'Tokens':<8}")
    print("-" * 60)
    for entry in results["leaderboard"]:
        print(f"{entry['rank']:<4} {entry['model_id']:<20} {entry['overall_score']:<7.1f}% {entry.get('avg_time_seconds', 0):<7.1f}s ${entry.get('total_cost_usd', 0):<8.4f} {entry.get('total_tokens', 0):<8}")
    
    return results


if __name__ == "__main__":
    # Example: Run benchmark for specific models
    # asyncio.run(run_benchmark(model_ids=["gpt-4o", "gpt-4o-mini"]))
    pass