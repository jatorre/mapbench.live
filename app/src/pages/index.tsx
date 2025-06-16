import { useState, useEffect } from 'react'
import Link from 'next/link'
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
        // Add human baseline to the data
        const dataWithHuman = [
          {
            rank: 1,
            model_id: "Human Expert",
            overall_score: 94.0,
            total_questions: 1171,
            last_updated: "2024-12-01T00:00:00Z",
            is_human: true
          },
          ...data.map((entry: LeaderboardEntry) => ({
            ...entry,
            rank: entry.rank + 1
          }))
        ]
        setLeaderboard(dataWithHuman)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error loading leaderboard:', error)
        // Fallback data with human baseline
        const fallbackData: LeaderboardEntry[] = [
          {
            rank: 1,
            model_id: "Human Expert",
            overall_score: 94.0,
            total_questions: 1171,
            last_updated: "2024-12-01T00:00:00Z",
            is_human: true
          },
          {
            rank: 2,
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
        {/* Showcase Example */}
        <section className="mb-12">
          <div className="bg-white rounded-lg shadow p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              How Well Can AI Understand Maps?
            </h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Map Image */}
              <div>
                <div className="bg-gray-100 rounded-lg overflow-hidden">
                  <img 
                    src="/mapbench.live/data/tasks/mapwise-usa-109.png" 
                    alt="USA Choropleth Map showing state data with 5 distinct value categories"
                    className="w-full h-auto"
                  />
                </div>
                <p className="text-center text-sm text-gray-500 mt-2">USA Choropleth Map (MapWise Dataset)</p>
              </div>
              
              {/* Question and Answers */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">Example Question:</h3>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-blue-900 font-medium">
                      &ldquo;What value range does the darkest shade represent?&rdquo;
                    </p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="border-l-4 border-green-500 pl-4">
                    <div className="flex items-center mb-2">
                      <span className="text-green-600 font-semibold">👤 Human Expert</span>
                      <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded">94% accuracy</span>
                    </div>
                    <p className="text-gray-700">&ldquo;29.1-34.2% - I can see this represents the highest value category based on the legend and the darkest shaded states.&rdquo;</p>
                  </div>
                  
                  <div className="border-l-4 border-blue-500 pl-4">
                    <div className="flex items-center mb-2">
                      <span className="text-blue-600 font-semibold">🤖 GPT-4o</span>
                      <span className="ml-2 bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">87% accuracy</span>
                    </div>
                    <p className="text-gray-700">&ldquo;The darkest shade represents the range 29.1-34.2%.&rdquo;</p>
                  </div>
                  
                  <div className="border-l-4 border-yellow-500 pl-4">
                    <div className="flex items-center mb-2">
                      <span className="text-yellow-600 font-semibold">🤖 GPT-4o-mini</span>
                      <span className="ml-2 bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">76% accuracy</span>
                    </div>
                    <p className="text-gray-700">&ldquo;The darkest color appears to represent the highest values on the map.&rdquo;</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

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
                        &ldquo;MapWise: Evaluating Vision-Language Models for Advanced Map Queries&rdquo;
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

        {/* Why CARTO is doing this */}
        <section className="mb-12">
          <div className="bg-white rounded-lg shadow p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Why CARTO is Building This</h3>
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-xl font-semibold text-gray-900 mb-3">Our Mission</h4>
                  <p className="text-gray-700 mb-4">
                    At CARTO, we believe that spatial intelligence is fundamental to solving the world&rsquo;s biggest challenges. 
                    As AI systems become more capable of understanding visual data, evaluating their spatial reasoning abilities 
                    becomes crucial for real-world applications.
                  </p>
                  <p className="text-gray-700">
                    CARTO MERIT helps the research community understand how well vision-language models can interpret 
                    the maps and geospatial visualizations that drive decision-making across industries.
                  </p>
                </div>
                <div>
                  <h4 className="text-xl font-semibold text-gray-900 mb-3">Real-World Impact</h4>
                  <div className="space-y-3">
                    <div className="flex items-start">
                      <div className="text-blue-600 font-bold mr-3">🌍</div>
                      <div>
                        <div className="font-medium text-gray-900">Urban Planning</div>
                        <div className="text-sm text-gray-600">AI systems that understand demographic and infrastructure maps</div>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <div className="text-green-600 font-bold mr-3">🌿</div>
                      <div>
                        <div className="font-medium text-gray-900">Climate Analysis</div>
                        <div className="text-sm text-gray-600">Models that can interpret environmental and weather data visualizations</div>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <div className="text-purple-600 font-bold mr-3">📊</div>
                      <div>
                        <div className="font-medium text-gray-900">Business Intelligence</div>
                        <div className="text-sm text-gray-600">Automated insights from geographic market analysis and logistics maps</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
                <div className="flex items-center mb-3">
                  <div className="text-2xl mr-3">🚀</div>
                  <h4 className="text-lg font-semibold text-gray-900">Join the Research</h4>
                </div>
                <p className="text-gray-700 mb-4">
                  Want to contribute to spatial AI research? Add your model to the leaderboard or explore our evaluation tasks.
                </p>
                <div className="flex flex-wrap gap-3">
                  <a 
                    href="https://github.com/jatorre/mapbench.live" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center"
                  >
                    <GithubIcon className="h-4 w-4 mr-2" />
                    View Repository
                  </a>
                  <Link 
                    href="/tasks" 
                    className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Explore Tasks
                  </Link>
                </div>
              </div>
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