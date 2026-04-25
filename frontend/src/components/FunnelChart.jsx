import React from 'react'
import { ArrowRight } from 'lucide-react'

const STAGE_COLORS = {
  new:        { bar: 'bg-slate-500',  text: 'text-slate-300',  border: 'border-slate-600' },
  registered: { bar: 'bg-blue-500',   text: 'text-blue-300',   border: 'border-blue-600'  },
  funded:     { bar: 'bg-amber-500',  text: 'text-amber-300',  border: 'border-amber-600' },
  active:     { bar: 'bg-green-500',  text: 'text-green-300',  border: 'border-green-600' },
}

export default function FunnelChart({ funnel, loading }) {
  const max = funnel ? Math.max(...funnel.map((s) => s.count), 1) : 1

  if (loading) {
    return (
      <div className="chart-container">
        <p className="section-title">Trader Lifecycle Funnel</p>
        <div className="space-y-4 mt-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="chart-container">
      <p className="section-title">Trader Lifecycle Funnel</p>
      <div className="space-y-3 mt-2">
        {(funnel ?? []).map((item, idx) => {
          const pct = Math.round((item.count / max) * 100)
          const colors = STAGE_COLORS[item.stage] ?? STAGE_COLORS.new
          const dropOff =
            idx > 0 && funnel[idx - 1].count > 0
              ? Math.round((1 - item.count / funnel[idx - 1].count) * 100)
              : null

          return (
            <div key={item.stage}>
              {idx > 0 && (
                <div className="flex items-center gap-2 text-xs text-slate-500 mb-1 pl-2">
                  <ArrowRight size={12} />
                  {dropOff !== null && (
                    <span className="text-rose-400">{dropOff}% drop-off</span>
                  )}
                </div>
              )}
              <div className={`flex items-center gap-3 border ${colors.border} bg-white/[0.03] rounded-xl px-4 py-3`}>
                <div className="w-24 shrink-0">
                  <span className={`text-xs font-semibold uppercase tracking-wider ${colors.text}`}>
                    {item.stage}
                  </span>
                </div>
                <div className="flex-1 h-2.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${colors.bar} rounded-full transition-all duration-700`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className={`text-sm font-bold font-mono ${colors.text} w-12 text-right`}>
                  {item.count.toLocaleString()}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
