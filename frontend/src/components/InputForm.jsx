import { useState } from 'react'
import { motion } from 'framer-motion'

const InputForm = ({ onSubmit, isRunning }) => {
  const [goal, setGoal] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (goal) {
      onSubmit(goal)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="agent-card"
    >
      <h2 className="text-2xl font-bold mb-6">Start New Session</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="goal" className="block text-sm font-medium text-gray-300 mb-2">
            Goal / Task Description
          </label>
          <textarea
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Describe your task or goal for the AI agents..."
            className="input-field resize-none h-32"
            disabled={isRunning}
            required
          />
        </div>

        <motion.button
          type="submit"
          disabled={isRunning || !goal}
          className="btn-primary w-full"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isRunning ? (
            <span className="flex items-center justify-center">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
              />
              Processing...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              Execute Workflow
            </span>
          )}
        </motion.button>
      </form>

      {/* Example Commands */}
      <div className="mt-6 pt-6 border-t border-white/10">
        <p className="text-sm text-gray-400 mb-3">Example goals:</p>
        <div className="space-y-2">
          {[
            'Research and create a comprehensive report on AI trends in 2026',
            'Design a system architecture for a microservices platform',
            'Write a technical blog post about multi-agent systems',
          ].map((example, index) => (
            <motion.button
              key={index}
              type="button"
              onClick={() => setGoal(example)}
              disabled={isRunning}
              className="text-xs text-left text-gray-500 hover:text-primary-400 transition-colors block w-full"
              whileHover={{ x: 5 }}
            >
              → {example}
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

export default InputForm
