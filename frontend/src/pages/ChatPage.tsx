import { useState, useEffect } from 'react'
import api from '../services/api'

export default function ChatPage() {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const resp = await api.get('/agents/history')
      setHistory(resp.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault()
    setLoading(true)

    try {
      const result = await api.post('/agents/chat', {
        message
      })

      setResponse(result.data)
      setMessage('')
      loadHistory()
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <div className="rounded-3xl bg-white p-10 shadow-lg">

        <h1 className="text-3xl font-semibold">
          AI Chat
        </h1>

        <p className="mt-3 text-slate-600">
          Describe your goals and ExpertVerse AI will recommend experts and generate a roadmap.
        </p>

        <form
          onSubmit={handleSubmit}
          className="mt-8 space-y-4"
        >
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            rows={6}
            className="w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 text-slate-900 outline-none focus:border-indigo-500"
            placeholder="I want to become a Machine Learning Engineer..."
          />

          <button
            type="submit"
            disabled={loading}
            className="rounded-full bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-700"
          >
            {loading ? 'Analyzing...' : 'Submit'}
          </button>
        </form>

        {response && (
          <div className="mt-8 rounded-3xl bg-slate-50 p-6">

            <h2 className="text-xl font-semibold">
              AI Recommendations
            </h2>

            <p className="mt-3 text-slate-700">
              {response.message}
            </p>

            <div className="mt-6 grid gap-6 md:grid-cols-2">

              {/* Recommended Experts */}
              <div className="rounded-2xl bg-white p-5 shadow-sm">
                <h3 className="font-semibold text-lg">
                  Recommended Experts
                </h3>

                <ul className="mt-4 space-y-4">
                  {response.recommended_experts?.map((expert: any) => (
                    <li key={expert.id}>
                      <div className="font-medium">
                        {expert.name}
                      </div>

                      <div className="text-sm text-slate-600">
                        {expert.title}
                      </div>

                      <div className="text-sm text-slate-500">
                        Experience: {expert.experience_years} years
                      </div>

                      <div className="text-sm text-yellow-600">
                        Rating: ⭐ {expert.rating}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Roadmap */}
              <div className="rounded-2xl bg-white p-5 shadow-sm">
                <h3 className="font-semibold text-lg">
                  Roadmap
                </h3>

                {response.roadmap &&
                  Object.entries(response.roadmap)
                    .filter(([key]) => key.startsWith('phase_'))
                    .map(([key, phase]: any) => (
                      <div
                        key={key}
                        className="mt-6 border-b pb-4"
                      >
                        <h4 className="font-semibold text-indigo-600">
                          {key.replace('_', ' ').toUpperCase()}
                        </h4>

                        <div className="mt-3 text-sm text-slate-700">

                          <p>
                            <strong>Milestones</strong>
                          </p>
                          <p className="mb-3">
                            {phase.milestones}
                          </p>

                          <p>
                            <strong>Tasks</strong>
                          </p>
                          <p className="mb-3">
                            {phase.tasks}
                          </p>

                          <p>
                            <strong>Next Steps</strong>
                          </p>
                          <p>
                            {phase.next_steps}
                          </p>

                        </div>
                      </div>
                    ))}
              </div>

            </div>

          </div>
        )}

        {history.length > 0 && (
          <div className="mt-10 rounded-3xl bg-white p-6 shadow-sm">

            <h2 className="text-xl font-semibold">
              Conversation History
            </h2>

            <ul className="mt-5 space-y-4">
              {history.map((h) => (
                <li
                  key={h.id}
                  className="border-b pb-4"
                >
                  <div className="font-medium">
                    Q: {h.message}
                  </div>

                  <div className="mt-2 text-slate-600">
                    A: {h.response}
                  </div>

                  <div className="mt-2 text-xs text-slate-400">
                    {new Date(h.created_at).toLocaleString()}
                  </div>
                </li>
              ))}
            </ul>

          </div>
        )}

      </div>
    </main>
  )
}