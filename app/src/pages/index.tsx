import { useState, useEffect } from 'react'
import { MapIcon, TrophyIcon, BarChart3Icon, FileTextIcon, GithubIcon, ExternalLinkIcon } from 'lucide-react'

interface LeaderboardEntry {
  rank: number
  model_id: string
  overall_score: number
  total_questions: number
  last_updated: string
  [key: string]: any
}

interface TaskSample {
  id: string
  type: string
  questions_count: number
  context: string
}

export default function Home() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [taskStats, setTaskStats] = useState({
    total: 138,
    choropleth: 98,
    counterfactual: 40,
    questions: 1171
  })

  useEffect(() => {
    // Load leaderboard data
    fetch('/mapbench.live/data/results/leaderboard_latest.json')
      .then(response => response.json())
      .then(data => {
        setLeaderboard(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error loading leaderboard:', error)
        // Fallback data
        const fallbackData: LeaderboardEntry[] = [
          {
            rank: 1,
            model_id: "gpt-4o-mini-test",
            overall_score: 76.7,
            total_questions: 30,
            last_updated: new Date().toISOString()
          }
        ]
        setLeaderboard(fallbackData)
        setLoading(false)
      })
  }, [])

  const getRankIcon = (rank: number) => {
    if (rank === 1) return "🥇"
    if (rank === 2) return "🥈" 
    if (rank === 3) return "🥉"
    return rank.toString()
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600"
    if (score >= 80) return "text-yellow-600"
    return "text-red-600"
  }

  const sampleTasks = [
    {
      type: "Choropleth Analysis",
      description: "Interpret color-coded geographic data maps",
      example: "Which state has the highest population density?",
      count: 98
    },
    {
      type: "Spatial Reasoning", 
      description: "Understand geographic relationships and patterns",
      example: "Name the northernmost state with higher values than neighbors",
      count: 650
    },
    {
      type: "Legend Comprehension",
      description: "Parse and interpret map legends and scales", 
      example: "How many distinct categories does the legend contain?",
      count: 321
    },
    {
      type: "Counterfactual Analysis",
      description: "Detect manipulated or synthetic map data",
      example: "Identify inconsistent geographic patterns",
      count: 40
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <MapIcon className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">CARTO MERIT</h1>
                <p className="text-sm text-gray-600">Map Evaluation and Reasoning Integrated Test</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a 
                href="https://github.com/map-wise/mapwise-dataset" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <GithubIcon className="h-5 w-5 mr-1" />
                MapWise Dataset
              </a>
              <a 
                href="https://github.com/jatorre/mapbench.live" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <GithubIcon className="h-5 w-5 mr-1" />
                Source Code
              </a>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Introduction */}
        <section className="mb-12">
          <div className="bg-white rounded-lg shadow p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Evaluating Vision-Language Models on Real-World Map Understanding
            </h2>
            <div className="prose max-w-none text-gray-700">
              <p className="text-lg mb-4">
                CARTO MERIT is a comprehensive benchmark for evaluating how well vision-language models understand and reason about geographic maps. 
                Unlike synthetic datasets, we use real-world maps that humans encounter daily.
              </p>
              
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <div className="flex">
                  <FileTextIcon className="h-5 w-5 text-blue-400 mt-0.5 mr-2" />
                  <div>
                    <p className="text-sm text-blue-700">
                      <strong>Based on MapWise Research:</strong> This benchmark implements the methodology from 
                      <a href="https://github.com/map-wise/mapwise-dataset" className="underline hover:text-blue-900 ml-1" target="_blank" rel="noopener noreferrer">
                        "MapWise: Evaluating Vision-Language Models for Advanced Map Queries"
                      </a>
                      , using their curated dataset of real-world geographic visualizations.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{taskStats.total}</div>
                  <div className="text-sm text-gray-600">Maps</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{taskStats.questions}</div>
                  <div className="text-sm text-gray-600">Questions</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{leaderboard.length}</div>
                  <div className="text-sm text-gray-600">Models Tested</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Task Types */}
        <section className="mb-12">
          <div className="bg-white rounded-lg shadow p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <BarChart3Icon className="h-6 w-6 mr-2 text-blue-600" />
              Evaluation Tasks
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {sampleTasks.map((task, index) => (
                <div key={index} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="text-lg font-semibold text-gray-900">{task.type}</h4>
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {task.count} questions
                    </span>
                  </div>
                  <p className="text-gray-600 mb-3">{task.description}</p>
                  <div className="bg-gray-50 p-3 rounded italic text-sm text-gray-700">
                    Example: "{task.example}"
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Leaderboard */}
        <section className="mb-12">
          <div className="bg-white rounded-lg shadow p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <TrophyIcon className="h-6 w-6 mr-2 text-yellow-500" />
              Model Performance Leaderboard
            </h3>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading results...</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rank
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Model
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Overall Score
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Questions
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Updated
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leaderboard.map((entry, index) => (
                      <tr key={entry.model_id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          <span className="text-xl">{getRankIcon(entry.rank)}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{entry.model_id}</div>
                            {entry.rank === 1 && (
                              <div className="text-sm text-green-600">🏆 Current Leader</div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={`text-lg font-semibold ${getScoreColor(entry.overall_score)}`}>
                            {entry.overall_score.toFixed(1)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {entry.total_questions.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(entry.last_updated).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>

        {/* How to Submit */}
        <section className="mb-12">
          <div className="bg-white rounded-lg shadow p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Submit Your Model</h3>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <p className="text-blue-900 mb-4">
                Add your vision-language model to the leaderboard by submitting a pull request:
              </p>
              <ol className="list-decimal list-inside space-y-2 text-blue-800">
                <li>Fork the <a href="https://github.com/jatorre/mapbench.live" className="underline">repository</a></li>
                <li>Add your model configuration to <code className="bg-blue-100 px-2 py-1 rounded">data/models.yaml</code></li>
                <li>Submit a pull request with your model details</li>
                <li>Our automated system will evaluate your model and update the leaderboard</li>
              </ol>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center text-gray-500 text-sm">
          <p>
            CARTO MERIT • Built with data from{' '}
            <a href="https://github.com/map-wise/mapwise-dataset" className="text-blue-600 hover:underline">
              MapWise Dataset
            </a>
            {' '}• Evaluating Vision-Language Models on Real-World Maps
          </p>
        </footer>
      </main>
    </div>
  )
}