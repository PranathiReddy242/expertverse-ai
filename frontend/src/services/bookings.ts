import api from './api'

export interface BookingCreatePayload {
  expert_id: number
  slot: string
}

export interface BookingResponse {
  id: number
  expert_id: number
  slot: string
  status: string
  payment_status: string
  amount: number
}

export interface RazorpayOrderResponse {
  booking_id: number
  order_id: string
  amount: number
  currency: string
  key_id: string
  merchant_upi_id?: string
  merchant_payment_url?: string
  upi_link?: string
  qr_code_url?: string
  is_razorpay_configured?: boolean
}

export interface RazorpayVerifyPayload {
  razorpay_order_id: string
  razorpay_payment_id: string
  razorpay_signature: string
}

export interface UpiConfirmPayload {
  upi_id?: string
  utr_number?: string
  transaction_id?: string
}

export const createBooking = async (payload: BookingCreatePayload) => {
  const response = await api.post('/bookings/create', payload)
  return response.data as BookingResponse
}

export const createPaymentOrder = async (bookingId: number) => {
  const response = await api.post<RazorpayOrderResponse>(`/bookings/${bookingId}/payment/create-order`)
  return response.data as RazorpayOrderResponse
}

export const verifyPayment = async (bookingId: number, payload: RazorpayVerifyPayload) => {
  const response = await api.post(`/bookings/${bookingId}/payment/verify`, payload)
  return response.data
}

export const confirmUpiPayment = async (bookingId: number, payload?: UpiConfirmPayload) => {
  const response = await api.post(`/bookings/${bookingId}/payment/upi-confirm`, payload || {})
  return response.data
}

export const reportPaymentFailure = async (bookingId: number) => {
  const response = await api.post(`/bookings/${bookingId}/payment/failure`)
  return response.data
}

export const listBookings = async () => {
  const response = await api.get<BookingResponse[]>('/bookings/list')
  return response.data
}

export const cancelBooking = async (bookingId: number) => {
  const response = await api.post<BookingResponse>(`/bookings/cancel/${bookingId}`)
  return response.data
}

export const demoConfirmPayment = async (bookingId: number) => {
  const response = await api.post(`/bookings/${bookingId}/payment/demo-confirm`)
  return response.data
}

export interface SlotAvailability {
  time: string
  slot: string
  available: boolean
  booked: boolean
  past: boolean
}

export interface ExpertAvailabilityResponse {
  expert_id: number
  expert_name: string
  date: string
  working_hours: string
  total_slots: number
  available_count: number
  slots: SlotAvailability[]
}

export const getExpertAvailability = async (expertId: number, date?: string) => {
  const params: any = {}
  if (date) params.date = date
  const response = await api.get<ExpertAvailabilityResponse>(`/bookings/availability/${expertId}`, { params })
  return response.data
}

export interface MonthAvailabilityResponse {
  expert_id: number
  year: number
  month: number
  days: Array<{
    date: string
    day: number
    available: boolean
    open_slots: number
    is_past: boolean
  }>
}

export const getExpertMonthAvailability = async (expertId: number, year?: number, month?: number) => {
  const params: any = {}
  if (year) params.year = year
  if (month) params.month = month
  const response = await api.get<MonthAvailabilityResponse>(`/bookings/availability/${expertId}/month`, { params })
  return response.data
}

