# 🗺️ CARTO MERIT

**Map Evaluation and Reasoning Integrated Test**

[![Website](https://img.shields.io/badge/Website-Live-brightgreen)](https://jatorre.github.io/mapbench.live)
[![Dataset](https://img.shields.io/badge/Dataset-MapWise-blue)](https://github.com/map-wise/mapwise-dataset)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **🚀 Live Benchmark**: Visit [jatorre.github.io/mapbench.live](https://jatorre.github.io/mapbench.live) to explore the leaderboard and evaluation results!

## What is CARTO MERIT?

CARTO MERIT (**Map Evaluation and Reasoning Integrated Test**) is a comprehensive benchmark for evaluating vision-language models on real-world map understanding tasks. Built upon the [MapWise dataset](https://github.com/map-wise/mapwise-dataset), this live benchmark provides continuous evaluation of model performance on geographic reasoning.

### 🎯 Why CARTO MERIT?

**Real-World Geographic Understanding**: Unlike synthetic datasets, we evaluate models on actual maps that humans encounter daily:
- 🗺️ **Choropleth visualizations** with complex legends and data patterns
- 🌍 **Spatial reasoning** tasks requiring geographic knowledge
- 📊 **Legend comprehension** and data interpretation
- 🔍 **Counterfactual analysis** for robustness testing

**Live, Continuous Evaluation**: 
- 🔄 **Automatic evaluation** of new model submissions
- 📊 **Real-time leaderboard** updates
- 🌍 **Community-driven** benchmark expansion
- 📈 **Transparent, reproducible** results

### 📊 Current Benchmark Statistics

| Metric | Value |
|--------|-------|
| **Maps** | 138 (98 USA choropleth + 40 counterfactuals) |
| **Questions** | 1,171 |
| **Task Types** | 4 (Choropleth, Spatial, Legend, Counterfactual) |
| **Models Evaluated** | Live leaderboard available |
| **Live Site** | ✅ [CARTO MERIT](https://jatorre.github.io/mapbench.live) |

## 🏆 Current Leaderboard

Visit the [live leaderboard](https://jatorre.github.io/mapbench.live) to see the latest model performance rankings.

## 🔬 Based on MapWise Research

This benchmark implements the methodology from **"MapWise: Evaluating Vision-Language Models for Advanced Map Queries"**, using their curated dataset of real-world geographic visualizations.

**Citation**: When using CARTO MERIT, please cite both this benchmark and the original MapWise research:

```bibtex
@misc{cartomerit2025,
  title={CARTO MERIT: Map Evaluation and Reasoning Integrated Test},
  author={},
  year={2025},
  url={https://github.com/jatorre/mapbench.live}
}

@misc{mapwise2024,
  title={MapWise: Evaluating Vision-Language Models for Advanced Map Queries},
  author={MapWise Team},
  year={2024},
  url={https://github.com/map-wise/mapwise-dataset}
}
```

## 🚀 Submit Your Model

Add your vision-language model to the leaderboard:

1. **Fork** this repository
2. **Edit** `data/models.yaml` with your model configuration:
   ```yaml
   - id: your-model-name
     provider: openai  # or vertexai, anthropic
     endpoint: "openai:gpt-4o"
     auth: "env:YOUR_API_KEY"
     description: "Your model description"
   ```
3. **Submit** a pull request
4. **Automated evaluation** runs and updates the leaderboard

## 🏗️ Architecture

```
carto-merit/
├── 🌐 app/                  # Single-page website
├── 🤖 benchmarks/           # Python evaluation pipeline
│   ├── runner.py           # Model execution (OpenAI, Vertex AI, Anthropic)
│   ├── scorer.py           # GPT-4o based scoring
│   └── evaluator.py        # End-to-end benchmark orchestration
├── 📊 data/
│   ├── tasks/              # 138 map images + JSON metadata  
│   ├── models.yaml         # Model registry (edit to add models!)
│   └── results/            # Benchmark outputs & leaderboard
├── 🔧 scripts/             # CLI tools for running benchmarks
└── ⚙️ .github/workflows/   # Automated CI/CD
```

## 📖 Evaluation Tasks

### Task Categories

1. **Choropleth Analysis** (98 maps)
   - Interpret color-coded geographic data
   - *"Which state has the highest population density?"*

2. **Spatial Reasoning** (650+ questions)
   - Understand geographic relationships
   - *"Name the northernmost state with higher values than neighbors"*

3. **Legend Comprehension** (321+ questions)
   - Parse map legends and scales
   - *"How many distinct categories does the legend contain?"*

4. **Counterfactual Analysis** (40 maps)
   - Detect manipulated map data
   - *"Identify inconsistent geographic patterns"*

## 🛠️ Local Development

### Run Benchmarks
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key"

# Run evaluation
python3 scripts/run_benchmark.py --models "gpt-4o-mini"
```

### Development Server
```bash
cd app
npm install
npm run dev
```

## 🤝 Contributing

- **Add Models**: Edit `data/models.yaml` and submit PR
- **Add Tasks**: Use `scripts/add_task.py` for new map tasks
- **Report Issues**: Use GitHub Issues for bugs or suggestions
- **Expand Dataset**: Help grow the benchmark with new map types

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **MapWise Team** for the foundational research and dataset
- **OpenAI, Google, Anthropic** for model APIs  
- **Research Community** for contributions and feedback

---

**🌟 Star this repository** to stay updated with the latest vision-language model evaluations on map understanding!

**🗺️ Visit CARTO MERIT**: [jatorre.github.io/mapbench.live](https://jatorre.github.io/mapbench.live)