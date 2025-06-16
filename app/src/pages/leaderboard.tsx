import { useState, useEffect } from 'react'
import { TrophyIcon, ChevronUpIcon, ChevronDownIcon } from 'lucide-react'

interface LeaderboardEntry {
  rank: number
  model_id: string
  overall_score: number
  total_questions: number
  last_updated: string
  [key: string]: any
}

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // In production, this would fetch from an API
    // For now, we'll use mock data
    const mockData: LeaderboardEntry[] = [
      {
        rank: 1,
        model_id: "gpt-4o",
        overall_score: 92.5,
        total_questions: 1171,
        last_updated: "2024-01-15T12:00:00Z",
        score_choropleth: 93.2,
        score_weather: 91.8
      },
      {
        rank: 2,
        model_id: "gemini-2-flash",
        overall_score: 89.3,
        total_questions: 1171,
        last_updated: "2024-01-15T12:00:00Z",
        score_choropleth: 90.1,
        score_weather: 88.5
      },
      {
        rank: 3,
        model_id: "gemini-1-5-pro",
        overall_score: 87.8,
        total_questions: 1171,
        last_updated: "2024-01-15T12:00:00Z",
        score_choropleth: 88.5,
        score_weather: 87.1
      },
      {
        rank: 4,
        model_id: "gpt-4o-mini",
        overall_score: 82.4,
        total_questions: 1171,
        last_updated: "2024-01-15T12:00:00Z",
        score_choropleth: 83.1,
        score_weather: 81.7
      }
    ]
    
    setLeaderboard(mockData)
    setLoading(false)
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

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">Loading leaderboard...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-8">
        <div className="flex justify-center items-center mb-4">
          <TrophyIcon className="h-10 w-10 text-yellow-500 mr-3" />
          <h1 className="text-4xl font-bold text-gray-900">Leaderboard</h1>
        </div>
        <p className="text-lg text-gray-600">
          Vision-Language Model Performance on Map Understanding Tasks
        </p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
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
                Choropleth
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Weather
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
                  <span className="text-2xl">{getRankIcon(entry.rank)}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{entry.model_id}</div>
                    <div className="text-sm text-gray-500">
                      {entry.rank === 1 && <span className="text-green-600">↑ Leader</span>}
                      {entry.rank > 1 && (
                        <span className="text-gray-400">
                          {(leaderboard[0].overall_score - entry.overall_score).toFixed(1)} pts behind
                        </span>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className={`text-lg font-semibold ${getScoreColor(entry.overall_score)}`}>
                    {entry.overall_score.toFixed(1)}%
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {entry.score_choropleth?.toFixed(1)}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {entry.score_weather?.toFixed(1)}%
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

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">How to Submit Your Model</h3>
        <p className="text-blue-700">
          To add your model to the leaderboard, create a pull request adding your model configuration to{' '}
          <code className="bg-blue-100 px-2 py-1 rounded text-sm">data/models.yaml</code>.
          The benchmark will automatically run and update the leaderboard.
        </p>
      </div>
    </div>
  )
}