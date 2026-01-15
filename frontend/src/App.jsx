import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Header from './components/Header'
import AgentWorkflow from './components/AgentWorkflow'
import InputForm from './components/InputForm'
import ResultsPanel from './components/ResultsPanel'
import StatsPanel from './components/StatsPanel'
import Footer from './components/Footer'
import About from './components/About'
import History from './components/History'
import FinalDraftView from './components/FinalDraftView'
import apiService from './services/api'

// Helper function to count API calls from backend response
const countApiCalls = (data) => {
  if (!data) return 12
  
  // If explicitly provided
  if (data.api_calls_count) return data.api_calls_count
  if (data.metrics?.api_calls) return data.metrics.api_calls
  if (data.statistics?.total_api_calls) return data.statistics.total_api_calls
  
  // Estimate from response structure: each agent call + confidence + reviewer
  let count = 0
  
  // Count handoff calls (Research, Developer, Writer, Confidence)
  if (data.handoff) {
    if (data.handoff.research) count += 1 // Research API call
    if (data.handoff.developer) count += 1 // Developer API call
    if (data.handoff.writer) count += 1 // Writer API call
  }
  
  // Confidence evaluation
  if (data.confidence) count += 1
  
  // CEO planning
  count += 1
  
  // Email sending
  if (data.email?.result) count += 1
  
  return count > 0 ? count : 12
}

