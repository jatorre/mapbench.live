🗺️ MapBench.Live — Real-World Map Understanding Benchmark for Vision-Language Models
📌 Overview
MapBench.Live is an open-source project that aims to become the definitive live benchmark for evaluating vision-language models (VLMs) on real-world map interpretation tasks. Unlike static datasets, MapBench.Live is continuously updated, community-driven, and aligned with how humans actually use maps—from reading weather charts to determining election outcomes.

The project provides:

A public-facing website with a leaderboard, interactive evaluation explorer, and task collections.

Automated benchmarking pipelines using OpenAI and Google Vertex AI.

Integration with GitHub Actions for continuous evaluation on new model entries.

A library of real map tasks (e.g. weather, election, transit, planning) and tools to expand it.

🎯 Goals
Measure real comprehension, not just visual grounding.

Provide ecologically valid tasks: real maps, real questions, human-intuitive prompts.

Enable repeatable, fair, and transparent evaluation.

Create a community space for sharing new tasks and results.

🧱 Architecture Overview
bash
Copy
Edit
.
├── app/                  # Frontend + backend logic (leaderboard, model runner)
├── data/
│   ├── tasks/            # Image maps + JSON metadata + prompts
│   └── models.yaml       # List of models with metadata & config
├── benchmarks/
│   ├── runner.py         # Executes evaluations (OpenAI, Vertex, etc.)
│   ├── scorer.py         # Grades model responses using GPT or rule-based scoring
│   └── evaluator.py      # Wraps task ↔ model ↔ score loop
├── .github/
│   └── workflows/        # GitHub Actions for triggering benchmarks
├── scripts/              # Helpers to add tasks, update results, visualize
└── README.md             # Project description and contributor guide
🌐 Components
1. Task Definitions
Each task includes:

map_image: The actual image (e.g. weather map, zoning plan)

context: Optional metadata or map title

questions: Natural language questions + expected answers

type: weather, election, urban, etc.

Example (YAML or JSON):

json
Copy
Edit
{
  "id": "weather-madrid-2024-06",
  "map_image": "weather_madrid_2024_06.png",
  "context": "Weather forecast for Madrid on June 12, 2024",
  "questions": [
    {
      "q": "What is the temperature expected in Madrid?",
      "a": "Around 30°C",
      "type": "short_answer"
    },
    {
      "q": "Is rain expected in the region?",
      "a": "Yes, in the northeast quadrant"
    }
  ]
}
2. Model Registry
A YAML or JSON config listing available models:

yaml
Copy
Edit
- id: gpt-4o
  provider: openai
  endpoint: "openai:gpt-4o"
  auth: "env:OPENAI_API_KEY"

- id: gemini-2p5-pro
  provider: vertexai
  model: "gemini-pro-vision"
  region: "us-central1"
Adding a new model to this file can trigger a benchmark run via GitHub Actions.

3. Evaluation Pipeline
Loads all tasks

Sends prompts + images to each model API

Scores results using GPT-4o or hard-coded keys

Outputs result JSON per model

Example output:

json
Copy
Edit
{
  "model": "gpt-4o",
  "task": "weather-madrid-2024-06",
  "score": 92,
  "answers": [...]
}
4. Frontend Website
Built with Next.js or Astro:

Live leaderboard

Browse tasks and answers

Submit new tasks or models

Documentation & community portal

5. GitHub Actions CI
On push to models.yaml or data/tasks/:

Runs benchmark for updated model(s)

Commits updated scores to data/results/

Deploys updated website

🔗 External Integrations
OpenAI API (GPT-4o)

Google Vertex AI (Gemini Pro Vision)

Future: Hugging Face endpoints, Claude, Ollama, fine-tuned open models

📌 Roadmap
 Define MVP task formats (weather, election, zoning)

 Script OpenAI + Vertex evaluation runners

 Create scoring logic using GPT-4o self-evaluator

 GitHub Action prototype

 Basic website frontend with task/results explorer

 Launch alpha benchmark run + open submissions