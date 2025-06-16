# MapBench.Live Setup Guide

## Repository Status ✅
Your code has been committed and is ready to push to GitHub!

## Next Steps

### 1. Push to GitHub
```bash
cd /Users/jatorre/workspace/merit
git push -u origin main
```

### 2. Set up GitHub Pages (for the website)
1. Go to your repo: https://github.com/jatorre/mapbench.live
2. Settings → Pages
3. Source: "GitHub Actions"
4. The deploy.yml workflow will build and deploy automatically

### 3. Set up API Keys (for benchmarks)
Add these secrets in GitHub Settings → Secrets and variables → Actions:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_APPLICATION_CREDENTIALS`: Your Google Cloud service account JSON

### 4. Test the Benchmark
```bash
# Install dependencies
pip install -r requirements.txt

# Run a test benchmark
python3 scripts/run_benchmark.py --models "gpt-4o-mini"
```

### 5. View the Website
- **Demo**: Open `demo.html` in your browser (works now!)
- **Full Site**: After GitHub Pages setup → https://jatorre.github.io/mapbench.live

## Project Structure
```
mapbench.live/
├── benchmarks/          # Python evaluation pipeline
├── app/                 # Next.js frontend
├── data/
│   ├── tasks/          # 138 MapWise tasks + images
│   ├── models.yaml     # Model configurations
│   └── results/        # Benchmark outputs
├── scripts/            # CLI tools
└── .github/workflows/  # CI/CD automation
```

## Available Commands
- `python3 scripts/run_benchmark.py` - Run benchmarks
- `python3 scripts/integrate_mapwise.py` - Import more MapWise data
- `python3 scripts/add_task.py` - Add custom tasks
- `cd app && npm run dev` - Run development server

The project is ready to go live! 🚀