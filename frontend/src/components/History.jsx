import { motion } from 'framer-motion'
import Header from './Header'
import Footer from './Footer'
import { useState, useEffect } from 'react'

const History = ({ onBack, onViewSession }) => {
  const [sessions, setSessions] = useState([])

  useEffect(() => {
    // Load sessions from localStorage (now only minimal session IDs)
    const loadSessions = () => {
      try {
        const saved = localStorage.getItem('agentforge_session_ids')
        if (saved) {
          setSessions(JSON.parse(saved))
        }
      } catch (err) {
        console.error('Failed to load sessions:', err)
      }
    }
    loadSessions()
  }, [])

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      localStorage.removeItem('agentforge_session_ids')
      setSessions([])
    }
  }

  const deleteSession = (sessionId) => {
    const updated = sessions.filter(s => s.session_id !== sessionId)
    setSessions(updated)
    localStorage.setItem('agentforge_session_ids', JSON.stringify(updated))
  }

  return (
    <>
      <Header currentPage="history" onBack={onBack} />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl min-h-screen">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-8"
        >
          {/* Header Section */}
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                Session History
              </h1>
              <p className="text-gray-400 mt-2">
                View and manage your past agent executions
              </p>
            </motion.div>

            {sessions.length > 0 && (
              <motion.button
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                onClick={clearHistory}
                className="px-4 py-2 glass-effect border border-red-500/50 text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
              >
                Clear All
              </motion.button>
            )}
          </div>

          {/* Sessions List */}
          {sessions.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="agent-card text-center py-16"
            >
              <div className="text-6xl mb-4">📋</div>
              <h2 className="text-2xl font-semibold text-gray-400 mb-2">No History Yet</h2>
              <p className="text-gray-500">Your completed sessions will appear here</p>
            </motion.div>
          ) : (
            <div className="space-y-4">
              {sessions.map((session, index) => (
                <motion.div
                  key={session.session_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="agent-card cursor-pointer hover:shadow-2xl hover:border-primary-500/50 transition-all group"
                  onClick={() => onViewSession(session)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
                          <span className="text-xl">🤖</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 transition-colors truncate">
                            {session.goal}
                          </h3>
                          <p className="text-sm text-gray-400">
                            {new Date(session.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="flex flex-wrap gap-3 mt-4">
                        <div className="glass-effect px-3 py-1 rounded-full flex items-center gap-2">
                          <span className="text-xs text-gray-400">📊</span>
                          <span className="text-xs font-semibold text-blue-400">
                            DB Stored
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-2">
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={(e) => {
                          e.stopPropagation()
                          onViewSession(session)
                        }}
                        className="p-2 glass-effect rounded-lg hover:bg-primary-500/20 transition-colors"
                        title="View details"
                      >
                        <svg className="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteSession(session.session_id)
                        }}
                        className="p-2 glass-effect rounded-lg hover:bg-red-500/20 transition-colors"
                        title="Delete session"
                      >
                        <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </main>

      <Footer />
    </>
  )
}

export default History
