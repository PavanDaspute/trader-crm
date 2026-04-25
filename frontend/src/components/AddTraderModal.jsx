import React, { useState, useCallback } from 'react'
import { X, CheckCircle, AlertCircle } from 'lucide-react'
import { createTrader } from '../api'

const SOURCES = ['Telegram', 'Ads', 'Referral', 'Organic', 'Other']

export default function AddTraderModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({ name: '', contact: '', source: 'Telegram' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const trader = await createTrader(form)
      onSuccess(trader)
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to create trader')
    } finally {
      setLoading(false)
    }
  }, [form, onClose, onSuccess])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative glass-card border border-white/10 w-full max-w-md p-6 animate-slide-up">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-white">Add New Trader</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-rose-400 text-sm bg-rose-900/20 border border-rose-800/50 rounded-lg px-3 py-2 mb-4">
            <AlertCircle size={14} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Full Name *
            </label>
            <input
              id="modal-trader-name"
              required
              value={form.name}
              onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="e.g. Alex Johnson"
              className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200
                placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Contact (Email / Phone / Telegram) *
            </label>
            <input
              id="modal-trader-contact"
              required
              value={form.contact}
              onChange={(e) => setForm(f => ({ ...f, contact: e.target.value }))}
              placeholder="e.g. alex@example.com or @alexhandle"
              className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200
                placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Acquisition Source *
            </label>
            <select
              id="modal-trader-source"
              value={form.source}
              onChange={(e) => setForm(f => ({ ...f, source: e.target.value }))}
              className="w-full px-3 py-2 bg-surface-800 border border-white/10 rounded-xl text-sm text-slate-200
                focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30"
            >
              {SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <button
            id="modal-submit-btn"
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500
              disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm rounded-xl
              transition-colors mt-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <CheckCircle size={16} />
            )}
            {loading ? 'Creating...' : 'Add Trader'}
          </button>
        </form>
      </div>
    </div>
  )
}
