#!/usr/bin/env python3
"""
Generate demo results for MapBench.Live
Creates a sample leaderboard for development
"""

import json
from datetime import datetime
from pathlib import Path

# Create demo leaderboard with 4 tasks
leaderboard = [
    {
        "rank": 1,
        "model_id": "o3-test",
        "overall_score": 94.8,
        "total_questions": 12,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-49": 96.0,
        "score_cf-imaginary-map-20649": 94.5,
        "score_mapwise-usa-11349": 95.2,
        "score_mapwise-usa-3689": 93.5
    },
    {
        "rank": 2,
        "model_id": "gpt-4o",
        "overall_score": 92.5,
        "total_questions": 12,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-49": 94.2,
        "score_cf-imaginary-map-20649": 93.2,
        "score_mapwise-usa-11349": 91.8,
        "score_mapwise-usa-3689": 89.5
    },
    {
        "rank": 3,
        "model_id": "gemini-2-flash",
        "overall_score": 89.3,
        "total_questions": 12,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-49": 91.1,
        "score_cf-imaginary-map-20649": 90.1,
        "score_mapwise-usa-11349": 88.5,
        "score_mapwise-usa-3689": 86.2
    },
    {
        "rank": 4,
        "model_id": "gpt-4o-mini",
        "overall_score": 82.4,
        "total_questions": 12,
        "last_updated": datetime.utcnow().isoformat(),
        "score_mapwise-usa-49": 84.0,
        "score_cf-imaginary-map-20649": 83.1,
        "score_mapwise-usa-11349": 81.7,
        "score_mapwise-usa-3689": 80.2
    }
]

# Save leaderboard
results_dir = Path("data/results")
results_dir.mkdir(exist_ok=True)

leaderboard_file = results_dir / "leaderboard_latest.json"
with open(leaderboard_file, 'w') as f:
    json.dump(leaderboard, f, indent=2)

print(f"Demo leaderboard saved to {leaderboard_file}")