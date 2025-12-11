import { useState } from 'react'
import { motion } from 'framer-motion'

/**
 * 期間フィルターコンポーネント
 */
export function DateRangeFilter({ onFilterChange }) {
  const [selectedPreset, setSelectedPreset] = useState('all')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  // 期間プリセット
  const presets = [
    { id: 'all', label: '全期間' },
    { id: 'today', label: '今日' },
    { id: 'week', label: '今週' },
    { id: 'month', label: '今月' },
    { id: 'custom', label: 'カスタム' }
  ]

  // プリセット選択時
  function handlePresetChange(presetId) {
    setSelectedPreset(presetId)

    const now = new Date()
    let start = null
    let end = null

    switch (presetId) {
      case 'today':
        start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59)
        break
      case 'week':
        const dayOfWeek = now.getDay()
        const diff = dayOfWeek === 0 ? 6 : dayOfWeek - 1 // 月曜始まり
        start = new Date(now.getFullYear(), now.getMonth(), now.getDate() - diff)
        start.setHours(0, 0, 0, 0)
        end = new Date()
        break
      case 'month':
        start = new Date(now.getFullYear(), now.getMonth(), 1)
        end = new Date()
        break
      case 'all':
        start = null
        end = null
        break
      case 'custom':
        // カスタムモードでは手動入力を待つ
        return
    }

    // ISO形式に変換
    const startTime = start ? start.toISOString() : null
    const endTime = end ? end.toISOString() : null

    onFilterChange({ start_time: startTime, end_time: endTime })
  }

  // カスタム日付変更時
  function handleCustomDateChange() {
    if (startDate || endDate) {
      const start = startDate ? new Date(startDate).toISOString() : null
      const end = endDate ? new Date(endDate + 'T23:59:59').toISOString() : null
      onFilterChange({ start_time: start, end_time: end })
    }
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-lg)',
      padding: 'var(--space-lg)',
      backgroundColor: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--radius-md)'
    }}>
      {/* プリセットボタン */}
      <div style={{
        display: 'flex',
        gap: 'var(--space-sm)',
        flexWrap: 'wrap'
      }}>
        {presets.map(preset => (
          <motion.button
            key={preset.id}
            onClick={() => handlePresetChange(preset.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            style={{
              padding: 'var(--space-sm) var(--space-md)',
              backgroundColor: selectedPreset === preset.id ? 'var(--color-red)' : 'transparent',
              color: selectedPreset === preset.id ? 'var(--color-bg)' : 'var(--color-text-secondary)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.875rem',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)'
            }}
          >
            {preset.label}
          </motion.button>
        ))}
      </div>

      {/* カスタム日付入力 */}
      {selectedPreset === 'custom' && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          style={{
            display: 'flex',
            gap: 'var(--space-md)',
            alignItems: 'center',
            flexWrap: 'wrap'
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
            <label style={{
              fontSize: '0.75rem',
              color: 'var(--color-text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.1em'
            }}>
              開始日
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              onBlur={handleCustomDateChange}
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                backgroundColor: 'var(--color-bg)',
                color: 'var(--color-text-primary)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.875rem'
              }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
            <label style={{
              fontSize: '0.75rem',
              color: 'var(--color-text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.1em'
            }}>
              終了日
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              onBlur={handleCustomDateChange}
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                backgroundColor: 'var(--color-bg)',
                color: 'var(--color-text-primary)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.875rem'
              }}
            />
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default DateRangeFilter
