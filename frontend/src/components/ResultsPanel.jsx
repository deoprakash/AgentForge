import { motion } from 'framer-motion'

const ResultsPanel = ({ results }) => {
  const renderValue = (value) => {
    if (typeof value === 'object' && value !== null) {
      return <pre className="text-xs text-gray-300 whitespace-pre-wrap break-words">{JSON.stringify(value, null, 2)}</pre>
    }
    return <p className="text-white whitespace-pre-wrap break-words">{String(value)}</p>
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="agent-card"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Execution Results</h2>
        <div className="flex items-center space-x-2 px-4 py-2 bg-green-500/20 border border-green-500 rounded-lg">
          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-green-500 font-semibold">Completed</span>
        </div>
      </div>

      <div className="space-y-4">
        <div className="glass-effect p-4 rounded-lg">
          <p className="text-sm text-gray-400 mb-1">Goal</p>
          <p className="text-white">{results.goal}</p>
        </div>

        {/* Display backend output */}
        {results.data && (
          <div className="glass-effect p-4 rounded-lg">
            <p className="text-sm text-gray-400 mb-2">Output</p>
            <div className="max-h-96 overflow-y-auto">
              {renderValue(results.data)}
            </div>
          </div>
        )}

        <div className="glass-effect p-4 rounded-lg">
          <p className="text-sm text-gray-400 mb-2">Agents Executed</p>
          <div className="flex flex-wrap gap-2">
            {results.agents_executed.map((agent, index) => (
              <motion.span
                key={agent}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="px-3 py-1 bg-primary-500/20 border border-primary-500 rounded-full text-sm text-primary-400"
              >
                {agent}
              </motion.span>
            ))}
          </div>
        </div>

        <div className="glass-effect p-4 rounded-lg">
          <p className="text-sm text-gray-400 mb-1">Timestamp</p>
          <p className="text-white">{new Date(results.timestamp).toLocaleString()}</p>
        </div>

        {results.note && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg"
          >
            <p className="text-sm text-gray-300">
              ℹ️ {results.note}
            </p>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export default ResultsPanel
