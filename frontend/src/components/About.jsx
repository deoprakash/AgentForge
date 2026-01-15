import { motion } from 'framer-motion'
import Header from './Header'
import BenchmarkMetrics from './BenchmarkMetrics'
import Footer from './Footer'

const About = ({ onBack }) => {
  return (
    <>
      <Header currentPage="about" onBack={onBack} />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-8"
        >
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="text-center space-y-6 mb-12"
          >
            <div className="relative py-4">
              <h1 className="text-7xl md:text-8xl font-black bg-gradient-to-r from-primary-300 via-primary-500 to-primary-700 bg-clip-text text-transparent leading-tight">
                About Intellixa
              </h1>
              {/* Glow effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-primary-600/20 blur-3xl -z-10 opacity-50"></div>
            </div>
          </motion.div>

          {/* Description Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="agent-card mb-8"
          >
            <h2 className="text-3xl font-bold mb-6">What is Intellixa?</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                Intellixa is an <span className="text-primary-400 font-semibold">enterprise-grade multi-agent AI orchestration platform</span> designed for production-ready autonomous systems. It demonstrates robust, scalable, and well-governed agent workflows built using modern backend and AI engineering practices.
              </p>
              <p>
                The platform addresses critical challenges in LLM-based systems including uncontrolled API usage, hallucinated outputs, and tightly coupled architectures. Intellixa introduces <span className="text-primary-400 font-semibold">governed multi-agent workflows</span> with embedded quality validation.
              </p>
            </div>
          </motion.div>

          {/* Key Features */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="agent-card mb-8"
          >
            <h2 className="text-3xl font-bold mb-6">Key Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                {
                  icon: '🤖',
                  title: 'Multi-Agent Pipeline',
                  desc: '6 specialized agents working in orchestrated sequence',
                },
                {
                  icon: '⚡',
                  title: '67% Fewer API Calls',
                  desc: 'Optimized LLM usage compared to traditional approaches',
                },
                {
                  icon: '✅',
                  title: 'Quality Validation',
                  desc: 'Confidence & hallucination checking before output',
                },
                {
                  icon: '🔄',
                  title: 'Automatic Refinement',
                  desc: 'Self-correcting loops ensure high-quality results',
                },
                {
                  icon: '💾',
                  title: 'State Management',
                  desc: 'Persistent context with MongoDB integration',
                },
                {
                  icon: '🔒',
                  title: 'Enterprise-Ready',
                  desc: 'Rate-limit aware, fault-tolerant architecture',
                },
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="glass-effect p-4 rounded-lg"
                >
                  <div className="text-3xl mb-2">{feature.icon}</div>
                  <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-400">{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Agent Pipeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="agent-card mb-8"
          >
            <h2 className="text-3xl font-bold mb-6">The Intellixa Pipeline</h2>
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              {[
                { name: 'CEO', emoji: '👔', desc: 'Strategic Planning' },
                { name: 'Research', emoji: '🔍', desc: 'Data Gathering' },
                { name: 'Developer', emoji: '💻', desc: 'Code Generation' },
                { name: 'Writer', emoji: '✍️', desc: 'Content Creation' },
                { name: 'Confidence', emoji: '✅', desc: 'Quality Check' },
                { name: 'Reviewer', emoji: '🔎', desc: 'Final Review' },
              ].map((agent, index) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="flex flex-col items-center"
                >
                  <div className="text-4xl mb-2">{agent.emoji}</div>
                  <p className="font-semibold text-white">{agent.name}</p>
                  <p className="text-xs text-gray-400">{agent.desc}</p>
                  {index < 5 && <div className="text-primary-500 text-xl mt-2 hidden md:block">→</div>}
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Benchmark Section */}
          <BenchmarkMetrics />
        </motion.div>
      </main>

      <Footer />
    </>
  )
}

export default About
