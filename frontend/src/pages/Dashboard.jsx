import React, { useState, useEffect, useCallback } from 'react'
import { RefreshCw, Plus, TrendingUp, Activity } from 'lucide-react'

import KPICards from '../components/KPICards'
import FunnelChart from '../components/FunnelChart'
import TradersLineChart from '../components/TradersLineChart'
import DepositsChart from '../components/DepositsChart'
import StatusPieChart from '../components/StatusPieChart'
import SourceChart from '../components/SourceChart'
import TraderTable from '../components/TraderTable'
import AddTraderModal from '../components/AddTraderModal'

import {
  fetchOverview, fetchFunnel, fetchTimeseries,
  fetchSources, fetchTraders,
} from '../api'

const AUTO_REFRESH_MS = 30_000

export default function Dashboard() {
  const [stats,      setStats]      = useState(null)
  const [funnel,     setFunnel]     = useState(null)
  const [timeseries, setTimeseries] = useState(null)
  const [sources,    setSources]    = useState(null)
  const [traders,    setTraders]    = useState(null)
  const [loading,    setLoading]    = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [showModal,  setShowModal]  = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)

  const loadAll = useCallback(async (silent = false) => {
    if (!silent) setLoading(true)
    else setRefreshing(true)
    try {
      const [s, f, ts, src, tr] = await Promise.all([
        fetchOverview(),
        fetchFunnel(),
        fetchTimeseries(30),
        fetchSources(),
        fetchTraders(),
      ])
      setStats(s)
      setFunnel(f)
      setTimeseries(ts)
      setSources(src)
      setTraders(tr)
      setLastUpdate(new Date())
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // Initial load + auto-refresh
  useEffect(() => {
    loadAll()
    const interval = setInterval(() => loadAll(true), AUTO_REFRESH_MS)
    return () => clearInterval(interval)
  }, [loadAll])

  const handleTraderAdded = useCallback(() => {
    loadAll(true)
  }, [loadAll])

  return (
    <div className="min-h-screen">
      {/* ── Top Nav ───────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 border-b border-white/5 bg-surface-900/80 backdrop-blur-md">
        <div className="max-w-[1600px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-green-500 rounded-lg flex items-center justify-center">
              <TrendingUp size={16} className="text-white" />
            </div>
            <div>
              <span className="font-bold text-white text-sm">TraderCRM</span>
              <span className="text-slate-500 text-xs ml-2 hidden sm:inline">Conversion Analytics Platform</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {lastUpdate && (
              <span className="text-xs text-slate-500 hidden md:inline">
                Updated {lastUpdate.toLocaleTimeString()}
              </span>
            )}
            <button
              id="refresh-btn"
              onClick={() => loadAll(true)}
              disabled={refreshing}
              className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-400
                hover:text-white hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
              Refresh
            </button>
            <button
              id="add-trader-btn"
              onClick={() => setShowModal(true)}
              className="flex items-center gap-2 px-4 py-1.5 text-xs font-semibold text-white
                bg-cyan-600 hover:bg-cyan-500 rounded-lg transition-colors"
            >
              <Plus size={13} />
              Add Trader
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Content ──────────────────────────────────────────────── */}
      <main className="max-w-[1600px] mx-auto px-6 py-8 space-y-8">

        {/* Live indicator */}
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-xs text-slate-500 font-medium">Live Dashboard</span>
          <Activity size={12} className="text-slate-600" />
        </div>

        {/* KPI Cards */}
        <section aria-label="KPI Overview">
          <KPICards stats={stats} loading={loading} />
        </section>

        {/* Funnel + Pie */}
        <section aria-label="Funnel and Status" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <FunnelChart funnel={funnel} loading={loading} />
          </div>
          <StatusPieChart funnel={funnel} loading={loading} />
        </section>

        {/* Time series charts */}
        <section aria-label="Time Series" className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <TradersLineChart timeseries={timeseries} loading={loading} />
          <DepositsChart   timeseries={timeseries} loading={loading} />
        </section>

        {/* Source breakdown */}
        <section aria-label="Source Analysis">
          <SourceChart sources={sources} loading={loading} />
        </section>

        {/* Trader Table */}
        <section aria-label="Trader Registry">
          <TraderTable traders={traders} loading={loading} />
        </section>
      </main>

      {/* Add Trader Modal */}
      {showModal && (
        <AddTraderModal
          onClose={() => setShowModal(false)}
          onSuccess={handleTraderAdded}
        />
      )}
    </div>
  )
}
