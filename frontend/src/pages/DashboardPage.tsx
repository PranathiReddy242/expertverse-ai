import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { listBookings, cancelBooking } from '../services/bookings'
import api from '../services/api'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { token } = useAuth()
  const [bookings, setBookings] = useState<any[]>([])
  const [chatHistory, setChatHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }

    const fetchData = async () => {
      setLoading(true)
      try {
        const [bookingsData, historyData] = await Promise.all([
          listBookings(),
          api.get('/agents/history').then((r) => r.data).catch(() => []),
        ])
        setBookings(bookingsData)
        setChatHistory(historyData)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Unable to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [token, navigate])

  const handleCancelBooking = async (bookingId: number) => {
    try {
      const updated = await cancelBooking(bookingId)
      setBookings((prev) =>
        prev.map((b) => (b.id === bookingId ? { ...b, status: updated.status } : b))
      )
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel booking')
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <p className="mt-3 text-slate-600">Your personalized space for recent chats, bookings, and action plan tracking.</p>

        {loading ? (
          <div className="mt-8 text-slate-600">Loading your dashboard...</div>
        ) : (
          <div className="mt-8 space-y-6">
            {/* Upcoming Bookings */}
            <div className="rounded-3xl bg-slate-50 p-6">
              <h2 className="font-semibold">Upcoming Bookings</h2>
              {error ? (
                <p className="mt-3 text-sm text-red-600">{error}</p>
              ) : bookings.length === 0 ? (
                <p className="mt-3 text-sm text-slate-600">No bookings found yet.</p>
              ) : (
                <div className="mt-4 space-y-4">
                  {bookings.map((booking) => (
                    <div key={booking.id} className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <p className="text-sm text-slate-500">Booking ID</p>
                          <p className="font-medium">{booking.id}</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-500">Status</p>
                          <p className="font-medium capitalize">{booking.status}</p>
                        </div>
                      </div>
                      <div className="mt-3 grid gap-4 sm:grid-cols-2">
                        <div>
                          <p className="text-sm text-slate-500">Payment</p>
                          <p className="font-medium capitalize">{booking.payment_status}</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-500">Slot</p>
                          <p className="font-medium">{new Date(booking.slot).toLocaleString()}</p>
                        </div>
                      </div>
                      {booking.status !== 'cancelled' && booking.status !== 'completed' && (
                        <button
                          onClick={() => handleCancelBooking(booking.id)}
                          className="mt-4 rounded-full border border-red-300 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                          Cancel Booking
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Chats */}
            <div className="rounded-3xl bg-slate-50 p-6">
              <h2 className="font-semibold">Recent Chats</h2>
              {chatHistory.length === 0 ? (
                <p className="mt-3 text-sm text-slate-600">No conversations yet. Try the AI Chat to get started.</p>
              ) : (
                <div className="mt-4 space-y-3">
                  {chatHistory.slice(0, 5).map((chat: any) => (
                    <div key={chat.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                      <p className="text-sm font-medium text-slate-900 line-clamp-1">Q: {chat.message}</p>
                      <p className="mt-1 text-sm text-slate-600 line-clamp-2">A: {chat.response}</p>
                      <p className="mt-2 text-xs text-slate-400">{new Date(chat.created_at).toLocaleString()}</p>
                    </div>
                  ))}
                  {chatHistory.length > 5 && (
                    <button
                      onClick={() => navigate('/chat')}
                      className="text-sm text-indigo-600 hover:underline"
                    >
                      View all {chatHistory.length} conversations →
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Action Plans */}
            <div className="rounded-3xl bg-slate-50 p-6">
              <h2 className="font-semibold">Action Plans</h2>
              {chatHistory.length === 0 ? (
                <p className="mt-3 text-sm text-slate-600">No action plans yet. Use the AI Chat to generate a personalized roadmap.</p>
              ) : (
                <div className="mt-3">
                  <p className="text-sm text-slate-600">
                    You have <span className="font-semibold text-indigo-600">{chatHistory.length}</span> AI-generated
                    roadmap{chatHistory.length !== 1 ? 's' : ''}. Review your latest recommendations in the{' '}
                    <button onClick={() => navigate('/chat')} className="text-indigo-600 hover:underline">
                      AI Chat
                    </button>
                    .
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
