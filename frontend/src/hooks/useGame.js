import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import { useSocket } from './useSocket'

export function useGame(gameId) {
  const [gameState, setGameState] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastProcessedThrowTimestamp, setLastProcessedThrowTimestamp] = useState(null)
  const { latestThrow } = useSocket()

  // ゲーム状態を取得
  const fetchGameState = useCallback(async () => {
    if (!gameId) return

    try {
      setLoading(true)
      const response = await api.getGame(gameId)
      setGameState(response.game_state)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch game state:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [gameId])

  // ゲーム作成
  const createGame = useCallback(async (gameConfig) => {
    try {
      setLoading(true)
      const response = await api.createGame(gameConfig)
      setGameState(response.game_state)
      setError(null)
      return response.game_id
    } catch (err) {
      console.error('Failed to create game:', err)
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  // 投擲を処理
  const processThrow = useCallback(async (throwData) => {
    if (!gameId) return

    try {
      const response = await api.processThrow(gameId, throwData)

      // ゲーム状態を更新
      if (response.result && response.result.game_state) {
        setGameState(response.result.game_state)
      }

      return response.result
    } catch (err) {
      console.error('Failed to process throw:', err)
      setError(err.message)
      throw err
    }
  }, [gameId])

  // ゲーム削除
  const deleteGame = useCallback(async () => {
    if (!gameId) return

    try {
      await api.deleteGame(gameId)
      setGameState(null)
    } catch (err) {
      console.error('Failed to delete game:', err)
      setError(err.message)
      throw err
    }
  }, [gameId])

  // リアルタイム投擲を自動処理（ゲームがアクティブな場合）
  useEffect(() => {
    // ゲームが投擲を受け付けられる状態かチェック
    // waiting: ゲーム開始前（最初の投擲でplayingに遷移）
    // playing: ゲーム進行中
    const canAcceptThrows = gameState?.state === 'waiting' || gameState?.state === 'playing'

    // 同じ投擲を重複処理しないようにチェック
    if (gameId && canAcceptThrows && latestThrow &&
        latestThrow.timestamp !== lastProcessedThrowTimestamp) {
      setLastProcessedThrowTimestamp(latestThrow.timestamp)
      processThrow(latestThrow).catch(console.error)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latestThrow, gameId])

  // 初回読み込み
  useEffect(() => {
    if (gameId) {
      fetchGameState()
    }
  }, [gameId, fetchGameState])

  return {
    gameState,
    loading,
    error,
    createGame,
    processThrow,
    deleteGame,
    refetch: fetchGameState
  }
}

export default useGame
