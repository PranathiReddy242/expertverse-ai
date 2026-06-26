import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getExperts } from '../services/experts'

export default function ExpertsPage() {
  const [experts, setExperts] = useState<any[]>([])

  useEffect(() => {
    getExperts().then(setExperts)
  }, [])

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-3xl font-semibold">Expert Directory</h1>
      <div className="mt-8 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        {experts.map((expert) => (
          <Link key={expert.id} to={`/experts/${expert.id}`} className="group rounded-3xl bg-white p-6 shadow transition hover:-translate-y-1">
            <p className="text-sm text-indigo-600">{expert.title}</p>
            <h2 className="mt-3 text-xl font-semibold text-slate-900">{expert.user?.name || 'Expert'}</h2>
            <p className="mt-2 text-sm text-slate-600">{expert.company}</p>
            <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
              <span>{expert.experience_years} yrs experience</span>
              <span>★ {expert.rating?.toFixed(1) || '4.5'}</span>
            </div>
          </Link>
        ))}
      </div>
    </main>
  )
}
