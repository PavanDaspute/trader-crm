import React from 'react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, Cell,
} from 'recharts'

const COLORS = ['#06b6d4', '#a855f7', '#f59e0b', '#22c55e', '#f43f5e']

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-4 py-3 text-sm border border-white/10">
      <p className="text-slate-400 mb-1 font-semibold">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }} className="text-xs">
          {p.name}: {p.value}
          {p.name === 'Conversion' ? '%' : ''}
        </p>
      ))}
    </div>
  )
}

export default function SourceChart({ sources, loading }) {
  if (loading) {
    return (
      <div className="chart-container">
        <p className="section-title">Source Breakdown</p>
        <div className="h-56 bg-white/5 rounded-xl animate-pulse mt-2" />
      </div>
    )
  }

  const data = (sources ?? []).map((s) => ({
    source: s.source,
    Traders: s.count,
    Funded: s.funded,
    'Conv %': s.conversion_rate,
  }))

  return (
    <div className="chart-container">
      <p className="section-title">Acquisition Source Breakdown</p>
      {data.length === 0 ? (
        <div className="flex items-center justify-center h-56 text-slate-500 text-sm">No data</div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="source" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
            <Bar dataKey="Traders" fill="#06b6d4" radius={[4, 4, 0, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
            <Bar dataKey="Funded" fill="#22c55e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
