import React, { useState } from 'react'
import { Search, ChevronUp, ChevronDown } from 'lucide-react'

const STATUS_MAP = {
  new:        'status-new',
  registered: 'status-registered',
  funded:     'status-funded',
  active:     'status-active',
}

function StatusBadge({ status }) {
  return (
    <span className={STATUS_MAP[status] ?? 'status-new'}>
      {status}
    </span>
  )
}

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

export default function TraderTable({ traders, loading }) {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState('created_at')
  const [sortDir, setSortDir] = useState('desc')
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 10

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  const filtered = (traders ?? []).filter((t) =>
    [t.name, t.contact, t.source, t.status].some((v) =>
      v?.toLowerCase().includes(search.toLowerCase())
    )
  )

  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortKey] ?? ''
    const bv = b[sortKey] ?? ''
    const cmp = av < bv ? -1 : av > bv ? 1 : 0
    return sortDir === 'asc' ? cmp : -cmp
  })

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE)
  const paged = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const SortIcon = ({ col }) =>
    sortKey === col
      ? sortDir === 'asc' ? <ChevronUp size={13} className="inline ml-1" /> : <ChevronDown size={13} className="inline ml-1" />
      : <ChevronUp size={13} className="inline ml-1 opacity-20" />

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-5 border-b border-white/5">
        <p className="section-title mb-0">Trader Registry</p>
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            id="trader-search"
            type="text"
            placeholder="Search traders..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="pl-9 pr-4 py-2 text-sm bg-white/5 border border-white/10 rounded-xl
              text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50
              focus:ring-1 focus:ring-cyan-500/30 transition-all w-56"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/5">
              {[
                { key: 'name',          label: 'Name'          },
                { key: 'contact',       label: 'Contact'       },
                { key: 'source',        label: 'Source'        },
                { key: 'status',        label: 'Status'        },
                { key: 'total_deposit', label: 'Total Deposit' },
                { key: 'created_at',    label: 'Joined'        },
              ].map(({ key, label }) => (
                <th
                  key={key}
                  onClick={() => toggleSort(key)}
                  className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wider
                    px-5 py-3 cursor-pointer hover:text-slate-300 transition-colors select-none"
                >
                  {label}<SortIcon col={key} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={i} className="border-b border-white/[0.03]">
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="px-5 py-3.5">
                      <div className="h-4 bg-white/5 rounded animate-pulse" style={{ width: `${60 + (i+j) * 7}%` }} />
                    </td>
                  ))}
                </tr>
              ))
            ) : paged.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center text-slate-500 py-12 text-sm">
                  {search ? 'No traders match your search' : 'No traders found'}
                </td>
              </tr>
            ) : (
              paged.map((t) => (
                <tr key={t.id} className="table-row-hover border-b border-white/[0.03]">
                  <td className="px-5 py-3.5 font-medium text-slate-200">{t.name}</td>
                  <td className="px-5 py-3.5 text-slate-400 font-mono text-xs">{t.contact}</td>
                  <td className="px-5 py-3.5 text-slate-400">{t.source}</td>
                  <td className="px-5 py-3.5"><StatusBadge status={t.status} /></td>
                  <td className="px-5 py-3.5 font-mono text-slate-200">
                    ${(t.total_deposit ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-5 py-3.5 text-slate-400 text-xs">{formatDate(t.created_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-between px-5 py-3 border-t border-white/5 text-xs text-slate-400">
          <span>{sorted.length} results</span>
          <div className="flex gap-1">
            {Array.from({ length: totalPages }).map((_, i) => (
              <button
                key={i}
                onClick={() => setPage(i + 1)}
                className={`w-7 h-7 rounded flex items-center justify-center transition-colors
                  ${page === i + 1
                    ? 'bg-cyan-600 text-white font-semibold'
                    : 'hover:bg-white/10 text-slate-400'}`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
