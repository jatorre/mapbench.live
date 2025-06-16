#!/usr/bin/env python3
"""
Generate demo results for MapBench.Live
Creates a sample leaderboard for development
"""

import json
from datetime import datetime
from pathlib import Path

# Create demo leaderboard
leaderboard = [
    {
        "rank": 1,
        "model_id": "gpt-4o",
        "overall_score": 92.5,
        "total_questions": 1171,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-8808": 94.2,
        "score_choropleth": 93.2,
        "score_weather": 91.8,
        "score_counterfactual": 89.5
    },
    {
        "rank": 2,
        "model_id": "gemini-2-flash",
        "overall_score": 89.3,
        "total_questions": 1171,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-8808": 91.1,
        "score_choropleth": 90.1,
        "score_weather": 88.5,
        "score_counterfactual": 86.2
    },
    {
        "rank": 3,
        "model_id": "gemini-1-5-pro",
        "overall_score": 87.8,
        "total_questions": 1171,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-8808": 89.5,
        "score_choropleth": 88.5,
        "score_weather": 87.1,
        "score_counterfactual": 85.0
    },
    {
        "rank": 4,
        "model_id": "gpt-4o-mini",
        "overall_score": 82.4,
        "total_questions": 1171,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-8808": 84.0,
        "score_choropleth": 83.1,
        "score_weather": 81.7,
        "score_counterfactual": 80.2
    }
]

# Save leaderboard
results_dir = Path("data/results")
results_dir.mkdir(exist_ok=True)

leaderboard_file = results_dir / "leaderboard_latest.json"
with open(leaderboard_file, 'w') as f:
    json.dump(leaderboard, f, indent=2)

print(f"Demo leaderboard saved to {leaderboard_file}")