import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

export default function ChatPage() {
  const navigate = useNavigate()
  const { token } = useAuth()
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    if (!token) {
      navigate('/login')
    } else {
      loadHistory()
    }
  }, [token, navigate])

  const loadHistory = async () => {
    try {
      const resp = await api.get('/agents/history')
      setHistory(resp.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load chat history')
    }
  }

  const handleSubmit = async (event?: React.FormEvent<HTMLFormElement>, queryText?: string) => {
    if (event) event.preventDefault()
    const textToSend = queryText || message
    if (!textToSend.trim()) return

    setLoading(true)
    setError('')

    try {
      const result = await api.post('/agents/chat', {
        message: textToSend
      })

      setResponse(result.data)
      setMessage('')
      loadHistory()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Chat request failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const samplePrompts = [
    "I want to become an AI/ML Engineer with a focus on ethical AI and LLMs.",
    "What are the ethical considerations and architectural steps for deploying AI systems in production?",
    "How do I transition from Frontend Development to Full-Stack Architecture?",
    "How can I prepare for Senior Software Engineer system design and behavioral interviews?"
  ]

  return (
    <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
      <div className="rounded-3xl bg-white p-6 shadow-sm sm:p-10 border border-slate-100">

        {/* Header */}
        <div className="border-b border-slate-100 pb-6">
          <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 mb-3">
            <span className="h-2 w-2 rounded-full bg-indigo-600 animate-pulse"></span>
            ExpertVerse AI Strategic Agent
          </div>
          <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
            Intelligent & Ethical AI Mentorship
          </h1>
          <p className="mt-2 text-slate-600">
            Ask any technical, career, or architectural question. Our AI agent synthesizes direct answers, ethical principles, personalized roadmaps, and connects you with verified mentors.
          </p>
        </div>

        {/* Sample Prompt Chips */}
        <div className="mt-6">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Suggested Queries:
          </p>
          <div className="flex flex-wrap gap-2">
            {samplePrompts.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setMessage(prompt)
                  handleSubmit(undefined, prompt)
                }}
                className="text-left text-xs bg-slate-50 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 rounded-full px-3 py-1.5 text-slate-700 transition"
              >
                💡 {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={(e) => handleSubmit(e)} className="mt-6 space-y-4">
          <div className="relative">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              rows={5}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-900 outline-none focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-100 transition resize-y text-sm sm:text-base"
              placeholder="Ask anything (e.g. 'I want to build a career in AI Engineering and understand responsible AI practices...')"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">
              {message.length > 0 ? `${message.length} characters` : 'Powered by Multi-Agent Reasoning & Expert Matching'}
            </span>
            <button
              type="submit"
              disabled={loading || !message.trim()}
              className="inline-flex items-center gap-2 rounded-full bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition shadow-sm hover:shadow"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  <span>Synthesizing Answer...</span>
                </>
              ) : (
                <>
                  <span>Submit Query</span>
                  <span>→</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700 flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError('')} className="text-red-500 hover:text-red-700 font-bold ml-2">✕</button>
          </div>
        )}

        {/* Current Active Response */}
        {response && (
          <div className="mt-8 rounded-3xl bg-gradient-to-b from-slate-50 to-indigo-50/20 p-6 sm:p-8 border border-slate-200 shadow-sm animate-fadeIn">
            
            <div className="flex items-center justify-between border-b border-slate-200/80 pb-4 mb-6">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
                  AI
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    ExpertVerse Agent Response
                  </h2>
                  <p className="text-xs text-slate-500">
                    Direct Solution • Ethical Best Practices • Action Plan
                  </p>
                </div>
              </div>
            </div>

            {/* Formatted Message */}
            <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-100">
              <div className="prose max-w-none text-slate-800 whitespace-pre-wrap leading-relaxed text-sm sm:text-base font-normal space-y-2">
                {response.message}
              </div>
            </div>

            {/* Matched Experts & Roadmap Grid */}
            <div className="mt-8 grid gap-6 md:grid-cols-2">

              {/* Recommended Experts */}
              <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-100 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-slate-900 text-base sm:text-lg flex items-center gap-2">
                      <span>👥</span> Recommended Mentors
                    </h3>
                    <Link to="/experts" className="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
                      View All →
                    </Link>
                  </div>

                  <p className="text-xs text-slate-600 mb-4">
                    Connect 1-on-1 with verified experts to review your action plan and code:
                  </p>

                  <ul className="space-y-3">
                    {response.recommended_experts && response.recommended_experts.length > 0 ? (
                      response.recommended_experts.map((expert: any) => (
                        <li key={expert.id} className="p-3.5 rounded-xl border border-slate-100 bg-slate-50 hover:bg-indigo-50/50 hover:border-indigo-100 transition">
                          <div className="flex items-center justify-between">
                            <div className="font-semibold text-slate-900 text-sm">
                              {expert.name}
                            </div>
                            <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                              ★ {expert.rating || '5.0'}
                            </span>
                          </div>
                          <div className="text-xs text-slate-600 mt-1">
                            {expert.title}
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5 flex items-center justify-between">
                            <span>Experience: {expert.experience_years} years</span>
                            <Link
                              to={`/booking/${expert.id}`}
                              className="text-xs font-semibold text-indigo-600 hover:underline"
                            >
                              Book Session →
                            </Link>
                          </div>
                        </li>
                      ))
                    ) : (
                      <p className="text-sm text-slate-500">No matching mentors found.</p>
                    )}
                  </ul>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-100">
                  <Link
                    to="/experts"
                    className="block w-full text-center rounded-xl bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 py-2.5 text-xs font-semibold text-slate-700 transition"
                  >
                    Browse Full Expert Directory
                  </Link>
                </div>
              </div>

              {/* Multi-Phase Roadmap */}
              <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-100">
                <h3 className="font-bold text-slate-900 text-base sm:text-lg mb-4 flex items-center gap-2">
                  <span>🗺️</span> Action Roadmap
                </h3>

                <div className="space-y-4 max-h-[420px] overflow-y-auto pr-1">
                  {response.roadmap &&
                    Object.entries(response.roadmap)
                      .filter(([key]) => key.startsWith('phase_'))
                      .map(([key, phase]: any) => (
                        <div key={key} className="rounded-xl border border-slate-100 bg-slate-50/60 p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-xs uppercase tracking-wider text-indigo-700">
                              {key.replace('_', ' ')}
                            </h4>
                          </div>

                          <div className="text-xs text-slate-700 space-y-2">
                            <div>
                              <span className="font-semibold text-slate-900">Milestone: </span>
                              <span>{phase.milestones}</span>
                            </div>
                            <div>
                              <span className="font-semibold text-slate-900">Tasks: </span>
                              <span>{phase.tasks}</span>
                            </div>
                            <div>
                              <span className="font-semibold text-slate-900">Next Action: </span>
                              <span className="text-indigo-600 font-medium">{phase.next_steps}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                </div>
              </div>

            </div>

          </div>
        )}

        {/* Conversation History */}
        {history.length > 0 && (
          <div className="mt-12 rounded-3xl bg-white p-6 sm:p-8 border border-slate-100 shadow-sm">
            <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
              <span>📜</span> Prior Consultations & History
            </h2>

            <div className="space-y-6">
              {history.map((h) => (
                <div key={h.id} className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
                  <div className="flex items-start gap-3 mb-3">
                    <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-bold text-slate-700">User</span>
                    <p className="font-semibold text-slate-900 text-sm sm:text-base">
                      {h.message}
                    </p>
                  </div>

                  <div className="flex items-start gap-3 border-t border-slate-200/60 pt-3">
                    <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-bold text-indigo-700">Agent</span>
                    <div className="text-xs sm:text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                      {h.response}
                    </div>
                  </div>

                  <div className="mt-3 text-right text-[11px] text-slate-400">
                    {new Date(h.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </main>
  )
}