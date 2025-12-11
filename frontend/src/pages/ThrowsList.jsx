import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { api } from '../services/api'
import useSocket from '../hooks/useSocket'
import DateRangeFilter from '../components/DateRangeFilter'

export function ThrowsList() {
  const [throws, setThrows] = useState([])
  const [loading, setLoading] = useState(true)
  const [dateFilter, setDateFilter] = useState({ start_time: null, end_time: null })
  const { latestThrow } = useSocket()

  useEffect(() => {
    fetchThrows()
  }, [dateFilter])

  useEffect(() => {
    // リアルタイム投擲は期間フィルターに関わらず追加（最新データなので）
    if (latestThrow) {
      setThrows(prev => [latestThrow, ...prev].slice(0, 50))
    }
  }, [latestThrow])

  async function fetchThrows() {
    try {
      setLoading(true)
      const params = { limit: 50 }
      if (dateFilter.start_time) params.start_time = dateFilter.start_time
      if (dateFilter.end_time) params.end_time = dateFilter.end_time

      const response = await api.getThrows(params)
      setThrows(response.throws || [])
    } catch (error) {
      console.error('Failed to fetch throws:', error)
    } finally {
      setLoading(false)
    }
  }

  function handleFilterChange(filter) {
    setDateFilter(filter)
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-3xl)' }}>
        <div className="animate-pulse" style={{ color: 'var(--color-text-secondary)' }}>
          Loading...
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-2xl)' }}>
        <h1 style={{
          fontSize: '3rem',
          fontFamily: 'var(--font-display)',
          marginBottom: 'var(--space-sm)'
        }}>
          Throws
        </h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          {throws.length} 件の投擲記録
        </p>
      </div>

      {/* Date Range Filter */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <DateRangeFilter onFilterChange={handleFilterChange} />
      </div>

      {/* Throws Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: 'var(--space-md)'
      }}>
        <AnimatePresence>
          {throws.map((throw_, index) => (
            <motion.div
              key={throw_.id || index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3, delay: index * 0.02 }}
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                padding: 'var(--space-lg)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-md)',
                transition: 'transform var(--transition-fast), border-color var(--transition-fast)',
                cursor: 'pointer'
              }}
              whileHover={{ scale: 1.02, borderColor: 'var(--color-text-tertiary)' }}
            >
              {/* Score */}
              <div style={{
                fontFamily: 'var(--font-display)',
                fontSize: '3rem',
                fontWeight: 700,
                color: getScoreColor(throw_.score),
                lineHeight: 1
              }}>
                {throw_.score}
              </div>

              {/* Segment Name */}
              <div style={{
                fontSize: '1rem',
                color: 'var(--color-text-primary)',
                fontFamily: 'var(--font-mono)'
              }}>
                {throw_.segment_name}
              </div>

              {/* Details */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: 'var(--space-sm)',
                borderTop: '1px solid var(--color-border)',
                fontSize: '0.75rem',
                color: 'var(--color-text-tertiary)'
              }}>
                <span>
                  {throw_.multiplier}x{throw_.base_number}
                </span>
                <span>
                  {new Date(throw_.timestamp).toLocaleTimeString('ja-JP')}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {throws.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: 'var(--space-3xl)',
          color: 'var(--color-text-secondary)'
        }}>
          投擲データがありません。ダーツを投げて記録を開始してください。
        </div>
      )}
    </div>
  )
}

function getScoreColor(score) {
  if (score >= 50) return 'var(--color-red)'
  if (score >= 40) return 'var(--color-yellow)'
  if (score >= 20) return 'var(--color-green)'
  return 'var(--color-text-primary)'
}

export default ThrowsList