function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [currentAgent, setCurrentAgent] = useState(null)
  const [results, setResults] = useState(null)
  const [sessionStats, setSessionStats] = useState(null)
  const [error, setError] = useState(null)
  const [backendStatus, setBackendStatus] = useState('checking')
  const [currentPage, setCurrentPage] = useState('home') // 'home', 'about', 'history', or 'finalDraft'
  const [viewingSession, setViewingSession] = useState(null)

  // Check backend connection on mount
  useEffect(() => {
    checkBackend()
  }, [])

  const checkBackend = async () => {
    try {
      await apiService.health()
      setBackendStatus('connected')
    } catch (err) {
      console.error('Backend not available:', err)
      setBackendStatus('disconnected')
    }
  }

  const saveToHistory = (sessionId, goal, timestamp) => {
    // Store minimal info - only session_id to retrieve full data from DB
    try {
      const existing = localStorage.getItem('agentforge_session_ids')
      const sessionIds = existing ? JSON.parse(existing) : []
      sessionIds.unshift({ session_id: sessionId, goal, timestamp })
      // Keep only last 50 sessions
      const limited = sessionIds.slice(0, 50)
      localStorage.setItem('agentforge_session_ids', JSON.stringify(limited))
    } catch (err) {
      console.error('Failed to save session ID to history:', err)
    }
  }

  const handleViewSession = async (session) => {
    setError(null)
    setIsRunning(true)
    
    try {
      // Always fetch from backend database using session_id
      const sessionData = await apiService.getSession(session.session_id)
      
      // Construct results object with fetched data
      const resultsData = {
        status: 'completed',
        goal: session.goal,
        agents_executed: sessionData.agents_executed || [],
        timestamp: session.timestamp,
        data: sessionData
      }
      
      setViewingSession({
        ...session,
        results: resultsData
      })
    } catch (err) {
      console.error('Failed to fetch session from database:', err)
      setError(`Failed to fetch session from database: ${err.message}`)
      return
    } finally {
      setIsRunning(false)
    }
    
    // Navigate to the separate final draft page
    setCurrentPage('finalDraft')
  }

  const handleRun = async (goal) => {
    setIsRunning(true)
    setResults(null)
    setError(null)
    setCurrentAgent('CEO')

    try {
      // Start backend request
      const resultPromise = apiService.run(goal, null)
      
      // Simulate agent progression for UI feedback
      const agents = ['CEO', 'Research', 'Developer', 'Writer', 'Confidence', 'Reviewer']
      
      // Animate through agents while waiting for backend
      for (const agent of agents) {
        setCurrentAgent(agent)
        await new Promise(resolve => setTimeout(resolve, 1500))
      }

      // Wait for backend result
      const result = await resultPromise
      console.log('Backend result:', result)

      setResults({
        status: 'completed',
        goal,
        agents_executed: agents,
        timestamp: new Date().toISOString(),
        data: result
      })
      
      // Calculate actual API call count from backend response
      const apiCallCount = countApiCalls(result)
      
      const stats = {
        totalTasks: 6,
        completedTasks: 6,
        apiCalls: apiCallCount,
        estimatedSavings: '67%'
      }
      
      setSessionStats(stats)
      
      // Save only session_id to history (will fetch from DB when needed)
      if (result.session_id) {
        saveToHistory(result.session_id, goal, new Date().toISOString())
      }
    } catch (err) {
      console.error('Error:', err)
      setError(err.response?.data?.error || err.response?.data?.detail || err.message || 'An error occurred')
      
      // If backend is down, use mock data
      if (err.code === 'ERR_NETWORK') {
        const mockResult = {
          status: 'completed (mock)',
          goal,
          agents_executed: ['CEO', 'Research', 'Developer', 'Writer', 'Confidence', 'Reviewer'],
          timestamp: new Date().toISOString(),
          note: 'Backend unavailable - showing mock data',
          data: { message: 'Mock execution - backend not connected', api_calls_count: 12 }
        }
        setResults(mockResult)
        setSessionStats({
          totalTasks: 6,
          completedTasks: 6,
          apiCalls: 12,
          estimatedSavings: '67%'
        })
      }
    } finally {
      setIsRunning(false)
      setCurrentAgent(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black">
      {currentPage === 'about' ? (
        <About onBack={() => setCurrentPage('home')} />
      ) : currentPage === 'history' ? (
        <History 
          onBack={() => setCurrentPage('home')} 
          onViewSession={handleViewSession}
        />
      ) : currentPage === 'finalDraft' && viewingSession ? (
        <FinalDraftView session={viewingSession} onBack={() => setCurrentPage('history')} />
      ) : (
        <>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary-900/20 via-transparent to-transparent"></div>
          
          <div className="relative z-10">
            <Header currentPage="home" onBack={(page) => setCurrentPage(page || 'about')} />
        
        <main className="container mx-auto px-4 py-8 max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-8"
          >
            {/* Hero Section */}
            <div className="text-center space-y-6 mb-12">
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className="relative py-4"
              >
                <h1 className="text-7xl md:text-8xl font-black bg-gradient-to-r from-primary-300 via-primary-500 to-primary-700 bg-clip-text text-transparent leading-tight">
                  Intellixa
                </h1>
                {/* Glow effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-primary-600/20 blur-3xl -z-10 opacity-50"></div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2, ease: 'easeOut' }}
                className="relative"
              >
                <p className="text-lg md:text-2xl font-semibold bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
                  Enterprise-Grade Multi-Agent AI Orchestration Platform
                </p>
                {/* Underline accent */}
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '60%' }}
                  transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
                  className="h-1 bg-gradient-to-r from-primary-500 via-primary-400 to-transparent rounded-full mx-auto mt-3"
                ></motion.div>
              </motion.div>
              
              {/* Backend Status Indicator */}
              <div className="flex items-center justify-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  backendStatus === 'connected' ? 'bg-green-500' :
                  backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
                } ${backendStatus === 'connected' ? 'animate-pulse' : ''}`}></div>
                <span className="text-sm text-gray-500">
                  Backend: {backendStatus === 'connected' ? 'Connected' : 
                           backendStatus === 'disconnected' ? 'Disconnected (using mock data)' : 
                           'Checking...'}
                </span>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-effect border-l-4 border-red-500 p-4 mb-6"
              >
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="font-semibold text-red-400">Error</p>
                    <p className="text-sm text-gray-300">{error}</p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Input Form */}
            <InputForm onSubmit={handleRun} isRunning={isRunning} />

            {/* Agent Workflow Visualization */}
            <AgentWorkflow currentAgent={currentAgent} isRunning={isRunning} />

            {/* Results Panel */}
            {results && <ResultsPanel results={results} />}

            {/* Stats Panel */}
            {sessionStats && <StatsPanel stats={sessionStats} />}
          </motion.div>
        </main>

        <Footer />
      </div>
        </>
      )}
    </div>
  )
}

export default App
