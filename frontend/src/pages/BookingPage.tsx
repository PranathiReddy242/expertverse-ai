import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  createBooking,
  createPaymentOrder,
  verifyPayment,
  confirmUpiPayment,
  reportPaymentFailure,
  demoConfirmPayment,
} from '../services/bookings'
import { getExperts } from '../services/experts'
import DynamicCalendar from '../components/DynamicCalendar'

declare global {
  interface Window {
    Razorpay?: any
  }
}

const loadRazorpayScript = () => {
  return new Promise<boolean>((resolve) => {
    if (window.Razorpay) {
      return resolve(true)
    }

    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.body.appendChild(script)
  })
}

export default function BookingPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { token } = useAuth()

  const [experts, setExperts] = useState<any[]>([])
  const [selectedExpertId, setSelectedExpertId] = useState<number>(() => {
    const fromUrl = searchParams.get('expert_id')
    return fromUrl ? parseInt(fromUrl, 10) : 2
  })

  const [selectedSlot, setSelectedSlot] = useState<string | null>(null)
  const [notes, setNotes] = useState('')
  const [booking, setBooking] = useState<any>(null)
  const [error, setError] = useState('')
  const [conflictSlots, setConflictSlots] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [paymentLoading, setPaymentLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState(false)
  const [paymentSuccess, setPaymentSuccess] = useState(false)
  const [paymentOrder, setPaymentOrder] = useState<any>(null)

  const [paymentTab, setPaymentTab] = useState<'upi' | 'razorpay' | 'demo'>('upi')
  const [upiUtr, setUpiUtr] = useState('')
  const [upiConfirming, setUpiConfirming] = useState(false)
  const [copiedUpi, setCopiedUpi] = useState(false)

  useEffect(() => {
    if (!token) {
      navigate('/login')
    }
  }, [token, navigate])

  // Load verified experts for dropdown
  useEffect(() => {
    const loadExperts = async () => {
      try {
        const data = await getExperts()
        setExperts(data)
        if (data.length > 0 && !searchParams.get('expert_id')) {
          setSelectedExpertId(data[0].id)
        }
      } catch (err) {
        console.error('Failed to load experts', err)
      }
    }
    loadExperts()
  }, [searchParams])

  const currentExpert = experts.find(e => e.id === selectedExpertId) || experts[0]

  const handleCreateBooking = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedSlot) {
      setError('Please select an available date and time slot from the calendar.')
      return
    }

    setLoading(true)
    setError('')
    setConflictSlots([])

    try {
      const resp = await createBooking({
        expert_id: selectedExpertId,
        slot: selectedSlot,
      })
      setBooking(resp)
      setPaymentSuccess(false)

      try {
        const order = await createPaymentOrder(resp.id)
        setPaymentOrder(order)
        if (order.is_razorpay_configured) {
          setPaymentTab('razorpay')
        } else {
          setPaymentTab('upi')
        }
      } catch (orderErr) {
        console.error('Failed to pre-generate payment order', orderErr)
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (err.response?.status === 409) {
        setError(detail || 'This slot is already booked. Please choose an alternate slot.')
        if (typeof detail === 'string' && detail.includes('Nearest available slots today:')) {
          const suggestions = detail.split('Nearest available slots today:')[1].replace('.', '').split(',')
          setConflictSlots(suggestions.map((s: string) => s.trim()).filter(Boolean))
        }
      } else {
        setError(typeof detail === 'string' ? detail : 'Booking failed. Please select another slot.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePayment = async () => {
    if (!booking) return
    setPaymentLoading(true)
    setError('')
    try {
      let order = paymentOrder
      if (!order) {
        order = await createPaymentOrder(booking.id)
        setPaymentOrder(order)
      }

      if (!order.is_razorpay_configured || !order.key_id || order.key_id === 'rzp_test_demo_key') {
        setError('Razorpay Live API keys are not configured in backend/.env. Please use the Direct UPI / QR Code option below to pay directly to the verified UPI ID.')
        setPaymentTab('upi')
        return
      }

      const loaded = await loadRazorpayScript()
      if (!loaded) {
        setError('Unable to load Razorpay checkout. Please try Direct UPI payment below.')
        return
      }

      const options = {
        key: order.key_id,
        amount: order.amount * 100,
        currency: order.currency,
        name: 'ExpertVerse AI',
        description: `Consultation session with ${currentExpert?.user?.name || 'Expert'}`,
        order_id: order.order_id,
        handler: async (response: any) => {
          try {
            const verifyRes = await verifyPayment(booking.id, {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            })
            setPaymentSuccess(true)
            setBooking({
              ...booking,
              payment_status: 'paid',
              status: 'confirmed',
              meeting_link: verifyRes.meeting_link || `https://meet.jit.si/expertverse-${booking.id}-${booking.expert_id}`,
            })
          } catch (verifyError: any) {
            setError(verifyError.response?.data?.detail || 'Payment verification failed.')
          }
        },
        modal: {
          ondismiss: async () => {
            await reportPaymentFailure(booking.id)
          },
        },
      }

      const rzp = new window.Razorpay(options)
      rzp.open()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Payment initialization failed. You can use Direct UPI payment below.')
    } finally {
      setPaymentLoading(false)
    }
  }

  const handleUpiConfirm = async () => {
    if (!booking) return
    setUpiConfirming(true)
    setError('')
    try {
      const res = await confirmUpiPayment(booking.id, {
        upi_id: paymentOrder?.merchant_upi_id,
        utr_number: upiUtr,
      })
      setPaymentSuccess(true)
      setBooking({
        ...booking,
        payment_status: 'paid',
        status: 'confirmed',
        meeting_link: res.meeting_link || `https://meet.jit.si/expertverse-${booking.id}-${booking.expert_id}`,
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'UPI payment verification failed.')
    } finally {
      setUpiConfirming(false)
    }
  }

  const handleCopyUpi = () => {
    const upiId = paymentOrder?.merchant_upi_id || 'expertverse@upi'
    navigator.clipboard.writeText(upiId)
    setCopiedUpi(true)
    setTimeout(() => setCopiedUpi(false), 2000)
  }

  const handleDemoConfirm = async () => {
    if (!booking) return
    setDemoLoading(true)
    setError('')
    try {
      const res = await demoConfirmPayment(booking.id)
      setPaymentSuccess(true)
      setBooking({
        ...booking,
        payment_status: 'paid',
        status: 'confirmed',
        meeting_link: res.meeting_link || `https://meet.jit.si/expertverse-${booking.id}-${booking.expert_id}`,
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Demo payment confirmation failed.')
    } finally {
      setDemoLoading(false)
    }
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
            Book 1-on-1 Consultation
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Schedule live architectural mentorship and code reviews with verified domain leaders
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3.5 py-1 text-xs font-semibold text-emerald-700 border border-emerald-200">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          Conflict-Free Real-Time Booking
        </span>
      </div>

      {/* Expert Selection Header Card */}
      <div className="mt-8 rounded-3xl bg-white p-6 shadow-sm border border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex-1">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            Select Verified Expert
          </label>
          <select
            value={selectedExpertId}
            onChange={(e) => {
              setSelectedExpertId(Number(e.target.value))
              setSelectedSlot(null)
              setBooking(null)
            }}
            className="w-full md:w-96 rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm font-semibold text-slate-800 outline-none focus:border-indigo-500"
          >
            {experts.map((exp) => (
              <option key={exp.id} value={exp.id}>
                {exp.user?.name || 'Expert'} — {exp.title} (₹{exp.hourly_rate}/hr)
              </option>
            ))}
          </select>
        </div>

        {currentExpert && (
          <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-100">
            <div>
              <p className="text-sm font-bold text-slate-900">{currentExpert.user?.name}</p>
              <p className="text-xs text-indigo-600 font-medium">{currentExpert.title}</p>
              <p className="text-xs text-slate-500">{currentExpert.company} • ★ {currentExpert.rating?.toFixed(1) || '5.0'}</p>
            </div>
            <div className="text-right pl-4 border-l border-slate-200">
              <p className="text-xs text-slate-400">Fee</p>
              <p className="text-lg font-black text-slate-900">₹{currentExpert.hourly_rate}<span className="text-xs font-normal text-slate-500">/hr</span></p>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Calendar & Real-Time Availability Grid */}
      <div className="mt-8">
        <DynamicCalendar
          expertId={selectedExpertId}
          selectedSlot={selectedSlot}
          onSelectSlot={(slotIso) => {
            setSelectedSlot(slotIso)
            setError('')
            setConflictSlots([])
          }}
        />
      </div>

      {/* Conflict / Error Alert with Nearest Slot Buttons */}
      {error && (
        <div className="mt-6 rounded-2xl bg-red-50 border border-red-200 p-5 text-sm text-red-800">
          <p className="font-semibold">⚠️ {error}</p>
          {conflictSlots.length > 0 && (
            <div className="mt-3 pt-3 border-t border-red-200/60">
              <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Click to switch to nearest available time:
              </p>
              <div className="flex flex-wrap gap-2">
                {conflictSlots.map((timeStr, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      if (selectedSlot) {
                        const datePart = selectedSlot.split('T')[0]
                        setSelectedSlot(`${datePart}T${timeStr}:00`)
                        setError('')
                        setConflictSlots([])
                      }
                    }}
                    className="rounded-xl bg-white border border-red-300 px-3 py-1.5 text-xs font-bold text-red-800 hover:bg-red-100 shadow-sm"
                  >
                    ⏰ Switch to {timeStr}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Confirmation Form */}
      <form onSubmit={handleCreateBooking} className="mt-8 rounded-3xl bg-white p-6 shadow-sm border border-slate-100 space-y-4">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
            Session Agenda / Learner Notes (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g. Architecture review of our microservices event-driven ingestion pipeline..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-3.5 text-sm outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-slate-500">
            {selectedSlot ? (
              <span>Selected Time: <strong className="text-slate-900">{new Date(selectedSlot).toLocaleString()}</strong></span>
            ) : (
              <span>Please pick a slot on the calendar above</span>
            )}
          </div>

          <button
            type="submit"
            disabled={!selectedSlot || loading}
            className="rounded-full bg-indigo-600 px-7 py-3 text-sm font-bold text-white hover:bg-indigo-700 disabled:opacity-40 shadow-sm transition"
          >
            {loading ? 'Reserving Slot...' : 'Reserve Session Slot'}
          </button>
        </div>
      </form>

      {/* Booking Created & Payment Card */}
      {booking && (
        <div className="mt-8 rounded-3xl bg-slate-900 text-white p-8 shadow-xl border border-slate-800 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-5">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400">Reservation Confirmed</span>
              <h2 className="text-2xl font-bold mt-0.5">Booking #{booking.id}</h2>
            </div>
            <span className={`rounded-full px-3.5 py-1 text-xs font-extrabold uppercase tracking-wider ${
              booking.status === 'confirmed' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
            }`}>
              {booking.status}
            </span>
          </div>

          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-2xl bg-white/5 p-4 border border-white/10">
              <p className="text-xs text-slate-400">Expert</p>
              <p className="text-sm font-bold mt-1">{currentExpert?.user?.name}</p>
            </div>
            <div className="rounded-2xl bg-white/5 p-4 border border-white/10">
              <p className="text-xs text-slate-400">Scheduled Time</p>
              <p className="text-xs font-bold mt-1 text-indigo-300">{new Date(booking.slot).toLocaleString()}</p>
            </div>
            <div className="rounded-2xl bg-white/5 p-4 border border-white/10">
              <p className="text-xs text-slate-400">Amount</p>
              <p className="text-sm font-black mt-1 text-emerald-400">₹{booking.amount}</p>
            </div>
            <div className="rounded-2xl bg-white/5 p-4 border border-white/10">
              <p className="text-xs text-slate-400">Payment Status</p>
              <p className="text-sm font-bold mt-1 capitalize text-amber-300">{booking.payment_status}</p>
            </div>
          </div>

          {booking.payment_status !== 'paid' ? (
            <div className="mt-8 pt-6 border-t border-slate-800">
              {/* Payment Method Tabs */}
              <div className="flex flex-wrap gap-2 mb-6">
                <button
                  type="button"
                  onClick={() => setPaymentTab('upi')}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition ${
                    paymentTab === 'upi'
                      ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
                      : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/10'
                  }`}
                >
                  <span>⚡</span>
                  <span>Direct UPI & QR Code</span>
                  <span className="ml-1 text-[10px] bg-slate-950/20 px-2 py-0.5 rounded-full font-extrabold">Instant</span>
                </button>

                <button
                  type="button"
                  onClick={() => setPaymentTab('razorpay')}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition ${
                    paymentTab === 'razorpay'
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                      : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/10'
                  }`}
                >
                  <span>💳</span>
                  <span>Razorpay Gateway</span>
                  <span className="ml-1 text-[10px] bg-white/20 px-2 py-0.5 rounded-full">Cards / Netbanking</span>
                </button>

                <button
                  type="button"
                  onClick={() => setPaymentTab('demo')}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition ${
                    paymentTab === 'demo'
                      ? 'bg-slate-700 text-white'
                      : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/10'
                  }`}
                >
                  <span>🧪</span>
                  <span>Academic Demo Fast-Track</span>
                </button>
              </div>

              {/* Tab 1: Direct UPI & QR Code */}
              {paymentTab === 'upi' && (
                <div className="rounded-2xl bg-white/[0.03] border border-emerald-500/30 p-6">
                  <div className="flex flex-col md:flex-row items-center gap-6">
                    {/* QR Code Container */}
                    <div className="flex flex-col items-center bg-white p-4 rounded-2xl shadow-xl text-slate-900">
                      {paymentOrder?.qr_code_url ? (
                        <img
                          src={paymentOrder.qr_code_url}
                          alt="UPI Payment QR Code"
                          className="w-48 h-48 rounded-xl object-contain"
                        />
                      ) : (
                        <div className="w-48 h-48 flex items-center justify-center text-xs text-slate-400">
                          Generating QR...
                        </div>
                      )}
                      <div className="mt-2 text-center">
                        <span className="inline-block text-[11px] font-black tracking-wider text-emerald-700 uppercase">Scan with Any UPI App</span>
                        <p className="text-[10px] text-slate-500 font-medium">GPay • PhonePe • Paytm • BHIM</p>
                      </div>
                    </div>

                    {/* UPI Details & Actions */}
                    <div className="flex-1 space-y-4 w-full">
                      <div>
                        <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">Direct UPI Transfer (0% Platform Fee)</span>
                        <h3 className="text-xl font-black text-white mt-1">Pay ₹{booking.amount} Directly</h3>
                        <p className="text-xs text-slate-400 mt-1">
                          Funds transfer immediately to the merchant UPI ID. Scan the QR code or tap the deep link below.
                        </p>
                      </div>

                      {/* Merchant UPI ID & Razorpay.me Info Box */}
                      <div className="bg-black/40 border border-emerald-500/30 rounded-xl p-3.5 space-y-2">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-[10px] font-bold text-slate-400 uppercase">Receiver: Pranathi Tarigonda</p>
                            <p className="text-sm font-mono font-bold text-emerald-300 mt-0.5 select-all">
                              {paymentOrder?.merchant_upi_id || 'pranathitarigonda@razorpay'}
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={handleCopyUpi}
                            className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-xs font-bold transition flex items-center gap-1.5"
                          >
                            <span>📋</span>
                            <span>{copiedUpi ? 'Copied!' : 'Copy'}</span>
                          </button>
                        </div>

                        {paymentOrder?.merchant_payment_url && (
                          <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs">
                            <span className="text-slate-400">Direct Razorpay Page:</span>
                            <a
                              href={paymentOrder.merchant_payment_url}
                              target="_blank"
                              rel="noreferrer"
                              className="font-mono text-indigo-400 hover:text-indigo-300 underline text-[11px]"
                            >
                              razorpay.me/@pranathitarigonda ↗
                            </a>
                          </div>
                        )}
                      </div>

                      {/* Payment Action Buttons */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {paymentOrder?.merchant_payment_url && (
                          <a
                            href={paymentOrder.merchant_payment_url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-3.5 py-2.5 text-xs font-black text-white hover:brightness-110 shadow-lg shadow-indigo-500/20 transition text-center"
                          >
                            <span>🔗</span>
                            <span>Open Razorpay.me</span>
                          </a>
                        )}

                        {paymentOrder?.upi_link && (
                          <a
                            href={paymentOrder.upi_link}
                            className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-3.5 py-2.5 text-xs font-black text-slate-950 hover:brightness-110 shadow-lg shadow-emerald-500/20 transition text-center"
                          >
                            <span>📱</span>
                            <span>Open in UPI App</span>
                          </a>
                        )}
                      </div>

                      {/* UTR Verification Input */}
                      <div className="pt-2 border-t border-white/10 space-y-2">
                        <label className="text-[11px] font-medium text-slate-300 block">
                          Enter 12-Digit UPI Reference ID / UTR (Optional for instant validation):
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={upiUtr}
                            onChange={(e) => setUpiUtr(e.target.value)}
                            placeholder="e.g. 423859201948"
                            className="flex-1 rounded-xl bg-black/40 border border-white/15 px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                          />
                          <button
                            type="button"
                            onClick={handleUpiConfirm}
                            disabled={upiConfirming}
                            className="px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs shadow-md transition disabled:opacity-50 whitespace-nowrap"
                          >
                            {upiConfirming ? 'Verifying...' : '✓ Confirm Payment'}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Razorpay Gateway */}
              {paymentTab === 'razorpay' && (
                <div className="rounded-2xl bg-white/[0.03] border border-white/10 p-6 space-y-4">
                  <div>
                    <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">Online Payment Gateway</span>
                    <h3 className="text-xl font-bold text-white mt-1">Razorpay Checkout</h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Accepts Credit Cards, Debit Cards, NetBanking, Wallets, and Razorpay UPI.
                    </p>
                  </div>

                  {!paymentOrder?.is_razorpay_configured ? (
                    <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-4 text-xs text-amber-200">
                      <p className="font-bold flex items-center gap-1.5">
                        <span>ℹ️</span>
                        <span>Razorpay API Keys Not Detected in .env</span>
                      </p>
                      <p className="mt-1 text-slate-300">
                        To enable the live Razorpay popup, add your <code className="text-amber-300 font-mono">RAZORPAY_KEY_ID</code> and <code className="text-amber-300 font-mono">RAZORPAY_KEY_SECRET</code> into <code className="text-amber-300 font-mono">backend/.env</code>.
                      </p>
                      <p className="mt-2 text-emerald-300 font-semibold">
                        👉 In the meantime, use the <strong>Direct UPI & QR Code</strong> tab above to pay directly!
                      </p>
                    </div>
                  ) : null}

                  <button
                    type="button"
                    onClick={handlePayment}
                    disabled={paymentLoading}
                    className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-bold text-white hover:bg-indigo-500 disabled:opacity-50 shadow-md transition flex items-center gap-2"
                  >
                    <span>💳</span>
                    <span>{paymentLoading ? 'Opening Razorpay...' : `Pay ₹${booking.amount} with Razorpay`}</span>
                  </button>
                </div>
              )}

              {/* Tab 3: Academic Demo Fast-Track */}
              {paymentTab === 'demo' && (
                <div className="rounded-2xl bg-white/[0.03] border border-white/10 p-6 space-y-4">
                  <div>
                    <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">Evaluation Mode</span>
                    <h3 className="text-xl font-bold text-white mt-1">Instant Session Confirmation</h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Instantly mark booking #{booking.id} as paid and generate your live consultation link without processing actual currency.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={handleDemoConfirm}
                    disabled={demoLoading}
                    className="rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-3 text-sm font-bold text-white hover:brightness-110 disabled:opacity-50 shadow-md transition flex items-center gap-2"
                  >
                    <span>⚡</span>
                    <span>{demoLoading ? 'Confirming...' : 'Instant Confirm (Academic Demo)'}</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="mt-6 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 p-4">
              <p className="text-sm font-bold text-emerald-300">✓ Consultation Session Scheduled & Confirmed!</p>
              <p className="text-xs text-slate-300 mt-1">
                Your video consultation link is active: <a href={booking.meeting_link || '#'} target="_blank" rel="noreferrer" className="text-indigo-400 underline">{booking.meeting_link}</a>
              </p>
            </div>
          )}

          {paymentOrder && (
            <p className="mt-4 text-xs text-slate-500">
              Razorpay Order ID: <span className="font-mono text-slate-400">{paymentOrder.order_id}</span>
            </p>
          )}
        </div>
      )}
    </main>
  )
}
