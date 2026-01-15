import axios from 'axios'

// Use proxy in development, direct URL in production
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiService = {
  // Health check
  async health() {
    const response = await api.get('/health')
    return response.data
  },

  // Run orchestrator workflow
  async run(goal, email) {
    const response = await api.post('/run', { goal, email })
    return response.data
  },

  // Get session details by ID
  async getSession(sessionId) {
    const response = await api.get(`/session/${sessionId}`)
    return response.data
  },

  // Approve human-in-the-loop decision
  async approve(sessionId, decision) {
    const response = await api.post('/approve', {
      session_id: sessionId,
      decision,
    })
    return response.data
  },
}

export default apiService
