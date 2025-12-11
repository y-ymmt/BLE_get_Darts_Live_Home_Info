import { useEffect, useState, useCallback } from 'react'
import socket from '../services/socket'

export function useSocket() {
  const [isConnected, setIsConnected] = useState(socket.connected)
  const [latestThrow, setLatestThrow] = useState(null)
  const [bleStatus, setBleStatus] = useState(null)

  useEffect(() => {
    function onConnect() {
      setIsConnected(true)
      console.log('Socket connected')
    }

    function onDisconnect() {
      setIsConnected(false)
      console.log('Socket disconnected')
    }

    function onThrow(data) {
      console.log('Throw detected:', data)
      setLatestThrow(data)
    }

    function onPlayerChange(data) {
      console.log('Player change:', data)
    }

    function onBLEConnected(data) {
      console.log('BLE connected:', data)
      setBleStatus({ is_connected: true, ...data })
    }

    function onBLEError(data) {
      console.error('BLE error:', data)
      setBleStatus({ is_connected: false, error: data.message })
    }

    function onBLEStatus(data) {
      setBleStatus(data)
    }

    socket.on('connect', onConnect)
    socket.on('disconnect', onDisconnect)
    socket.on('throw', onThrow)
    socket.on('player_change', onPlayerChange)
    socket.on('ble_connected', onBLEConnected)
    socket.on('ble_error', onBLEError)
    socket.on('ble_status', onBLEStatus)

    // Request initial status
    if (socket.connected) {
      socket.emit('request_status')
    }

    return () => {
      socket.off('connect', onConnect)
      socket.off('disconnect', onDisconnect)
      socket.off('throw', onThrow)
      socket.off('player_change', onPlayerChange)
      socket.off('ble_connected', onBLEConnected)
      socket.off('ble_error', onBLEError)
      socket.off('ble_status', onBLEStatus)
    }
  }, [])

  const requestStatus = useCallback(() => {
    socket.emit('request_status')
  }, [])

  return {
    socket,
    isConnected,
    latestThrow,
    bleStatus,
    requestStatus
  }
}

export default useSocket
