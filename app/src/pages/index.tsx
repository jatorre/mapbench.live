import { MapIcon, BarChart3Icon, RefreshCwIcon, UsersIcon } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const features = [
    {
      icon: MapIcon,
      title: 'Real-World Maps',
      description: 'Evaluate VLMs on actual choropleth maps from weather, elections, and urban planning'
    },
    {
      icon: RefreshCwIcon,
      title: 'Live Benchmarks',
      description: 'Continuously updated with new maps and models, unlike static datasets'
    },
    {
      icon: BarChart3Icon,
      title: 'Comprehensive Metrics',
      description: 'Track performance across different map types, question categories, and complexity levels'
    },
    {
      icon: UsersIcon,
      title: 'Community Driven',
      description: 'Submit new maps, models, and contribute to the growing benchmark'
    }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          MapBench.Live
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          The definitive live benchmark for evaluating vision-language models on real-world map interpretation tasks
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div className="rounded-md shadow">
            <Link
              href="/leaderboard"
              className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-mapbench-blue hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
            >
              View Leaderboard
            </Link>
          </div>
          <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
            <Link
              href="/tasks"
              className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-mapbench-blue bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
            >
              Explore Tasks
            </Link>
          </div>
        </div>
      </div>

      <div className="mt-20">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div key={index} className="relative">
                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-mapbench-blue text-white">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-gray-900">{feature.title}</h3>
                  <p className="mt-2 text-base text-gray-500 text-center">
                    {feature.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="mt-20 bg-gray-100 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Current Statistics</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="bg-white rounded-lg p-4">
            <p className="text-3xl font-bold text-mapbench-blue">138</p>
            <p className="text-sm text-gray-500">Total Maps</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <p className="text-3xl font-bold text-mapbench-green">1,171</p>
            <p className="text-sm text-gray-500">Questions</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <p className="text-3xl font-bold text-mapbench-purple">4</p>
            <p className="text-sm text-gray-500">Models Evaluated</p>
          </div>
        </div>
      </div>
    </div>
  )
}