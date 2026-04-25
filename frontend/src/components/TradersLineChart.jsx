import React from 'react'
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-4 py-3 text-sm border border-white/10">
      <p className="text-slate-400 mb-1 font-mono text-xs">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }} className="font-semibold">
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  )
}

export default function TradersLineChart({ timeseries, loading }) {
  const data = timeseries?.series ?? []

  if (loading) {
    return (
      <div className="chart-container">
        <p className="section-title">Traders Over Time</p>
        <div className="h-56 bg-white/5 rounded-xl animate-pulse mt-2" />
      </div>
    )
  }

  return (
    <div className="chart-container">
      <p className="section-title">Traders Over Time</p>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="traderGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#06b6d4" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}   />
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
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
          <Line
            type="monotone"
            dataKey="traders"
            name="New Traders"
            stroke="#06b6d4"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#06b6d4' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
