import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <section className="rounded-3xl bg-white p-10 shadow-lg">
        <div className="space-y-8">
          <div className="space-y-4">
            <p className="text-sm uppercase tracking-[0.3em] text-indigo-600">ExpertVerse AI</p>
            <h1 className="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
              Book AI-backed expertise for your next critical project.
            </h1>
            <p className="max-w-2xl text-lg text-slate-700">
              Describe your goals, connect with an expert, and get a custom roadmap with meeting summaries, action plans, and expert twin support.
            </p>
          </div>
          <div className="flex flex-wrap gap-4">
            <Link to="/experts" className="rounded-full bg-indigo-600 px-6 py-3 text-white shadow hover:bg-indigo-700">
              Browse Experts
            </Link>
            <Link to="/chat" className="rounded-full border border-slate-300 px-6 py-3 text-slate-900 hover:bg-slate-100">
              Try AI Chat
            </Link>
          </div>
        </div>
      </section>
      <section className="mt-10 grid gap-6 sm:grid-cols-3">
        <div className="rounded-3xl bg-white p-6 shadow">
          <h2 className="text-xl font-semibold">AI Problem Analyzer</h2>
          <p className="mt-3 text-sm text-slate-600">Analyze your challenge and identify the best pathways.</p>
        </div>
        <div className="rounded-3xl bg-white p-6 shadow">
          <h2 className="text-xl font-semibold">Expert Matching</h2>
          <p className="mt-3 text-sm text-slate-600">Get recommended experts based on skills, reviews, and past cases.</p>
        </div>
        <div className="rounded-3xl bg-white p-6 shadow">
          <h2 className="text-xl font-semibold">Booking & Planning</h2>
          <p className="mt-3 text-sm text-slate-600">Reserve time, join meetings, and track your action plan.</p>
        </div>
      </section>
    </main>
  )
}
