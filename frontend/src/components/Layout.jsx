import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import useSocket from '../hooks/useSocket'

export function Layout({ children }) {
  const location = useLocation()
  const { isConnected, bleStatus, latestThrow } = useSocket()
  const [showThrowNotification, setShowThrowNotification] = useState(false)

  // 投擲検出時に通知を表示
  useEffect(() => {
    if (latestThrow) {
      setShowThrowNotification(true)
      const timer = setTimeout(() => setShowThrowNotification(false), 2000)
      return () => clearTimeout(timer)
    }
  }, [latestThrow])

  const navItems = [
    { path: '/', label: 'Throws' },
    { path: '/analysis', label: 'Analysis' },
    { path: '/game', label: 'Game' }
  ]

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{
        borderBottom: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)'
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: 'var(--space-lg) var(--space-xl)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          {/* Logo */}
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.5rem',
            fontWeight: 700,
            letterSpacing: '-0.02em'
          }}>
            DARTSLIVE<span style={{ color: 'var(--color-red)' }}>_</span>
          </div>

          {/* Navigation */}
          <nav style={{
            display: 'flex',
            gap: 'var(--space-md)'
          }}>
            {navItems.map(item => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  style={{
                    position: 'relative',
                    padding: 'var(--space-sm) var(--space-md)',
                    color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.875rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    transition: 'color var(--transition-fast)'
                  }}
                >
                  {item.label}
                  {isActive && (
                    <motion.div
                      layoutId="activeNav"
                      style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '2px',
                        backgroundColor: 'var(--color-red)'
                      }}
                      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                  )}
                </Link>
              )
            })}
          </nav>

          {/* Status Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-md)'
          }}>
            {/* WebSocket Status */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-sm)'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: isConnected ? 'var(--color-green)' : 'var(--color-text-tertiary)',
                animation: isConnected ? 'pulse 2s ease-in-out infinite' : 'none'
              }} />
              <span style={{
                fontSize: '0.75rem',
                color: 'var(--color-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.1em'
              }}>
                WS
              </span>
            </div>

            {/* BLE Status */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-sm)'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: bleStatus?.is_connected ? 'var(--color-green)' : 'var(--color-text-tertiary)',
                animation: bleStatus?.is_connected ? 'pulse 2s ease-in-out infinite' : 'none'
              }} />
              <span style={{
                fontSize: '0.75rem',
                color: 'var(--color-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.1em'
              }}>
                BLE
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Throw Notification */}
      <AnimatePresence>
        {showThrowNotification && latestThrow && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            style={{
              position: 'fixed',
              top: '80px',
              right: 'var(--space-xl)',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-md) var(--space-lg)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-md)'
            }}
          >
            <div style={{
              fontSize: '2rem',
              fontWeight: 700,
              color: latestThrow.score >= 20 ? 'var(--color-green)' : 'var(--color-text-primary)'
            }}>
              {latestThrow.score}
            </div>
            <div style={{
              borderLeft: '1px solid var(--color-border)',
              paddingLeft: 'var(--space-md)'
            }}>
              <div style={{
                fontSize: '0.875rem',
                fontFamily: 'var(--font-mono)',
                color: 'var(--color-text-secondary)'
              }}>
                {latestThrow.segment_name}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main style={{
        flex: 1,
        maxWidth: '1400px',
        width: '100%',
        margin: '0 auto',
        padding: 'var(--space-2xl) var(--space-xl)'
      }}>
        {children}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--color-border)',
        padding: 'var(--space-lg) var(--space-xl)',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '0.75rem',
          color: 'var(--color-text-tertiary)',
          fontFamily: 'var(--font-mono)'
        }}>
          {bleStatus?.device_name && (
            <span>Connected to: {bleStatus.device_name} • </span>
          )}
          DARTSLIVE HOME Web Application
        </div>
      </footer>
    </div>
  )
}

export default Layout
