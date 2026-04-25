import React from 'react'
import {
  Users, TrendingUp, Activity, DollarSign, BarChart2,
} from 'lucide-react'

const CARDS = [
  {
    key: 'total_traders',
    label: 'Total Traders',
    icon: Users,
    color: 'text-cyan-400',
    bg: 'from-cyan-900/30 to-transparent',
    border: 'border-cyan-500/20',
    glow: 'shadow-cyan-500/10',
    format: (v) => v?.toLocaleString() ?? '—',
  },
  {
    key: 'funded_traders',
    label: 'Funded Traders',
    icon: DollarSign,
    color: 'text-amber-400',
    bg: 'from-amber-900/30 to-transparent',
    border: 'border-amber-500/20',
    glow: 'shadow-amber-500/10',
    format: (v) => v?.toLocaleString() ?? '—',
  },
  {
    key: 'active_traders',
    label: 'Active Traders',
    icon: Activity,
    color: 'text-green-400',
    bg: 'from-green-900/30 to-transparent',
    border: 'border-green-500/20',
    glow: 'shadow-green-500/10',
    format: (v) => v?.toLocaleString() ?? '—',
  },
  {
    key: 'conversion_rate',
    label: 'Conversion Rate',
    icon: TrendingUp,
    color: 'text-purple-400',
    bg: 'from-purple-900/30 to-transparent',
    border: 'border-purple-500/20',
    glow: 'shadow-purple-500/10',
    format: (v) => `${v ?? 0}%`,
  },
  {
    key: 'total_deposits',
    label: 'Total Deposits',
    icon: BarChart2,
    color: 'text-rose-400',
    bg: 'from-rose-900/30 to-transparent',
    border: 'border-rose-500/20',
    glow: 'shadow-rose-500/10',
    format: (v) => `$${(v ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
  },
]

export default function KPICards({ stats, loading }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4 animate-slide-up">
      {CARDS.map(({ key, label, icon: Icon, color, bg, border, glow, format }) => (
        <div
          key={key}
          className={`kpi-card border ${border} overflow-hidden relative shadow-lg ${glow}`}
        >
          {/* background gradient accent */}
          <div className={`absolute inset-0 bg-gradient-to-br ${bg} pointer-events-none`} />

          <div className="relative z-10">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
              <div className={`p-2 rounded-lg bg-white/5 ${color}`}>
                <Icon size={16} />
              </div>
            </div>

            {loading ? (
              <div className="h-8 w-24 bg-white/10 rounded-lg animate-pulse" />
            ) : (
              <p className={`text-2xl font-bold ${color} font-mono tracking-tight`}>
                {format(stats?.[key])}
              </p>
            )}

            {!loading && key === 'conversion_rate' && (
              <p className="text-xs text-slate-500 mt-1">funded / total</p>
            )}
            {!loading && key === 'total_deposits' && (
              <p className="text-xs text-slate-500 mt-1">
                avg ${(stats?.avg_deposit_per_trader ?? 0).toFixed(2)} / trader
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
