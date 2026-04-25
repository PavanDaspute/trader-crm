import React from 'react'
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend,
} from 'recharts'

const COLORS = {
  new:        '#64748b',
  registered: '#3b82f6',
  funded:     '#f59e0b',
  active:     '#22c55e',
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
  return (
    <div className="glass-card px-4 py-3 text-sm border border-white/10">
      <p className="font-semibold" style={{ color: COLORS[name] }}>
        {name}: {value}
      </p>
    </div>
  )
}

const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  if (percent < 0.05) return null
  const RADIAN = Math.PI / 180
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

export default function StatusPieChart({ funnel, loading }) {
  const data = (funnel ?? []).filter((s) => s.count > 0)

  if (loading) {
    return (
      <div className="chart-container">
        <p className="section-title">Status Distribution</p>
        <div className="h-56 bg-white/5 rounded-xl animate-pulse mt-2" />
      </div>
    )
  }

  return (
    <div className="chart-container">
      <p className="section-title">Status Distribution</p>
      {data.length === 0 ? (
        <div className="flex items-center justify-center h-56 text-slate-500 text-sm">
          No trader data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="stage"
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={3}
              labelLine={false}
              label={renderCustomLabel}
            >
              {data.map((entry) => (
                <Cell key={entry.stage} fill={COLORS[entry.stage] ?? '#64748b'} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(v) => <span style={{ color: COLORS[v], fontSize: 12 }}>{v}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
