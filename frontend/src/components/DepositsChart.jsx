import React from 'react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-4 py-3 text-sm border border-white/10">
      <p className="text-slate-400 mb-1 font-mono text-xs">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }} className="font-semibold">
          {p.name}: ${Number(p.value).toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </p>
      ))}
    </div>
  )
}

export default function DepositsChart({ timeseries, loading }) {
  const data = timeseries?.series ?? []

  if (loading) {
    return (
      <div className="chart-container">
        <p className="section-title">Deposits Over Time</p>
        <div className="h-56 bg-white/5 rounded-xl animate-pulse mt-2" />
      </div>
    )
  }

  return (
    <div className="chart-container">
      <p className="section-title">Deposits Over Time (USD)</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="depositGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.9} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.4} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => v.slice(5)}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
          <Bar
            dataKey="deposits"
            name="Deposits"
            fill="url(#depositGrad)"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
