const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  }

  const response = await fetch(url, config)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }))
    throw new Error(error.error || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Throws
  getThrows: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/throws?${query}`)
  },

  getThrowCount: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/throws/count?${query}`)
  },

  // Stats
  getStatistics: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/stats?${query}`)
  },

  getSegmentDistribution: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/stats/segments?${query}`)
  },

  getScoreDistribution: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/stats/scores?${query}`)
  },

  getDailySummary: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/stats/daily?${query}`)
  },

  getRecentThrows: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/stats/recent?${query}`)
  },

  // Games
  createGame: (data) => {
    return request('/games', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  getGame: (gameId) => {
    return request(`/games/${gameId}`)
  },

  deleteGame: (gameId) => {
    return request(`/games/${gameId}`, {
      method: 'DELETE'
    })
  },

  listGames: () => {
    return request('/games')
  },

  processThrow: (gameId, throwData) => {
    return request(`/games/${gameId}/throw`, {
      method: 'POST',
      body: JSON.stringify(throwData)
    })
  },

  // Health
  healthCheck: () => request('/health'),

  // BLE Status
  getBLEStatus: () => request('/ble/status')
}

export default api
