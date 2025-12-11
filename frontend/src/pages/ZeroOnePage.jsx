import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import useGame from '../hooks/useGame'

export function ZeroOnePage() {
  const [gameId, setGameId] = useState(null)
  const [showSetup, setShowSetup] = useState(true)
  const { gameState, loading, createGame, deleteGame } = useGame(gameId)

  async function handleStartGame(config) {
    try {
      const newGameId = await createGame(config)
      setGameId(newGameId)
      setShowSetup(false)
    } catch (error) {
      console.error('Failed to start game:', error)
      alert('ゲームの開始に失敗しました')
    }
  }

  async function handleEndGame() {
    if (confirm('ゲームを終了しますか？')) {
      await deleteGame()
      setGameId(null)
      setShowSetup(true)
    }
  }

  if (showSetup || !gameState) {
    return <GameSetup onStart={handleStartGame} loading={loading} />
  }

  return (
    <div>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--space-2xl)'
      }}>
        <div>
          <h1 style={{
            fontSize: '3rem',
            fontFamily: 'var(--font-display)',
            marginBottom: 'var(--space-sm)'
          }}>
            01 Game
          </h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            {gameState.starting_score} • {gameState.finish_type.toUpperCase()} • Round {gameState.round_count}
          </p>
        </div>
        <button
          onClick={handleEndGame}
          style={{
            padding: 'var(--space-md) var(--space-lg)',
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-secondary)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.875rem',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            transition: 'all var(--transition-fast)',
            cursor: 'pointer'
          }}
          onMouseEnter={e => {
            e.target.style.borderColor = 'var(--color-red)'
            e.target.style.color = 'var(--color-red)'
          }}
          onMouseLeave={e => {
            e.target.style.borderColor = 'var(--color-border)'
            e.target.style.color = 'var(--color-text-secondary)'
          }}
        >
          End Game
        </button>
      </div>

      {/* Game Board */}
      {gameState.state === 'finished' ? (
        <WinnerScreen winner={gameState.winner} onNewGame={() => setShowSetup(true)} />
      ) : (
        <ScoreBoard gameState={gameState} />
      )}
    </div>
  )
}

