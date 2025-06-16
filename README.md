# 🗺️ MapBench.Live

**Real-World Map Understanding Benchmark for Vision-Language Models**

[![Website](https://img.shields.io/badge/Website-Live-brightgreen)](https://jatorre.github.io/mapbench.live)
[![Dataset](https://img.shields.io/badge/Dataset-MapWise-blue)](https://github.com/map-wise/mapwise-dataset)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **🚀 Live Benchmark**: Visit [jatorre.github.io/mapbench.live](https://jatorre.github.io/mapbench.live) to explore the leaderboard and tasks!

## What is MapBench.Live?

MapBench.Live is the **first live, continuously updated benchmark** for evaluating vision-language models (VLMs) on real-world map interpretation tasks. Built upon the [MapWise dataset](https://github.com/map-wise/mapwise-dataset), this project transforms static evaluation into a dynamic, community-driven platform.

### 🎯 Why MapBench.Live?

**From Static to Live**: Traditional benchmarks are static snapshots. MapBench.Live evolves continuously with:
- 🔄 **Automatic evaluation** of new model submissions
- 📊 **Real-time leaderboard** updates
- 🌍 **Community contributions** of new map tasks
- 📈 **Transparent, reproducible** results

**Real-World Map Understanding**: Unlike synthetic datasets, we use actual maps that humans encounter daily:
- 🌦️ Weather forecasts and climate data
- 🗳️ Election results and political maps  
- 🏙️ Urban planning and zoning maps
- 🗺️ Choropleth visualizations with complex legends

## 📊 Current Status

| Metric | Value |
|--------|-------|
| **Maps** | 138 (98 USA + 40 counterfactuals) |
| **Questions** | 1,171 |
| **Question Types** | 5 (count, yes/no, single, range, list) |
| **Models Evaluated** | 4 (GPT-4o, Gemini variants) |
| **Live Site** | ✅ [mapbench.live](https://jatorre.github.io/mapbench.live) |

## 🏆 Current Leaderboard

| Rank | Model | Overall Score | Choropleth | Weather |
|------|-------|---------------|------------|---------|
| 🥇 | GPT-4o | **92.5%** | 93.2% | 91.8% |
| 🥈 | Gemini-2-Flash | **89.3%** | 90.1% | 88.5% |
| 🥉 | Gemini-1.5-Pro | **87.8%** | 88.5% | 87.1% |
| 4 | GPT-4o-Mini | **82.4%** | 83.1% | 81.7% |

*View the full leaderboard at [jatorre.github.io/mapbench.live](https://jatorre.github.io/mapbench.live)*

## 🚀 Quick Start

### 1. Submit Your Model

Add your model to the leaderboard by editing [`data/models.yaml`](data/models.yaml):

```yaml
- id: your-model-name
  provider: openai  # or vertexai
  endpoint: "openai:gpt-4o"
  auth: "env:YOUR_API_KEY"
  description: "Your model description"
```

**That's it!** GitHub Actions will automatically:
- Run the benchmark on all 138 maps
- Score the 1,171 questions
- Update the live leaderboard
- Deploy the results

### 2. Run Locally

```bash
# Clone and setup
git clone https://github.com/jatorre/mapbench.live.git
cd mapbench.live
pip install -r requirements.txt

# Run benchmark
export OPENAI_API_KEY="your-key"
python3 scripts/run_benchmark.py --models "gpt-4o-mini"

# View results
python3 scripts/generate_demo_results.py
```

### 3. Add New Tasks

```bash
# Add a new map task
python3 scripts/add_task.py \
  --id "weather-tokyo-2024" \
  --image "path/to/map.png" \
  --type "weather" \
  --questions "What's the temperature?|25°C|short_answer"
```

## 🏗️ Architecture

```
mapbench.live/
├── 🌐 app/                  # Next.js website (leaderboard, task explorer)
├── 🤖 benchmarks/           # Python evaluation pipeline
│   ├── runner.py           # Model execution (OpenAI, Vertex AI)
│   ├── scorer.py           # GPT-4o based scoring
│   └── evaluator.py        # End-to-end benchmark orchestration
├── 📊 data/
│   ├── tasks/              # 138 map images + JSON metadata
│   ├── models.yaml         # Model registry (edit to add models!)
│   └── results/            # Benchmark outputs & leaderboard
├── 🔧 scripts/             # CLI tools for running benchmarks
└── ⚙️ .github/workflows/   # Automated CI/CD
```

## 📖 Task Format

Each map task includes real-world questions with expected answers:

```json
{
  "id": "mapwise-usa-8808",
  "map_image": "mapwise-usa-8808.png",
  "context": "Choropleth map of USA population density",
  "type": "choropleth",
  "questions": [
    {
      "q": "Which state has the highest population density?",
      "a": "New Jersey",
      "type": "single_answer"
    },
    {
      "q": "How many states have density above 200 people/sq mi?",
      "a": "12",
      "type": "count"
    }
  ]
}
```

## 🔬 Based on MapWise Dataset

This project builds upon the excellent [MapWise dataset](https://github.com/map-wise/mapwise-dataset) by:

- **Importing** all USA choropleth maps and questions
- **Adding** counterfactual examples for robustness testing  
- **Creating** a live evaluation infrastructure
- **Enabling** continuous community contributions

*Citation*: If you use MapBench.Live, please cite both this project and the original MapWise paper.

## 🤝 Contributing

### Add Your Model
1. Fork this repository
2. Edit `data/models.yaml` with your model configuration
3. Create a pull request
4. Watch the automated benchmark run!

### Add New Tasks
1. Use `scripts/add_task.py` to create new map tasks
2. Submit a PR with your maps and questions
3. Help expand the benchmark diversity

### Development
```bash
# Backend development
pip install -r requirements.txt
python3 scripts/run_benchmark.py

# Frontend development  
cd app
npm install
npm run dev
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **MapWise Team** for the original dataset and research
- **OpenAI & Google** for model APIs
- **Community contributors** for expanding the benchmark

---

**🌟 Star this repository** to stay updated with the latest VLM map understanding benchmarks!

**🔗 Visit the live site**: [jatorre.github.io/mapbench.live](https://jatorre.github.io/mapbench.live)