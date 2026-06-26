import { useState } from 'react'
import api from '../services/api'

export default function BookingPage() {
  const [expertId, setExpertId] = useState('1')
  const [date, setDate] = useState('2026-06-20')
  const [time, setTime] = useState('10:00')
  const [booking, setBooking] = useState<any>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const slot = new Date(`${date}T${time}`).toISOString()
      const response = await api.post('/bookings/create', { expert_id: Number(expertId), slot })
      setBooking(response.data)
      setExpertId('1')
      setDate('2026-06-20')
      setTime('10:00')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Booking failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="rounded-3xl bg-white p-10 shadow-lg">
        <h1 className="text-3xl font-semibold">Book an Expert Session</h1>
        <p className="mt-2 text-slate-600">Schedule a one-on-one consultation</p>
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Expert ID</span>
              <input
                type="number"
                value={expertId}
                onChange={(event) => setExpertId(event.target.value)}
                className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                required
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Date</span>
              <input
                type="date"
                value={date}
                onChange={(event) => setDate(event.target.value)}
                className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                required
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Time</span>
              <input
                type="time"
                value={time}
                onChange={(event) => setTime(event.target.value)}
                className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                required
              />
            </label>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button disabled={loading} className="rounded-full bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-700 disabled:opacity-50">
            {loading ? 'Booking...' : 'Confirm Booking'}
          </button>
        </form>
        {booking && (
          <div className="mt-8 rounded-3xl bg-green-50 p-6 border border-green-200">
            <h2 className="text-xl font-semibold text-green-900">✓ Booking Confirmed</h2>
            <p className="mt-3 text-green-800">Booking ID: <span className="font-mono">{booking.id}</span></p>
            <p className="mt-1 text-sm text-green-700">Status: {booking.status}</p>
            <p className="mt-2 text-sm text-green-700">Slot: {new Date(booking.slot).toLocaleString()}</p>
          </div>
        )}
      </div>
    </main>
  )
}

