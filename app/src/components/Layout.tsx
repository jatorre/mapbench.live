import Link from 'next/link'
import { useRouter } from 'next/router'
import { MapIcon, TrophyIcon, GridIcon, GithubIcon } from 'lucide-react'

export default function Layout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  
  const navItems = [
    { href: '/', label: 'Home', icon: MapIcon },
    { href: '/leaderboard', label: 'Leaderboard', icon: TrophyIcon },
    { href: '/tasks', label: 'Tasks', icon: GridIcon },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link href="/" className="flex items-center space-x-2">
                  <MapIcon className="h-8 w-8 text-mapbench-blue" />
                  <span className="text-xl font-bold">MapBench.Live</span>
                </Link>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = router.pathname === item.href
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                        isActive
                          ? 'border-mapbench-blue text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.label}
                    </Link>
                  )
                })}
              </div>
            </div>
            <div className="flex items-center">
              <a
                href="https://github.com/map-wise/mapwise-dataset"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-gray-700"
              >
                <GithubIcon className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </nav>
      
      <main>{children}</main>
      
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            MapBench.Live - Real-World Map Understanding Benchmark for Vision-Language Models
          </p>
        </div>
      </footer>
    </div>
  )
}