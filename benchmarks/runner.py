"""
MapBench.Live - Model Runner
Executes evaluations against OpenAI, Vertex AI, and other providers
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
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
    execution_time: Optional[float] = None  # in seconds
    estimated_cost: Optional[float] = None  # in USD
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class ModelRunner:
    def __init__(self, models_config_path: str = "data/models.yaml", use_cache: bool = True):
        self.models_config_path = models_config_path
        self.models = self._load_models()
        self.use_cache = use_cache
        
        # Initialize cache system
        if self.use_cache:
            from .cache import BenchmarkCache
            self.cache = BenchmarkCache()
        else:
            self.cache = None
        
        # Pricing per 1M tokens (approximate, as of Dec 2024)
        self.pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4.1": {"input": 30.00, "output": 60.00},  # Estimated
            "o3": {"input": 100.00, "output": 200.00},      # Estimated
            "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        }
    
    def _load_models(self) -> Dict[str, ModelConfig]:
        """Load model configurations from YAML file"""
        with open(self.models_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        models = {}
        for model_data in config['models']:
            model = ModelConfig(**model_data)
            models[model.id] = model
        
        return models
    
    def _estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on token usage"""
        # Extract base model name for pricing lookup
        base_model = model_name.lower()
        if "gpt-4o-mini" in base_model:
            pricing_key = "gpt-4o-mini"
        elif "gpt-4o" in base_model:
            pricing_key = "gpt-4o"
        elif "gpt-4.1" in base_model:
            pricing_key = "gpt-4.1"
        elif "o3" in base_model:
            pricing_key = "o3"
        elif "gemini-2.5-pro" in base_model:
            pricing_key = "gemini-2.5-pro"
        elif "gemini-2.5-flash" in base_model:
            pricing_key = "gemini-2.5-flash"
        elif "gemini-1.5-pro" in base_model:
            pricing_key = "gemini-1.5-pro"
        elif "gemini-1.5-flash" in base_model:
            pricing_key = "gemini-1.5-flash"
        else:
            return 0.0  # Unknown model
        
        if pricing_key not in self.pricing:
            return 0.0
        
        pricing = self.pricing[pricing_key]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def _parse_batched_response(self, batched_response: str, questions: List[Dict]) -> List[Dict]:
        """Parse a batched response back into individual answers"""
        import re
        
        answers = []
        
        # Try multiple parsing strategies
        
        # Strategy 1: Look for numbered patterns (1., 2., 3., etc.)
        pattern = r'^\s*(\d+)[\.\:\)]\s*(.+?)(?=^\s*\d+[\.\:\)]|\Z)'
        matches = re.findall(pattern, batched_response, flags=re.MULTILINE | re.DOTALL)
        
        if matches and len(matches) >= len(questions):
            # Successfully parsed numbered answers
            for i, question in enumerate(questions):
                answer_text = ""
                # Find matching numbered answer
                for num_str, ans_text in matches:
                    if int(num_str) - 1 == i:  # Convert to 0-based
                        answer_text = ans_text.strip()
                        break
                
                answers.append({
                    "question": question['q'],
                    "expected": question.get('a', ''),
                    "model_answer": answer_text,
                    "type": question.get('type', 'short_answer')
                })
        else:
            # Strategy 2: Fallback - split by lines and try to map sequentially
            lines = [line.strip() for line in batched_response.split('\n') if line.strip()]
            
            # Filter out obvious header/intro lines
            answer_lines = []
            for line in lines:
                if not re.match(r'^(here are|based on|the map|these are)', line.lower()):
                    answer_lines.append(line)
            
            # Map answers to questions sequentially
            for i, question in enumerate(questions):
                answer_text = ""
                if i < len(answer_lines):
                    # Remove number prefix if it exists
                    answer_text = re.sub(r'^\s*\d+[\.\:\)]\s*', '', answer_lines[i])
                
                answers.append({
                    "question": question['q'],
                    "expected": question.get('a', ''),
                    "model_answer": answer_text,
                    "type": question.get('type', 'short_answer')
                })
        
        return answers
    
    async def run_model(self, model_id: str, task: Task, force_refresh: bool = False) -> EvaluationResult:
        """Run a single model on a single task with caching support"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found in registry")
        
        model = self.models[model_id]
        
        # Check cache first (unless force_refresh is True)
        if self.use_cache and not force_refresh and self.cache:
            cached_result = self.cache.get_cached_result(model, task)
            if cached_result:
                print(f"📁 Using cached result for {model_id} on {task.id}")
                return cached_result
        
        # Cache miss or force refresh - run the evaluation
        print(f"🚀 Running {model_id} on {task.id}")
        start_time = time.time()
        
        try:
            if model.provider == "openai":
                result = await self._run_openai(model, task)
            elif model.provider == "vertexai":
                result = await self._run_vertexai(model, task)
            else:
                raise NotImplementedError(f"Provider {model.provider} not implemented")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Extract token usage and cost from result
            input_tokens = result.get('input_tokens', 0)
            output_tokens = result.get('output_tokens', 0)
            estimated_cost = self._estimate_cost(model_id, input_tokens, output_tokens)
            
            evaluation_result = EvaluationResult(
                model_id=model_id,
                task_id=task.id,
                timestamp=datetime.utcnow().isoformat(),
                answers=result['answers'],
                raw_response=result.get('raw_response'),
                execution_time=execution_time,
                estimated_cost=estimated_cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            # Cache the result (only if successful)
            if self.use_cache and self.cache and not evaluation_result.error:
                self.cache.cache_result(model, task, evaluation_result)
            
            return evaluation_result
        
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            return EvaluationResult(
                model_id=model_id,
                task_id=task.id,
                timestamp=datetime.utcnow().isoformat(),
                answers=[],
                error=str(e),
                execution_time=execution_time
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
        
        # Batch all questions into a single request for efficiency
        batched_prompt = "Please answer each of the following questions about the map image. Provide clear, concise answers and number your responses (1, 2, 3, etc.):\n\n"
        
        for i, question in enumerate(task.questions, 1):
            batched_prompt += f"{i}. {question['q']}\n"
        
        messages.append({
            "role": "user", 
            "content": batched_prompt
        })
        
        model_name = model.endpoint.split(":", 1)[1]
        
        # Use max_completion_tokens for o3 models, max_tokens for others
        # o3 models also don't support temperature=0.0, only default (1)
        if model_name.startswith("o3"):
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_completion_tokens=1500  # Increased for batched response
            )
        else:
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=1500,  # Increased for batched response
                temperature=0.0
            )
        
        # Track token usage
        total_input_tokens = 0
        total_output_tokens = 0
        if hasattr(response, 'usage') and response.usage:
            total_input_tokens = response.usage.prompt_tokens
            total_output_tokens = response.usage.completion_tokens
        
        # Parse the batched response back into individual answers
        batched_response = response.choices[0].message.content
        answers = self._parse_batched_response(batched_response, task.questions)
        
        return {
            "answers": answers,
            "raw_response": json.dumps([msg for msg in messages if msg['role'] == 'assistant']),
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens
        }
    
    async def _run_vertexai(self, model: ModelConfig, task: Task) -> Dict[str, Any]:
        """Run evaluation using Vertex AI"""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel, Part
        except ImportError:
            raise NotImplementedError("Vertex AI SDK not installed. Run: pip install google-cloud-aiplatform")
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
        
        vertexai.init(project=project_id, location=model.region or "us-central1")
        
        # Create the model
        gemini_model = GenerativeModel(model.model)
        
        # Load and encode the image
        image_path = Path("data/tasks") / task.map_image
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Prepare the conversation
        messages = []
        
        # Add context if available
        if task.context:
            messages.append(f"Context: {task.context}")
        
        # Add image
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
        
        image_part = Part.from_data(mime_type="image/png", data=image_data)
        
        # Batch all questions into a single request for efficiency
        batched_prompt = "You are a map interpretation assistant. Please answer each of the following questions about the map image. Provide clear, concise answers and number your responses (1, 2, 3, etc.):\n\n"
        
        for i, question in enumerate(task.questions, 1):
            batched_prompt += f"{i}. {question['q']}\n"
        
        # Generate response
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: gemini_model.generate_content([image_part, batched_prompt])
        )
        
        # Track token usage (Gemini provides usage metadata)
        total_input_tokens = 0
        total_output_tokens = 0
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            total_input_tokens = response.usage_metadata.prompt_token_count
            total_output_tokens = response.usage_metadata.candidates_token_count
        
        # Parse the batched response back into individual answers
        batched_response = response.text if response.text else ""
        answers = self._parse_batched_response(batched_response, task.questions)
        
        # Create conversation history for compatibility
        conversation_history = [f"Q: All {len(task.questions)} questions asked in batch", f"A: {batched_response}"]
        
        return {
            "answers": answers,
            "raw_response": json.dumps(conversation_history),
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens
        }
    
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