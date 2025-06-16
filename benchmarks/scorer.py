"""
MapBench.Live - Scorer
Grades model responses using GPT-4o or rule-based scoring
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import os
import openai


@dataclass
class ScoringResult:
    task_id: str
    model_id: str
    question: str
    expected_answer: str
    model_answer: str
    score: float
    explanation: str = None
    scoring_method: str = "gpt"


class Scorer:
    def __init__(self, scoring_model: str = "gpt-4o", api_key: Optional[str] = None):
        self.scoring_model = scoring_model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def score_answer(self, 
                          question: str, 
                          expected_answer: str, 
                          model_answer: str,
                          answer_type: str = "short_answer") -> ScoringResult:
        """Score a single answer using GPT-4o or rule-based methods"""
        
        # For certain answer types, use rule-based scoring
        if answer_type == "exact_match":
            score, explanation = self._score_exact_match(expected_answer, model_answer)
            return ScoringResult(
                task_id="",
                model_id="",
                question=question,
                expected_answer=expected_answer,
                model_answer=model_answer,
                score=score,
                explanation=explanation,
                scoring_method="rule_based"
            )
        
        # Default to GPT-based scoring
        if self.client:
            score, explanation = await self._score_with_gpt(
                question, expected_answer, model_answer
            )
            return ScoringResult(
                task_id="",
                model_id="",
                question=question,
                expected_answer=expected_answer,
                model_answer=model_answer,
                score=score,
                explanation=explanation,
                scoring_method="gpt"
            )
        else:
            # Fallback to simple similarity
            score, explanation = self._score_similarity(expected_answer, model_answer)
            return ScoringResult(
                task_id="",
                model_id="",
                question=question,
                expected_answer=expected_answer,
                model_answer=model_answer,
                score=score,
                explanation=explanation,
                scoring_method="similarity"
            )
    
    def _score_exact_match(self, expected: str, actual: str) -> tuple[float, str]:
        """Score based on exact match"""
        normalized_expected = expected.lower().strip()
        normalized_actual = actual.lower().strip()
        
        if normalized_expected == normalized_actual:
            return 1.0, "Exact match"
        else:
            return 0.0, f"No match: expected '{expected}', got '{actual}'"
    
    def _score_similarity(self, expected: str, actual: str) -> tuple[float, str]:
        """Simple word-based similarity scoring"""
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        if not expected_words:
            return 0.0, "No expected answer provided"
        
        overlap = expected_words.intersection(actual_words)
        score = len(overlap) / len(expected_words)
        
        explanation = f"Word overlap: {len(overlap)}/{len(expected_words)} words matched"
        return score, explanation
    
    async def _score_with_gpt(self, 
                             question: str, 
                             expected: str, 
                             actual: str) -> tuple[float, str]:
        """Use GPT-4o to score the answer"""
        
        prompt = f"""You are evaluating a model's answer to a map interpretation question.

Question: {question}
Expected Answer: {expected}
Model's Answer: {actual}

Score the model's answer on a scale from 0.0 to 1.0 based on:
1. Factual accuracy compared to the expected answer
2. Completeness of the response
3. Relevance to the question

Provide your response in JSON format:
{{
    "score": <float between 0.0 and 1.0>,
    "explanation": "<brief explanation of the score>"
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.scoring_model,
                messages=[
                    {"role": "system", "content": "You are a fair and accurate evaluator of map interpretation answers."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.0,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result["score"], result["explanation"]
        
        except Exception as e:
            return 0.0, f"Error in GPT scoring: {str(e)}"
    
    async def score_evaluation_result(self, eval_result: Dict[str, Any]) -> List[ScoringResult]:
        """Score all answers in an evaluation result"""
        scores = []
        
        for answer in eval_result.get("answers", []):
            scoring_result = await self.score_answer(
                question=answer["question"],
                expected_answer=answer["expected"],
                model_answer=answer["model_answer"],
                answer_type=answer.get("type", "short_answer")
            )
            
            # Update with task and model info
            scoring_result.task_id = eval_result["task_id"]
            scoring_result.model_id = eval_result["model_id"]
            
            scores.append(scoring_result)
        
        return scores
    
    def calculate_aggregate_score(self, scores: List[ScoringResult]) -> Dict[str, float]:
        """Calculate aggregate scores for a model"""
        if not scores:
            return {"overall": 0.0}
        
        # Overall average
        overall = sum(s.score for s in scores) / len(scores)
        
        # Group by task
        task_scores = {}
        for score in scores:
            if score.task_id not in task_scores:
                task_scores[score.task_id] = []
            task_scores[score.task_id].append(score.score)
        
        # Calculate per-task averages
        task_averages = {
            task_id: sum(scores) / len(scores)
            for task_id, scores in task_scores.items()
        }
        
        return {
            "overall": overall,
            "by_task": task_averages,
            "total_questions": len(scores)
        }


if __name__ == "__main__":
    # Example usage
    scorer = Scorer()
    
    # Example scoring
    async def test_scoring():
        result = await scorer.score_answer(
            question="What is the temperature in Madrid?",
            expected_answer="Around 30°C",
            model_answer="The temperature appears to be approximately 30 degrees Celsius"
        )
        print(f"Score: {result.score}")
        print(f"Explanation: {result.explanation}")
    
    # asyncio.run(test_scoring())