import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getExpertDetails } from '../services/experts'

export default function ExpertDetailsPage() {
  const { id } = useParams()
  const [expert, setExpert] = useState<any>(null)

  useEffect(() => {
    if (id) {
      getExpertDetails(id).then(setExpert)
    }
  }, [id])

  if (!expert) {
    return <div className="p-8 text-center">Loading expert details...</div>
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="rounded-3xl bg-white p-10 shadow-lg">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-indigo-600">{expert.title}</p>
            <h1 className="mt-3 text-4xl font-semibold text-slate-900">{expert.user?.name || 'Expert'}</h1>
            <p className="mt-2 text-slate-600">{expert.company}</p>
          </div>
          <div className="rounded-3xl bg-slate-100 px-6 py-4 text-center">
            <p className="text-sm text-slate-500">Hourly rate</p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">${expert.hourly_rate?.toFixed(0) || '150'}</p>
          </div>
        </div>
        <div className="mt-8 grid gap-6 sm:grid-cols-2">
          <div className="rounded-3xl bg-slate-50 p-6">
            <h2 className="text-xl font-semibold">About</h2>
            <p className="mt-3 text-sm leading-7 text-slate-600">{expert.bio}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <h2 className="text-xl font-semibold">Highlights</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-600">
              <li>Rating: ★ {expert.rating?.toFixed(1) || '4.8'}</li>
              <li>Experience: {expert.experience_years} years</li>
              <li>Available for AI-driven coaching</li>
            </ul>
          </div>
        </div>
        <div className="mt-8 flex flex-wrap gap-4">
          <Link to="/book" className="rounded-full bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-700">
            Book Session
          </Link>
          <Link to="/chat" className="rounded-full border border-slate-300 px-6 py-3 text-slate-900 hover:bg-slate-100">
            Ask Expert Twin
          </Link>
        </div>
      </div>
    </main>
  )
}
