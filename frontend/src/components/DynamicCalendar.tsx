import { useState, useEffect } from 'react'
import {
  getExpertAvailability,
  getExpertMonthAvailability,
  SlotAvailability,
  MonthAvailabilityResponse,
} from '../services/bookings'

interface DynamicCalendarProps {
  expertId: number
  selectedSlot: string | null
  onSelectSlot: (slotIso: string) => void
}

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

export default function DynamicCalendar({ expertId, selectedSlot, onSelectSlot }: DynamicCalendarProps) {
  const today = new Date()
  const [currentYear, setCurrentYear] = useState(today.getFullYear())
  const [currentMonth, setCurrentMonth] = useState(today.getMonth()) // 0-indexed
  const [selectedDateStr, setSelectedDateStr] = useState<string>(() => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toLocaleDateString('en-CA')
  })

  const [monthData, setMonthData] = useState<MonthAvailabilityResponse | null>(null)
  const [slots, setSlots] = useState<SlotAvailability[]>([])
  const [loadingMonth, setLoadingMonth] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState(false)

  // 1. Fetch month-level availability overview
  useEffect(() => {
    if (!expertId) return
    const fetchMonth = async () => {
      setLoadingMonth(true)
      try {
        const data = await getExpertMonthAvailability(expertId, currentYear, currentMonth + 1)
        setMonthData(data)
      } catch (err) {
        console.error('Failed to load month availability', err)
      } finally {
        setLoadingMonth(false)
      }
    }
    fetchMonth()
  }, [expertId, currentYear, currentMonth])

  // 2. Fetch day-level slot availability when date or expert changes
  useEffect(() => {
    if (!expertId || !selectedDateStr) return
    const fetchSlots = async () => {
      setLoadingSlots(true)
      try {
        const data = await getExpertAvailability(expertId, selectedDateStr)
        setSlots(data.slots || [])
      } catch (err) {
        console.error('Failed to load slots for date', err)
        setSlots([])
      } finally {
        setLoadingSlots(false)
      }
    }
    fetchSlots()
  }, [expertId, selectedDateStr])

  // Calendar calculations
  const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay() // 0 = Sun
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate()

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11)
      setCurrentYear(currentYear - 1)
    } else {
      setCurrentMonth(currentMonth - 1)
    }
  }

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0)
      setCurrentYear(currentYear + 1)
    } else {
      setCurrentMonth(currentMonth + 1)
    }
  }

  const handleDateClick = (day: number) => {
    const mStr = String(currentMonth + 1).padStart(2, '0')
    const dStr = String(day).padStart(2, '0')
    const dateStr = `${currentYear}-${mStr}-${dStr}`
    setSelectedDateStr(dateStr)
  }

  const isDayPast = (day: number) => {
    const d = new Date(currentYear, currentMonth, day)
    const t = new Date()
    t.setHours(0, 0, 0, 0)
    return d < t
  }

  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm border border-slate-200">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Select Date & Time Slot</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time availability calculated against expert working hours and active bookings
          </p>
        </div>

        {/* Month Navigation */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handlePrevMonth}
            aria-label="Previous Month"
            className="rounded-full p-2 text-slate-600 hover:bg-slate-100 transition"
          >
            ←
          </button>
          <span className="min-w-[140px] text-center font-bold text-slate-800 text-sm">
            {MONTH_NAMES[currentMonth]} {currentYear}
          </span>
          <button
            type="button"
            onClick={handleNextMonth}
            aria-label="Next Month"
            className="rounded-full p-2 text-slate-600 hover:bg-slate-100 transition"
          >
            →
          </button>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Calendar Grid (7 cols) */}
        <div className="lg:col-span-7">
          <div className="grid grid-cols-7 text-center text-xs font-semibold text-slate-400 mb-2">
            <span>Su</span>
            <span>Mo</span>
            <span>Tu</span>
            <span>We</span>
            <span>Th</span>
            <span>Fr</span>
            <span>Sa</span>
          </div>

          <div className="grid grid-cols-7 gap-1 text-center text-sm">
            {/* Blank cells for offset */}
            {Array.from({ length: firstDayOfMonth }).map((_, i) => (
              <div key={`blank-${i}`} className="p-2" />
            ))}

            {/* Days of month */}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1
              const past = isDayPast(day)
              const mStr = String(currentMonth + 1).padStart(2, '0')
              const dStr = String(day).padStart(2, '0')
              const dateStr = `${currentYear}-${mStr}-${dStr}`
              const isSelected = selectedDateStr === dateStr

              const dayMeta = monthData?.days?.find(d => d.day === day)
              const hasOpenSlots = dayMeta ? dayMeta.open_slots > 0 : !past

              return (
                <button
                  key={`day-${day}`}
                  type="button"
                  disabled={past}
                  onClick={() => handleDateClick(day)}
                  className={`relative flex flex-col items-center justify-center rounded-2xl py-2.5 px-1 font-medium transition-all ${
                    past
                      ? 'text-slate-300 cursor-not-allowed'
                      : isSelected
                      ? 'bg-indigo-600 text-white font-bold shadow-md'
                      : 'text-slate-800 hover:bg-indigo-50 hover:text-indigo-600'
                  }`}
                >
                  <span>{day}</span>
                  {!past && (
                    <span
                      className={`mt-1 h-1.5 w-1.5 rounded-full ${
                        isSelected
                          ? 'bg-white'
                          : hasOpenSlots
                          ? 'bg-emerald-500'
                          : 'bg-slate-300'
                      }`}
                    />
                  )}
                </button>
              )
            })}
          </div>

          <div className="mt-4 flex items-center justify-between text-[11px] text-slate-500 pt-3 border-t border-slate-100">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500 inline-block" /> Available Dates
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-indigo-600 inline-block" /> Selected Day
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-slate-300 inline-block" /> Past / Unavailable
            </span>
          </div>
        </div>

        {/* Time Slots Column (5 cols) */}
        <div className="lg:col-span-5 bg-slate-50 rounded-2xl p-5 border border-slate-100 flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-slate-800">
              Slots for {selectedDateStr}
            </h3>
            {loadingSlots && (
              <span className="text-[11px] text-indigo-600 animate-pulse font-medium">Checking live...</span>
            )}
          </div>

          {slots.length === 0 && !loadingSlots ? (
            <div className="flex-1 flex items-center justify-center text-center p-6 text-slate-400 text-xs">
              No consultation slots configured for this date.
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2.5 max-h-[300px] overflow-y-auto pr-1">
              {slots.map((slotItem) => {
                const isCurrentSelected = selectedSlot === slotItem.slot
                return (
                  <button
                    key={slotItem.slot}
                    type="button"
                    disabled={!slotItem.available}
                    onClick={() => onSelectSlot(slotItem.slot)}
                    className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      !slotItem.available
                        ? 'bg-slate-200/60 text-slate-400 cursor-not-allowed border border-slate-200'
                        : isCurrentSelected
                        ? 'bg-emerald-600 text-white shadow-sm ring-2 ring-emerald-500 ring-offset-1'
                        : 'bg-white text-slate-700 hover:border-emerald-500 hover:text-emerald-700 border border-slate-200'
                    }`}
                  >
                    <span>{slotItem.time}</span>
                    <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded ${
                      slotItem.booked
                        ? 'bg-red-100 text-red-700 font-bold'
                        : slotItem.past
                        ? 'bg-slate-200 text-slate-500'
                        : isCurrentSelected
                        ? 'bg-emerald-700 text-white'
                        : 'bg-emerald-50 text-emerald-700'
                    }`}>
                      {slotItem.booked ? 'Booked' : slotItem.past ? 'Past' : 'Open'}
                    </span>
                  </button>
                )
              })}
            </div>
          )}

          {selectedSlot && (
            <div className="mt-4 pt-3 border-t border-slate-200 text-xs text-slate-600">
              <span className="font-semibold text-slate-900">Selected Slot:</span>{' '}
              <span className="font-mono text-indigo-600 font-bold">
                {new Date(selectedSlot).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
