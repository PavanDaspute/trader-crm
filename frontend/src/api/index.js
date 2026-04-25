import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Traders ────────────────────────────────────────────────────────────────────
export const fetchTraders = (params = {}) => api.get('/traders/', { params }).then(r => r.data)
export const createTrader = (data) => api.post('/traders/', data).then(r => r.data)
export const updateStatus = (id, status) => api.put(`/traders/${id}/status`, { status }).then(r => r.data)
export const addDeposit = (id, amount) => api.post(`/traders/${id}/deposit`, { amount }).then(r => r.data)

// ─── Stats ──────────────────────────────────────────────────────────────────────
export const fetchOverview = () => api.get('/stats/overview').then(r => r.data)
export const fetchFunnel = () => api.get('/stats/funnel').then(r => r.data)
export const fetchTimeseries = (days = 30) => api.get('/stats/timeseries', { params: { days } }).then(r => r.data)
export const fetchSources = () => api.get('/stats/sources').then(r => r.data)

export default api
