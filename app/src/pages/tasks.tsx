import { useState, useEffect } from 'react'
import { SearchIcon, FilterIcon, EyeIcon } from 'lucide-react'
import Image from 'next/image'

interface Task {
  id: string
  map_image: string
  context: string
  type: string
  questions: Array<{
    q: string
    a: string
    type: string
  }>
  metadata?: {
    country?: string
    counterfactual_type?: string
  }
}

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')

  useEffect(() => {
    // In production, this would fetch from an API
    // For now, we'll create sample data
    const sampleTasks: Task[] = [
      {
        id: "mapwise-usa-8808",
        map_image: "/data/tasks/mapwise-usa-8808.png",
        context: "Choropleth map of USA",
        type: "choropleth",
        questions: [
          {
            q: "Name the North most state that belongs to a higher value range compared to all its neighbours.",
            a: "Washington",
            type: "single_answer"
          },
          {
            q: "How many distinct categories does the legend contain?",
            a: "4",
            type: "count"
          }
        ],
        metadata: { country: "usa" }
      },
      {
        id: "weather-madrid-2024-06",
        map_image: "/data/tasks/weather_madrid_2024_06.png",
        context: "Weather forecast for Madrid on June 12, 2024",
        type: "weather",
        questions: [
          {
            q: "What is the temperature expected in Madrid?",
            a: "Around 30°C",
            type: "short_answer"
          }
        ]
      }
    ]
    
    setTasks(sampleTasks)
    setFilteredTasks(sampleTasks)
    setLoading(false)
  }, [])

  useEffect(() => {
    let filtered = tasks

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(task =>
        task.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.context.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.questions.some(q => q.q.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }

    // Apply type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(task => task.type === typeFilter)
    }

    setFilteredTasks(filtered)
  }, [searchQuery, typeFilter, tasks])

  const taskTypes = ['all', 'choropleth', 'weather', 'choropleth_counterfactual']

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">Loading tasks...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Task Explorer</h1>
        <p className="text-lg text-gray-600">
          Browse and explore the map understanding tasks in our benchmark
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-mapbench-blue focus:border-transparent"
            />
            <SearchIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FilterIcon className="h-5 w-5 text-gray-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-mapbench-blue focus:border-transparent"
          >
            {taskTypes.map(type => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Types' : type.replace('_', ' ')}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Task Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTasks.map(task => (
          <div
            key={task.id}
            className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => setSelectedTask(task)}
          >
            <div className="aspect-w-16 aspect-h-9 bg-gray-200">
              <div className="p-4 flex items-center justify-center text-gray-500">
                <MapIcon className="h-12 w-12" />
              </div>
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-1">{task.id}</h3>
              <p className="text-sm text-gray-600 mb-2">{task.context}</p>
              <div className="flex justify-between items-center">
                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {task.type}
                </span>
                <span className="text-xs text-gray-500">
                  {task.questions.length} questions
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Task Detail Modal */}
      {selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">{selectedTask.id}</h2>
                <button
                  onClick={() => setSelectedTask(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-600 mb-2">{selectedTask.context}</p>
                <div className="flex gap-2">
                  <span className="text-sm bg-gray-100 px-2 py-1 rounded">
                    {selectedTask.type}
                  </span>
                  {selectedTask.metadata?.country && (
                    <span className="text-sm bg-blue-100 px-2 py-1 rounded">
                      {selectedTask.metadata.country}
                    </span>
                  )}
                </div>
              </div>

              <div className="mb-6 bg-gray-100 p-4 rounded-lg">
                <div className="text-center text-gray-500">
                  <MapIcon className="h-24 w-24 mx-auto mb-2" />
                  <p>Map: {selectedTask.map_image}</p>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-lg mb-3">Questions ({selectedTask.questions.length})</h3>
                <div className="space-y-3">
                  {selectedTask.questions.map((q, idx) => (
                    <div key={idx} className="border rounded-lg p-4">
                      <p className="font-medium mb-2">{q.q}</p>
                      <p className="text-sm text-gray-600">
                        <span className="font-semibold">Expected Answer:</span> {q.a}
                      </p>
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded mt-2 inline-block">
                        {q.type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Import MapIcon since we're using it
import { MapIcon } from 'lucide-react'