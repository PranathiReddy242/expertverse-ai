import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getExperts } from '../services/experts'

export default function ExpertsPage() {
  const [experts, setExperts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState('')

  const fetchExperts = async (query?: string) => {
    setLoading(true)
    try {
      const data = await getExperts(query)
      setExperts(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load experts. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExperts()
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchExperts(searchQuery)
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Expert Directory</h1>
          <p className="mt-1 text-sm text-slate-500">
            Connect with verified domain experts across AI, Cloud Architecture, and Software Engineering
          </p>
        </div>
        <form onSubmit={handleSearch} className="flex gap-2 w-full md:w-auto">
          <input
            type="text"
            placeholder="Search by name, title, company..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full md:w-80 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm shadow-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="submit"
            className="rounded-full bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 shadow-sm"
          >
            Search
          </button>
        </form>
      </div>

      {loading ? (
        <div className="mt-16 flex flex-col items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
          <p className="mt-3 text-sm text-slate-500">Loading verified experts...</p>
        </div>
      ) : error ? (
        <div className="mt-8 rounded-3xl bg-red-50 p-6 text-center border border-red-200">
          <p className="text-red-700 font-medium">{error}</p>
          <button
            onClick={() => fetchExperts()}
            className="mt-3 rounded-full bg-red-600 px-4 py-2 text-xs font-semibold text-white hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      ) : experts.length === 0 ? (
        <div className="mt-12 rounded-3xl bg-slate-50 border border-slate-200 p-12 text-center">
          <p className="text-lg font-semibold text-slate-700">No verified experts found.</p>
          <p className="mt-1 text-sm text-slate-500">
            {searchQuery ? `No verified experts matching "${searchQuery}".` : 'Newly registered experts are currently awaiting administrator verification.'}
          </p>
          {searchQuery && (
            <button
              onClick={() => { setSearchQuery(''); fetchExperts(''); }}
              className="mt-4 rounded-full bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700"
            >
              Clear Filter
            </button>
          )}
        </div>
      ) : (
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {experts.map((expert) => (
            <Link
              key={expert.id}
              to={`/experts/${expert.id}`}
              className="group flex flex-col justify-between rounded-3xl bg-white p-6 shadow-sm border border-slate-100 transition-all duration-200 hover:-translate-y-1 hover:shadow-md"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 border border-emerald-200">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    Verified
                  </span>
                  <span className="text-sm font-bold text-slate-800">₹{expert.hourly_rate}/hr</span>
                </div>

                <h2 className="mt-4 text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                  {expert.user?.name || 'Expert'}
                </h2>
                <p className="text-xs font-semibold text-indigo-600">{expert.title}</p>
                <p className="mt-1 text-xs text-slate-500">{expert.company}</p>

                {expert.bio && (
                  <p className="mt-3 text-xs text-slate-600 line-clamp-3 leading-relaxed">
                    {expert.bio}
                  </p>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span>{expert.experience_years} yrs experience</span>
                <span className="font-semibold text-amber-500">★ {(expert.rating || 5.0).toFixed(1)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </main>
  )
}
