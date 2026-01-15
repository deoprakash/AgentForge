import { motion } from 'framer-motion'

const FinalDraftView = ({ session, onBack }) => {
  // Extract final document from backend response structure
  const results = session.results?.data || session.results || {};
  const finalDocument =
    results.final?.document ||
    results.final_document ||
    results.handoff?.writer?.document ||
    results.document ||
    'No final draft available';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black">
      <div className="container mx-auto px-4 py-8">
        {/* Header with Back Button */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-white hover:text-primary-400 transition-colors mb-6"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to History
          </button>
          
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">Final Draft</h1>
          <p className="text-gray-400">
            Generated on {new Date(session.timestamp).toLocaleString()}
          </p>
        </motion.div>

        {/* User Input Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-lg p-6 mb-6"
        >
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-semibold text-white">User Input</h2>
          </div>
          <p className="text-gray-300 text-lg leading-relaxed">
            {session.goal || 'No goal specified'}
          </p>
        </motion.div>

        {/* Final Draft Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-lg p-8"
        >
          <div className="flex items-center gap-2 mb-6">
            <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h2 className="text-2xl font-semibold text-white">Final Document</h2>
          </div>
          
          <div className="prose prose-invert max-w-none">
            <div className="text-gray-100 leading-relaxed whitespace-pre-wrap break-words text-base">
              {finalDocument}
            </div>
          </div>
        </motion.div>

        {/* Session Stats */}
        {session.stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-lg p-4">
              <p className="text-gray-400 text-sm">API Calls</p>
              <p className="text-2xl font-bold text-purple-400">{session.stats.apiCalls || 0}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Agents Executed</p>
              <p className="text-2xl font-bold text-purple-400">{session.stats.agentsExecuted || 0}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Status</p>
              <p className={`text-2xl font-bold ${session.status === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                {session.status || 'Unknown'}
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default FinalDraftView
