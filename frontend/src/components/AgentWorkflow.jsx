import { motion, AnimatePresence } from 'framer-motion'

const agents = [
  { name: 'CEO', icon: '👔', description: 'Strategic Planning', color: 'from-blue-500 to-blue-600' },
  { name: 'Research', icon: '🔍', description: 'Data Gathering', color: 'from-green-500 to-green-600' },
  { name: 'Developer', icon: '💻', description: 'Code Generation', color: 'from-purple-500 to-purple-600' },
  { name: 'Writer', icon: '✍️', description: 'Content Creation', color: 'from-orange-500 to-orange-600' },
  { name: 'Confidence', icon: '✅', description: 'Quality Check', color: 'from-yellow-500 to-yellow-600' },
  { name: 'Reviewer', icon: '🔎', description: 'Final Review', color: 'from-red-500 to-red-600' },
]

const AgentWorkflow = ({ currentAgent, isRunning }) => {
  return (
    <div className="agent-card">
      <h2 className="text-2xl font-bold mb-6 text-center">Agent Workflow Pipeline</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent, index) => {
          const isActive = currentAgent === agent.name
          const isPassed = isRunning && agents.findIndex(a => a.name === currentAgent) > index
          
          return (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="relative"
            >
              <motion.div
                animate={{
                  scale: isActive ? 1.05 : 1,
                  boxShadow: isActive
                    ? '0 0 30px rgba(59, 130, 246, 0.5)'
                    : '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                }}
                className={`glass-effect rounded-lg p-6 transition-all duration-300 ${
                  isActive ? 'border-2 border-primary-500' : ''
                } ${isPassed ? 'border-2 border-green-500' : ''}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-4xl">{agent.icon}</span>
                  {isActive && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full"
                    />
                  )}
                  {isPassed && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
                    >
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </motion.div>
                  )}
                </div>
                
                <h3 className="text-xl font-semibold mb-1">{agent.name}</h3>
                <p className="text-sm text-gray-400">{agent.description}</p>
                
                <motion.div
                  className={`mt-4 h-1 rounded-full bg-gradient-to-r ${agent.color}`}
                  initial={{ width: 0 }}
                  animate={{ width: isActive ? '100%' : isPassed ? '100%' : '0%' }}
                  transition={{ duration: 0.5 }}
                />
              </motion.div>

              {/* Connector Arrow */}
              {index < agents.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 transform translate-x-1/2 -translate-y-1/2 z-10">
                  <motion.svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    className={`${isPassed ? 'text-green-500' : 'text-gray-600'}`}
                    animate={{ scale: isActive ? [1, 1.2, 1] : 1 }}
                    transition={{ duration: 0.5, repeat: isActive ? Infinity : 0 }}
                  >
                    <path
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </motion.svg>
                </div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Workflow Status */}
      <AnimatePresence>
        {isRunning && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mt-6 text-center"
          >
            <div className="inline-flex items-center space-x-2 glass-effect px-6 py-3 rounded-full">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full"
              />
              <span className="text-primary-400 font-medium">
                {currentAgent} Agent is working...
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default AgentWorkflow
