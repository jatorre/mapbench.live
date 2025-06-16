"""
MapBench.Live - Model Runner
Executes evaluations against OpenAI, Vertex AI, and other providers
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import yaml
import base64
from dataclasses import dataclass, asdict


@dataclass
class ModelConfig:
    id: str
    provider: str
    endpoint: str = None
    model: str = None
    region: str = None
    auth: str = None
    description: str = None


@dataclass
class Task:
    id: str
    map_image: str
    context: str = None
    questions: List[Dict[str, str]] = None
    type: str = None


@dataclass
class EvaluationResult:
    model_id: str
    task_id: str
    timestamp: str
    answers: List[Dict[str, Any]]
    raw_response: str = None
    error: str = None


class ModelRunner:
    def __init__(self, models_config_path: str = "data/models.yaml"):
        self.models_config_path = models_config_path
        self.models = self._load_models()
    
    def _load_models(self) -> Dict[str, ModelConfig]:
        """Load model configurations from YAML file"""
        with open(self.models_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        models = {}
        for model_data in config['models']:
            model = ModelConfig(**model_data)
            models[model.id] = model
        
        return models
    
    async def run_model(self, model_id: str, task: Task) -> EvaluationResult:
        """Run a single model on a single task"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found in registry")
        
        model = self.models[model_id]
        
        try:
            if model.provider == "openai":
                result = await self._run_openai(model, task)
            elif model.provider == "vertexai":
                result = await self._run_vertexai(model, task)
            else:
                raise NotImplementedError(f"Provider {model.provider} not implemented")
            
            return EvaluationResult(
                model_id=model_id,
                task_id=task.id,
                timestamp=datetime.utcnow().isoformat(),
                answers=result['answers'],
                raw_response=result.get('raw_response')
            )
        
        except Exception as e:
            return EvaluationResult(
                model_id=model_id,
                task_id=task.id,
                timestamp=datetime.utcnow().isoformat(),
                answers=[],
                error=str(e)
            )
    
    async def _run_openai(self, model: ModelConfig, task: Task) -> Dict[str, Any]:
        """Run evaluation using OpenAI API"""
        import openai
        
        # Get API key from environment
        api_key = None
        if model.auth and model.auth.startswith("env:"):
            env_var = model.auth.split(":", 1)[1]
            api_key = os.getenv(env_var)
        
        if not api_key:
            raise ValueError(f"API key not found for {model.id}")
        
        client = openai.AsyncOpenAI(api_key=api_key)
        
        # Prepare the prompt
        messages = [
            {
                "role": "system",
                "content": "You are a map interpretation assistant. Answer questions about the provided map image accurately and concisely."
            }
        ]
        
        # Add context if available
        if task.context:
            messages.append({
                "role": "user",
                "content": f"Context: {task.context}"
            })
        
        # Load and encode the image
        image_path = Path("data/tasks") / task.map_image
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Add image to the conversation
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                }
            ]
        })
        
        # Process each question
        answers = []
        for question in task.questions:
            messages.append({
                "role": "user",
                "content": question['q']
            })
            
            response = await client.chat.completions.create(
                model=model.endpoint.split(":", 1)[1],
                messages=messages,
                max_tokens=500,
                temperature=0.0
            )
            
            answer_text = response.choices[0].message.content
            messages.append({
                "role": "assistant",
                "content": answer_text
            })
            
            answers.append({
                "question": question['q'],
                "expected": question.get('a', ''),
                "model_answer": answer_text,
                "type": question.get('type', 'short_answer')
            })
        
        return {
            "answers": answers,
            "raw_response": json.dumps([msg for msg in messages if msg['role'] == 'assistant'])
        }
    
    async def _run_vertexai(self, model: ModelConfig, task: Task) -> Dict[str, Any]:
        """Run evaluation using Vertex AI"""
        # This would require vertexai SDK setup
        # Placeholder for now
        raise NotImplementedError("Vertex AI integration pending")
    
    async def run_all_models(self, task: Task) -> List[EvaluationResult]:
        """Run all registered models on a single task"""
        tasks = [self.run_model(model_id, task) for model_id in self.models.keys()]
        return await asyncio.gather(*tasks)
    
    def save_results(self, results: List[EvaluationResult], output_dir: str = "data/results"):
        """Save evaluation results to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        for result in results:
            filename = f"{result.model_id}_{result.task_id}_{timestamp}.json"
            filepath = output_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(asdict(result), f, indent=2)


if __name__ == "__main__":
    # Example usage
    runner = ModelRunner()
    
    # Example task
    example_task = Task(
        id="weather-madrid-2024-06",
        map_image="weather_madrid_2024_06.png",
        context="Weather forecast for Madrid on June 12, 2024",
        questions=[
            {
                "q": "What is the temperature expected in Madrid?",
                "a": "Around 30°C",
                "type": "short_answer"
            }
        ]
    )
    
    # Run async evaluation
    # asyncio.run(runner.run_model("gpt-4o", example_task))