import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { api } from '../services/api'

export function AnalysisPage() {
  const [stats, setStats] = useState(null)
  const [segmentDist, setSegmentDist] = useState([])
  const [scoreDist, setScoreDist] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      setLoading(true)
      const [statsRes, segmentRes, scoreRes] = await Promise.all([
        api.getStatistics(),
        api.getSegmentDistribution({ top_n: 10 }),
        api.getScoreDistribution()
      ])

      setStats(statsRes.statistics)
      setSegmentDist(segmentRes.distribution)
      setScoreDist(scoreRes.distribution)
    } catch (error) {
      console.error('Failed to fetch analysis data:', error)
    } finally {
      setLoading(false)
    }
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

  if (!stats) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-3xl)', color: 'var(--color-text-secondary)' }}>
        データがありません
      </div>
    )
  }

  const maxSegmentCount = segmentDist[0]?.count || 1
  const maxScoreCount = Math.max(...scoreDist.map(s => s.count), 1)

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-2xl)' }}>
        <h1 style={{
          fontSize: '3rem',
          fontFamily: 'var(--font-display)',
          marginBottom: 'var(--space-sm)'
        }}>
          Analysis
        </h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          投擲データの統計分析
        </p>
      </div>

      {/* Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--space-lg)',
        marginBottom: 'var(--space-3xl)'
      }}>
        <StatCard
          label="Total Throws"
          value={stats.total_throws}
          unit="回"
        />
        <StatCard
          label="Total Score"
          value={stats.total_score}
          unit="点"
        />
        <StatCard
          label="Average"
          value={stats.average_score?.toFixed(1) || '0.0'}
          unit="点/投"
        />
        <StatCard
          label="Max Score"
          value={stats.max_score}
          unit="点"
          highlight
        />
      </div>

      {/* Charts */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: 'var(--space-2xl)'
      }}>
        {/* Segment Distribution */}
        <div>
          <h2 style={{
            fontSize: '1.5rem',
            fontFamily: 'var(--font-display)',
            marginBottom: 'var(--space-lg)'
          }}>
            よく狙ったセグメント
          </h2>
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            padding: 'var(--space-lg)'
          }}>
            {segmentDist.map((item, index) => (
              <motion.div
                key={item.segment_name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                style={{
                  marginBottom: 'var(--space-lg)',
                  ':last-child': { marginBottom: 0 }
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: 'var(--space-xs)',
                  fontSize: '0.875rem'
                }}>
                  <span style={{ color: 'var(--color-text-primary)' }}>
                    {item.segment_name}
                  </span>
                  <span style={{ color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                    {item.count}回
                  </span>
                </div>
                <div style={{
                  height: '8px',
                  backgroundColor: 'var(--color-surface-elevated)',
                  overflow: 'hidden'
                }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(item.count / maxSegmentCount) * 100}%` }}
                    transition={{ duration: 0.8, delay: index * 0.05 }}
                    style={{
                      height: '100%',
                      backgroundColor: index === 0 ? 'var(--color-red)' : 'var(--color-text-tertiary)'
                    }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Score Distribution */}
        <div>
          <h2 style={{
            fontSize: '1.5rem',
            fontFamily: 'var(--font-display)',
            marginBottom: 'var(--space-lg)'
          }}>
            得点分布
          </h2>
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            padding: 'var(--space-lg)',
            display: 'flex',
            alignItems: 'flex-end',
            gap: 'var(--space-xs)',
            height: '300px'
          }}>
            {scoreDist.filter(s => s.score > 0).slice(0, 20).map((item, index) => (
              <motion.div
                key={item.score}
                initial={{ height: 0 }}
                animate={{ height: `${(item.count / maxScoreCount) * 100}%` }}
                transition={{ duration: 0.5, delay: index * 0.02 }}
                style={{
                  flex: 1,
                  backgroundColor: getScoreColor(item.score),
                  minWidth: '8px',
                  position: 'relative'
                }}
                title={`${item.score}点: ${item.count}回`}
              />
            ))}
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: 'var(--space-sm)',
            fontSize: '0.75rem',
            color: 'var(--color-text-tertiary)'
          }}>
            <span>低得点</span>
            <span>高得点</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, unit, highlight }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        backgroundColor: 'var(--color-surface)',
        border: `1px solid ${highlight ? 'var(--color-red)' : 'var(--color-border)'}`,
        padding: 'var(--space-lg)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-sm)'
      }}
    >
      <div style={{
        fontSize: '0.75rem',
        color: 'var(--color-text-tertiary)',
        textTransform: 'uppercase',
        letterSpacing: '0.1em'
      }}>
        {label}
      </div>
      <div style={{
        fontFamily: 'var(--font-display)',
        fontSize: '2.5rem',
        fontWeight: 700,
        color: highlight ? 'var(--color-red)' : 'var(--color-text-primary)',
        lineHeight: 1
      }}>
        {value}
        <span style={{
          fontSize: '1rem',
          fontWeight: 400,
          color: 'var(--color-text-secondary)',
          marginLeft: 'var(--space-xs)'
        }}>
          {unit}
        </span>
      </div>
    </motion.div>
  )
}

function getScoreColor(score) {
  if (score >= 50) return 'var(--color-red)'
  if (score >= 40) return 'var(--color-yellow)'
  if (score >= 20) return 'var(--color-green)'
  return 'var(--color-text-tertiary)'
}

export default AnalysisPage
