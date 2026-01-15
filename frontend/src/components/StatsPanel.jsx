import { motion } from 'framer-motion'

const StatsPanel = ({ stats }) => {
  const statItems = [
    {
      label: 'Total Tasks',
      value: stats.totalTasks,
      icon: '📋',
      color: 'from-blue-500 to-blue-600',
    },
    {
      label: 'Completed',
      value: stats.completedTasks,
      icon: '✅',
      color: 'from-green-500 to-green-600',
    },
    {
      label: 'API Calls',
      value: stats.apiCalls,
      icon: '🔄',
      color: 'from-purple-500 to-purple-600',
    },
    {
      label: 'Cost Savings',
      value: stats.estimatedSavings,
      icon: '💰',
      color: 'from-yellow-500 to-yellow-600',
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="agent-card"
    >
      <h2 className="text-2xl font-bold mb-6">Session Statistics</h2>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statItems.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="glass-effect p-6 rounded-lg text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 + 0.2, type: 'spring' }}
              className="text-4xl mb-3"
            >
              {stat.icon}
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.1 + 0.3 }}
              className={`text-3xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent mb-2`}
            >
              {stat.value}
            </motion.div>
            
            <p className="text-sm text-gray-400">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg"
      >
        <div className="flex items-start space-x-3">
          <svg className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="text-sm font-semibold text-green-400 mb-1">Optimized Execution</p>
            <p className="text-sm text-gray-400">
              Our multi-agent system achieved <span className="text-green-400 font-semibold">{stats.estimatedSavings}</span> fewer
              API calls compared to traditional single-agent approaches, resulting in significant cost savings and improved efficiency.
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default StatsPanel
