import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  getAdminSummary,
  getAdminUsers,
  getAdminExperts,
  getAdminBookings,
  getPendingVerifications,
  approveExpert,
  rejectExpert,
  askAdminAI,
  AdminSummary,
} from '../services/admin'

export default function AdminPage() {
  const navigate = useNavigate()
  const { token, user, loading } = useAuth()
  const [summary, setSummary] = useState<AdminSummary | null>(null)
  const [users, setUsers] = useState<any[]>([])
  const [experts, setExperts] = useState<any[]>([])
  const [bookings, setBookings] = useState<any[]>([])
  const [pendingApps, setPendingApps] = useState<any[]>([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loadingAdmin, setLoadingAdmin] = useState(false)

  // Rejection modal state
  const [rejectingExpertId, setRejectingExpertId] = useState<number | null>(null)
  const [rejectReason, setRejectReason] = useState('')

  // Admin AI assistant state
  const [aiQuery, setAiQuery] = useState('')
  const [aiAnswer, setAiAnswer] = useState('')
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    if (!token) {
      navigate('/login')
    }
  }, [token, navigate])

  const loadAdminData = async () => {
    if (!token || loading || !user?.is_admin) {
      return
    }

    setLoadingAdmin(true)
    setError('')

    try {
      const [summaryData, usersData, expertsData, bookingsData, pendingData] = await Promise.all([
        getAdminSummary(),
        getAdminUsers(),
        getAdminExperts(),
        getAdminBookings(),
        getPendingVerifications(),
      ])

      setSummary(summaryData)
      setUsers(usersData)
      setExperts(expertsData)
      setBookings(bookingsData)
      setPendingApps(pendingData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to load admin data')
    } finally {
      setLoadingAdmin(false)
    }
  }

  useEffect(() => {
    loadAdminData()
  }, [token, user, loading])

  const handleApprove = async (expertId: number) => {
    try {
      const res = await approveExpert(expertId)
      setSuccess(res.message || 'Expert approved successfully')
      setTimeout(() => setSuccess(''), 3000)
      loadAdminData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve expert')
    }
  }

  const handleReject = async () => {
    if (!rejectingExpertId) return
    try {
      const res = await rejectExpert(rejectingExpertId, rejectReason || 'Did not meet verification criteria')
      setSuccess(res.message || 'Expert application rejected')
      setTimeout(() => setSuccess(''), 3000)
      setRejectingExpertId(null)
      setRejectReason('')
      loadAdminData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reject expert')
    }
  }

  const handleAskAI = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!aiQuery.trim()) return
    setAiLoading(true)
    try {
      const result = await askAdminAI(aiQuery)
      setAiAnswer(result.answer)
    } catch (err: any) {
      setAiAnswer('Unable to generate administrative insight at this time.')
    } finally {
      setAiLoading(false)
    }
  }

  if (loading) {
    return <div className="p-8 text-center text-slate-600">Checking credentials...</div>
  }

  if (user && !user.is_admin) {
    return (
      <main className="mx-auto max-w-4xl px-6 py-10">
        <div className="rounded-3xl bg-white p-10 shadow-lg border border-red-100">
          <h1 className="text-3xl font-semibold text-slate-900">Admin Governance</h1>
          <p className="mt-4 text-red-600">Access Restricted: Administrative role privileges required.</p>
        </div>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-10">
      <div className="space-y-8">

        {/* Top Header */}
        <div className="rounded-3xl bg-white p-6 sm:p-8 shadow-sm border border-slate-100 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-purple-50 px-3 py-1 text-xs font-semibold text-purple-700 mb-2">
              <span className="h-2 w-2 rounded-full bg-purple-600"></span>
              Platform Governance & Authority
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Admin Operations Dashboard</h1>
            <p className="mt-1 text-sm text-slate-600">
              Audit expert verifications, oversee user permissions, monitor bookings, and query live platform analytics.
            </p>
          </div>
          <button
            onClick={loadAdminData}
            disabled={loadingAdmin}
            className="self-start md:self-auto rounded-full bg-slate-100 hover:bg-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition"
          >
            {loadingAdmin ? 'Refreshing...' : '↻ Refresh State'}
          </button>
        </div>

        {error && (
          <div className="rounded-2xl bg-red-50 border border-red-200 p-4 text-sm text-red-700 flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => setError('')} className="font-bold text-red-500 hover:text-red-700 ml-2">✕</button>
          </div>
        )}

        {success && (
          <div className="rounded-2xl bg-green-50 border border-green-200 p-4 text-sm text-green-700 flex justify-between items-center">
            <span>✓ {success}</span>
            <button onClick={() => setSuccess('')} className="font-bold text-green-500 hover:text-green-700 ml-2">✕</button>
          </div>
        )}

        {/* Operational Metrics Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: 'Total Users', value: summary?.users ?? 0, color: 'text-slate-900', bg: 'bg-white' },
            { label: 'Verified Experts', value: summary?.approved_experts ?? 0, color: 'text-emerald-700', bg: 'bg-emerald-50/40' },
            { label: 'Pending Review', value: summary?.pending_experts ?? 0, color: 'text-amber-700', bg: 'bg-amber-50/60' },
            { label: 'Total Bookings', value: summary?.bookings ?? 0, color: 'text-indigo-700', bg: 'bg-indigo-50/40' },
            { label: 'Paid Sessions', value: summary?.paid_bookings ?? 0, color: 'text-emerald-700', bg: 'bg-white' },
            { label: 'Platform Revenue', value: `₹${summary?.total_revenue ?? 0}`, color: 'text-slate-900', bg: 'bg-white' },
          ].map((item, idx) => (
            <div key={idx} className={`rounded-2xl p-4 border border-slate-100 shadow-sm ${item.bg}`}>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{item.label}</p>
              <p className={`mt-2 text-2xl font-bold ${item.color}`}>{item.value}</p>
            </div>
          ))}
        </div>

        {/* Action Required: Pending Verifications Queue */}
        <section className="rounded-3xl bg-white p-6 sm:p-8 shadow-sm border border-slate-100">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span className="flex h-3 w-3 rounded-full bg-amber-500 animate-pulse"></span>
                Action Required: Pending Expert Verifications ({pendingApps.length})
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Applicants must be approved by an administrator before their profile and calendar become publicly active.
              </p>
            </div>
          </div>

          {pendingApps.length === 0 ? (
            <div className="rounded-2xl bg-slate-50 p-8 text-center text-sm text-slate-500">
              ✓ Verification queue is clear. No pending applications awaiting review.
            </div>
          ) : (
            <div className="space-y-4">
              {pendingApps.map((app) => (
                <div key={app.expert_id} className="rounded-2xl border border-amber-200/80 bg-amber-50/20 p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-bold text-slate-900 text-base">{app.name}</h3>
                      <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-800 border border-amber-300">
                        {app.verification_status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-slate-700">{app.title} • {app.company || 'Independent'}</p>
                    <p className="text-xs text-slate-500">
                      Experience: {app.experience_years} years | Rate: ₹{app.hourly_rate}/hr | Email: {app.email}
                    </p>
                    {app.skills && (
                      <p className="text-xs text-slate-600">
                        <span className="font-semibold">Skills:</span> {app.skills}
                      </p>
                    )}
                    {app.rejection_reason && (
                      <p className="text-xs text-red-600 bg-red-50 p-2 rounded-lg mt-1">
                        <span className="font-semibold">Previous Note:</span> {app.rejection_reason}
                      </p>
                    )}

                    {/* Supporting Documents & Links */}
                    <div className="flex flex-wrap gap-2 pt-2">
                      {app.linkedin_url && (
                        <a href={app.linkedin_url} target="_blank" rel="noreferrer" className="text-xs bg-white border border-slate-200 px-2.5 py-1 rounded-lg text-indigo-600 hover:underline">
                          🔗 LinkedIn Profile
                        </a>
                      )}
                      {app.certificate_url && (
                        <a href={app.certificate_url} target="_blank" rel="noreferrer" className="text-xs bg-white border border-slate-200 px-2.5 py-1 rounded-lg text-indigo-600 hover:underline">
                          📜 Certificate URL
                        </a>
                      )}
                      {app.documents && app.documents.map((doc: any) => (
                        <span key={doc.id} className="text-xs bg-white border border-slate-200 px-2 py-1 rounded-lg text-slate-600">
                          📄 {doc.title} ({doc.file_type})
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-2 md:pt-0 self-end md:self-center">
                    <button
                      onClick={() => handleApprove(app.expert_id)}
                      className="rounded-full bg-emerald-600 hover:bg-emerald-700 px-4 py-2 text-xs font-bold text-white shadow-sm transition"
                    >
                      Approve Expert
                    </button>
                    <button
                      onClick={() => {
                        setRejectingExpertId(app.expert_id)
                        setRejectReason('')
                      }}
                      className="rounded-full bg-red-50 hover:bg-red-100 border border-red-200 px-4 py-2 text-xs font-bold text-red-700 transition"
                    >
                      Reject...
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Admin AI Assistant Section */}
        <section className="rounded-3xl bg-gradient-to-r from-slate-900 to-indigo-950 p-6 sm:p-8 text-white shadow-lg">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-indigo-500/20 px-3 py-1 text-xs font-semibold text-indigo-300 mb-3 border border-indigo-500/30">
              🤖 Admin AI Intelligence Agent
            </div>
            <h2 className="text-xl sm:text-2xl font-bold">Query Live Platform Intelligence</h2>
            <p className="mt-1 text-xs sm:text-sm text-indigo-200">
              Ask questions regarding platform operations, pending applicant workloads, revenue, and active domain distributions.
            </p>

            <form onSubmit={handleAskAI} className="mt-5 flex gap-2">
              <input
                type="text"
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                placeholder="e.g. 'What is our pending verification workload and revenue summary?'"
                className="flex-1 rounded-2xl bg-white/10 border border-white/20 px-4 py-2.5 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:border-indigo-400"
              />
              <button
                type="submit"
                disabled={aiLoading || !aiQuery.trim()}
                className="rounded-2xl bg-indigo-500 hover:bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50 transition"
              >
                {aiLoading ? 'Analyzing...' : 'Ask AI'}
              </button>
            </form>

            <div className="flex flex-wrap gap-2 mt-3">
              {[
                'How many experts are waiting for verification?',
                'Summarize platform users, bookings, and revenue.',
                'What are our action items for today?',
              ].map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setAiQuery(q)
                  }}
                  className="text-[11px] bg-white/5 hover:bg-white/15 px-2.5 py-1 rounded-full text-indigo-200 border border-white/10 transition"
                >
                  💡 {q}
                </button>
              ))}
            </div>

            {aiAnswer && (
              <div className="mt-5 rounded-2xl bg-white/10 border border-white/15 p-4 text-sm text-slate-100 whitespace-pre-line leading-relaxed">
                {aiAnswer}
              </div>
            )}
          </div>
        </section>

        {/* Experts Directory (All Statuses) */}
        <section className="rounded-3xl bg-white p-6 sm:p-8 shadow-sm border border-slate-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-slate-900">All Registered Experts ({experts.length})</h2>
            <span className="text-xs text-slate-500">Includes Verified, Pending, and Rejected Profiles</span>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Expert Name</th>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Rate</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {experts.map((exp) => (
                  <tr key={exp.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{exp.id}</td>
                    <td className="px-4 py-3 font-semibold text-slate-900">{exp.name}</td>
                    <td className="px-4 py-3 text-slate-700">{exp.title}</td>
                    <td className="px-4 py-3 font-medium">₹{exp.hourly_rate}/hr</td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        exp.is_verified
                          ? 'bg-emerald-100 text-emerald-800'
                          : exp.verification_status === 'rejected'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {exp.is_verified ? 'Verified' : exp.verification_status?.toUpperCase() || 'PENDING'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {!exp.is_verified ? (
                        <button
                          onClick={() => handleApprove(exp.id)}
                          className="text-xs font-bold text-emerald-600 hover:text-emerald-800 mr-3"
                        >
                          Approve
                        </button>
                      ) : (
                        <button
                          onClick={() => {
                            setRejectingExpertId(exp.id)
                            setRejectReason('Revoked by administrator')
                          }}
                          className="text-xs font-bold text-red-600 hover:text-red-800"
                        >
                          Revoke
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Users Management */}
        <section className="rounded-3xl bg-white p-6 sm:p-8 shadow-sm border border-slate-100">
          <h2 className="text-lg font-bold text-slate-900 mb-4">User Accounts ({users.length})</h2>
          <div className="overflow-x-auto rounded-2xl border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Roles</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{u.id}</td>
                    <td className="px-4 py-3 font-semibold text-slate-900">{u.name}</td>
                    <td className="px-4 py-3 text-slate-600">{u.email}</td>
                    <td className="px-4 py-3">
                      {[
                        u.is_admin ? <span key="adm" className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full text-xs font-bold mr-1">Admin</span> : null,
                        u.is_expert ? <span key="exp" className="bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full text-xs font-bold mr-1">Expert</span> : null,
                        u.is_learner ? <span key="lrn" className="bg-slate-100 text-slate-800 px-2 py-0.5 rounded-full text-xs font-bold">Learner</span> : null,
                      ]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Bookings & Sessions */}
        <section className="rounded-3xl bg-white p-6 sm:p-8 shadow-sm border border-slate-100">
          <h2 className="text-lg font-bold text-slate-900 mb-4">Platform Bookings & Consultations ({bookings.length})</h2>
          <div className="overflow-x-auto rounded-2xl border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Learner</th>
                  <th className="px-4 py-3">Expert</th>
                  <th className="px-4 py-3">Slot</th>
                  <th className="px-4 py-3">Booking Status</th>
                  <th className="px-4 py-3">Payment</th>
                  <th className="px-4 py-3">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {bookings.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">#{b.id}</td>
                    <td className="px-4 py-3 font-semibold text-slate-900">{b.learner || `User ${b.user_id}`}</td>
                    <td className="px-4 py-3 text-slate-700">{b.expert || `Expert ${b.expert_id}`}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">{new Date(b.slot).toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        b.status === 'confirmed' || b.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : b.status === 'cancelled'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {b.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        b.payment_status === 'paid'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {b.payment_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-900">₹{b.amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

      </div>

      {/* Rejection Modal */}
      {rejectingExpertId && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-slate-100 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Decline / Reject Verification</h3>
            <p className="text-xs text-slate-600">
              Provide specific feedback for why this application does not currently meet verification criteria. The applicant will see this note to correct and resubmit.
            </p>
            <textarea
              rows={3}
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="e.g. Insufficient verified portfolio links provided; please attach GitHub profile."
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-900 outline-none focus:border-red-500"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setRejectingExpertId(null)}
                className="rounded-full bg-slate-100 hover:bg-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="rounded-full bg-red-600 hover:bg-red-700 px-5 py-2 text-xs font-bold text-white transition shadow-sm"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
