import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getExpertDetails } from '../services/experts'
import { getExpertAvailability, SlotAvailability } from '../services/bookings'

export default function ExpertDetailsPage() {
  const { id } = useParams()
  const [expert, setExpert] = useState<any>(null)
  const [slots, setSlots] = useState<SlotAvailability[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      setLoading(true)
      getExpertDetails(id)
        .then((exp) => {
          setExpert(exp)
          return getExpertAvailability(Number(id))
        })
        .then((avail) => {
          setSlots(avail?.slots || [])
        })
        .catch((err) => console.error('Failed to load expert details', err))
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading || !expert) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-r-transparent inline-block" />
          <p className="mt-3 text-sm text-slate-500 font-medium">Loading expert profile & schedule...</p>
        </div>
      </div>
    )
  }

  const openSlotsCount = slots.filter(s => s.available).length

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <div className="rounded-3xl bg-white p-8 sm:p-10 shadow-sm border border-slate-100">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between border-b border-slate-100 pb-8">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-0.5 text-xs font-semibold text-emerald-700 border border-emerald-200">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                Verified Expert
              </span>
              <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wider">
                {expert.company}
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              {expert.user?.name || 'Expert'}
            </h1>
            <p className="mt-1 text-base font-semibold text-indigo-600">{expert.title}</p>
          </div>

          <div className="rounded-3xl bg-slate-50 p-5 border border-slate-100 text-center sm:text-right min-w-[160px]">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Consultation Rate</p>
            <p className="mt-1 text-3xl font-black text-slate-900">₹{expert.hourly_rate}<span className="text-sm font-normal text-slate-500">/hr</span></p>
            <p className="text-xs text-amber-500 font-bold mt-1">★ {(expert.rating || 5.0).toFixed(1)} Rating</p>
          </div>
        </div>

        <div className="mt-8 grid gap-8 md:grid-cols-12">
          {/* Main Info (7 cols) */}
          <div className="md:col-span-7 space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-900">About & Background</h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">
                {expert.bio || 'Experienced engineering leader dedicated to mentoring learners on architectural best practices and production deployment.'}
              </p>
            </div>

            {expert.skills && (
              <div>
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Verified Skills & Tools</h2>
                <div className="flex flex-wrap gap-1.5">
                  {expert.skills.split(',').map((skill: string, idx: number) => (
                    <span key={idx} className="rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="rounded-2xl bg-slate-50 p-5 border border-slate-100">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Key Highlights</h3>
              <ul className="space-y-2 text-xs text-slate-700">
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span><strong>{expert.experience_years} Years</strong> of verified industry experience</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>1-on-1 private video mentorship sessions via Jitsi Meet</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>Portfolio code reviews and architectural whiteboarding</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Availability Schedule Card (5 cols) */}
          <div className="md:col-span-5 rounded-2xl bg-slate-50 p-6 border border-slate-200/80 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-bold text-slate-900">Next Available Schedule</h2>
                <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-[11px] font-bold text-emerald-800">
                  {openSlotsCount} Open Slots
                </span>
              </div>

              <p className="text-xs text-slate-500 mb-3">
                Working Hours: 09:00 - 18:00 UTC. Bookings are confirmed in real-time.
              </p>

              <div className="grid grid-cols-2 gap-2 mb-4">
                {slots.slice(0, 6).map((s) => (
                  <div
                    key={s.slot}
                    className={`px-2.5 py-2 rounded-xl text-xs flex items-center justify-between border ${
                      s.available
                        ? 'bg-white border-slate-200 text-slate-800 font-semibold'
                        : 'bg-slate-100 border-slate-200 text-slate-400 line-through'
                    }`}
                  >
                    <span>{s.time}</span>
                    <span className="text-[10px] uppercase">{s.available ? 'Free' : 'Booked'}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 space-y-2">
              <Link
                to={`/book?expert_id=${expert.id}`}
                className="block w-full text-center rounded-full bg-indigo-600 py-3 text-sm font-bold text-white hover:bg-indigo-700 shadow-sm transition"
              >
                Book Session (₹{expert.hourly_rate}/hr)
              </Link>
              <Link
                to="/chat"
                className="block w-full text-center rounded-full bg-white border border-slate-200 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50 transition"
              >
                Ask Questions in AI Chat
              </Link>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