function GameSetup({ onStart, loading }) {
  const [playerNames, setPlayerNames] = useState(['Player 1'])
  const [startingScore, setStartingScore] = useState(501)
  const [finishType, setFinishType] = useState('double')
  const [customScore, setCustomScore] = useState('')

  function addPlayer() {
    setPlayerNames([...playerNames, `Player ${playerNames.length + 1}`])
  }

  function removePlayer(index) {
    setPlayerNames(playerNames.filter((_, i) => i !== index))
  }

  function updatePlayer(index, name) {
    const newNames = [...playerNames]
    newNames[index] = name
    setPlayerNames(newNames)
  }

  function handleSubmit(e) {
    e.preventDefault()
    const score = customScore ? parseInt(customScore) : startingScore

    // スコアのバリデーション
    if (isNaN(score) || score <= 0 || score > 10000) {
      alert('スコアは1から10000の間で入力してください')
      return
    }

    onStart({
      game_type: 'zero_one',
      player_names: playerNames,
      settings: {
        starting_score: score,
        finish_type: finishType
      }
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{
        maxWidth: '600px',
        margin: '0 auto'
      }}
    >
      <h1 style={{
        fontSize: '3rem',
        fontFamily: 'var(--font-display)',
        marginBottom: 'var(--space-2xl)',
        textAlign: 'center'
      }}>
        Start 01 Game
      </h1>

      <form onSubmit={handleSubmit} style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        padding: 'var(--space-2xl)'
      }}>
        {/* Starting Score */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <label style={{
            display: 'block',
            marginBottom: 'var(--space-md)',
            fontSize: '0.875rem',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: 'var(--color-text-secondary)'
          }}>
            Starting Score
          </label>
          <div style={{ display: 'flex', gap: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
            {[301, 501, 701].map(score => (
              <button
                key={score}
                type="button"
                onClick={() => {
                  setStartingScore(score)
                  setCustomScore('')
                }}
                style={{
                  flex: 1,
                  padding: 'var(--space-md)',
                  backgroundColor: startingScore === score && !customScore ? 'var(--color-red)' : 'var(--color-surface-elevated)',
                  border: `1px solid ${startingScore === score && !customScore ? 'var(--color-red)' : 'var(--color-border)'}`,
                  color: 'var(--color-text-primary)',
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)'
                }}
              >
                {score}
              </button>
            ))}
          </div>
          <input
            type="number"
            placeholder="Custom score..."
            value={customScore}
            onChange={e => setCustomScore(e.target.value)}
            style={{
              width: '100%',
              padding: 'var(--space-md)',
              backgroundColor: 'var(--color-surface-elevated)',
              border: `1px solid ${customScore ? 'var(--color-red)' : 'var(--color-border)'}`,
              color: 'var(--color-text-primary)',
              fontFamily: 'var(--font-mono)',
              fontSize: '1rem'
            }}
          />
        </div>

        {/* Finish Type */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <label style={{
            display: 'block',
            marginBottom: 'var(--space-md)',
            fontSize: '0.875rem',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: 'var(--color-text-secondary)'
          }}>
            Finish Type
          </label>
          <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
            {[
              { value: 'straight', label: 'Straight' },
              { value: 'double', label: 'Double Out' },
              { value: 'master', label: 'Master Out' }
            ].map(option => (
              <button
                key={option.value}
                type="button"
                onClick={() => setFinishType(option.value)}
                style={{
                  flex: 1,
                  padding: 'var(--space-md)',
                  backgroundColor: finishType === option.value ? 'var(--color-red)' : 'var(--color-surface-elevated)',
                  border: `1px solid ${finishType === option.value ? 'var(--color-red)' : 'var(--color-border)'}`,
                  color: 'var(--color-text-primary)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)'
                }}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Players */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <label style={{
            display: 'block',
            marginBottom: 'var(--space-md)',
            fontSize: '0.875rem',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: 'var(--color-text-secondary)'
          }}>
            Players ({playerNames.length})
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
            {playerNames.map((name, index) => (
              <div key={index} style={{ display: 'flex', gap: 'var(--space-sm)' }}>
                <input
                  type="text"
                  value={name}
                  onChange={e => updatePlayer(index, e.target.value)}
                  style={{
                    flex: 1,
                    padding: 'var(--space-md)',
                    backgroundColor: 'var(--color-surface-elevated)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-primary)',
                    fontFamily: 'var(--font-mono)'
                  }}
                />
                {playerNames.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removePlayer(index)}
                    style={{
                      padding: 'var(--space-md)',
                      backgroundColor: 'var(--color-surface-elevated)',
                      border: '1px solid var(--color-border)',
                      color: 'var(--color-text-secondary)',
                      cursor: 'pointer'
                    }}
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={addPlayer}
            style={{
              marginTop: 'var(--space-md)',
              width: '100%',
              padding: 'var(--space-md)',
              backgroundColor: 'var(--color-surface-elevated)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.875rem',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)'
            }}
          >
            + Add Player
          </button>
        </div>

        {/* Start Button */}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: 'var(--space-lg)',
            backgroundColor: 'var(--color-red)',
            border: 'none',
            color: 'var(--color-text-primary)',
            fontFamily: 'var(--font-display)',
            fontSize: '1.25rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1,
            transition: 'all var(--transition-fast)'
          }}
        >
          {loading ? 'Starting...' : 'Start Game'}
        </button>
      </form>
    </motion.div>
  )
}

function ScoreBoard({ gameState }) {
  const players = gameState.players || []
  const scores = gameState.scores || {}

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${Math.min(players.length, 3)}, 1fr)`,
      gap: 'var(--space-lg)'
    }}>
      <AnimatePresence>
        {players.map((player) => {
          const score = scores[player.id]
          const isCurrentPlayer = player.is_current

          return (
            <motion.div
              key={player.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{
                opacity: 1,
                scale: 1,
                borderColor: isCurrentPlayer ? 'var(--color-green)' : 'var(--color-border)'
              }}
              exit={{ opacity: 0, scale: 0.9 }}
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '2px solid',
                borderColor: isCurrentPlayer ? 'var(--color-green)' : 'var(--color-border)',
                padding: 'var(--space-2xl)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 'var(--space-lg)',
                transition: 'border-color var(--transition-normal)'
              }}
            >
              {/* Player Name */}
              <div style={{
                fontSize: '1rem',
                color: isCurrentPlayer ? 'var(--color-green)' : 'var(--color-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                fontWeight: 700
              }}>
                {player.name}
                {isCurrentPlayer && (
                  <motion.span
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    style={{ marginLeft: 'var(--space-sm)' }}
                  >
                    •
                  </motion.span>
                )}
              </div>

              {/* Score */}
              <motion.div
                key={score}
                initial={{ scale: 1.2, color: 'var(--color-yellow)' }}
                animate={{ scale: 1, color: 'var(--color-text-primary)' }}
                transition={{ duration: 0.3 }}
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '5rem',
                  fontWeight: 700,
                  lineHeight: 1,
                  color: 'var(--color-text-primary)'
                }}
              >
                {score}
              </motion.div>

              {/* Progress Bar */}
              <div style={{
                width: '100%',
                height: '4px',
                backgroundColor: 'var(--color-surface-elevated)',
                overflow: 'hidden'
              }}>
                <motion.div
                  initial={{ width: '100%' }}
                  animate={{ width: `${(score / gameState.starting_score) * 100}%` }}
                  style={{
                    height: '100%',
                    backgroundColor: isCurrentPlayer ? 'var(--color-green)' : 'var(--color-text-tertiary)'
                  }}
                />
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}

function WinnerScreen({ winner, onNewGame }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      style={{
        textAlign: 'center',
        padding: 'var(--space-3xl)',
        backgroundColor: 'var(--color-surface)',
        border: '2px solid var(--color-red)'
      }}
    >
      <motion.h2
        initial={{ y: 20 }}
        animate={{ y: 0 }}
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: '4rem',
          color: 'var(--color-red)',
          marginBottom: 'var(--space-lg)'
        }}
      >
        Winner!
      </motion.h2>
      <div style={{
        fontSize: '2rem',
        fontFamily: 'var(--font-display)',
        marginBottom: 'var(--space-2xl)'
      }}>
        {winner?.name}
      </div>
      <button
        onClick={onNewGame}
        style={{
          padding: 'var(--space-lg) var(--space-2xl)',
          backgroundColor: 'var(--color-red)',
          border: 'none',
          color: 'var(--color-text-primary)',
          fontFamily: 'var(--font-display)',
          fontSize: '1.25rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          cursor: 'pointer'
        }}
      >
        New Game
      </button>
    </motion.div>
  )
}

export default ZeroOnePage
