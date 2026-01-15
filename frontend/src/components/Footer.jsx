import { motion } from 'framer-motion'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  const footerLinks = [
    { label: 'Documentation', href: '#' },
    { label: 'GitHub', href: '#' },
    { label: 'Issues', href: '#' },
    { label: 'Contact', href: '#' },
  ]

  const features = [
    { icon: '🤖', label: 'Multi-Agent' },
    { icon: '⚡', label: 'Optimized' },
    { icon: '🔒', label: 'Reliable' },
    { icon: '📊', label: 'Scalable' },
  ]

  return (
    <footer className="glass-effect border-t border-white/10 mt-16">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="space-y-8"
        >
          {/* Features Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pb-8 border-b border-white/10">
            {features.map((feature, index) => (
              <motion.div
                key={feature.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="text-2xl mb-2">{feature.icon}</div>
                <p className="text-sm text-gray-400">{feature.label}</p>
              </motion.div>
            ))}
          </div>

          {/* Footer Content */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Brand Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
            >
              <div className="flex items-center space-x-2 mb-3">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-white"
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
                </div>
                <span className="text-lg font-bold text-white">Intellixa</span>
              </div>
              <p className="text-sm text-gray-400">
                Enterprise-grade multi-agent AI orchestration platform for reliable autonomous systems.
              </p>
            </motion.div>

            {/* Quick Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
            >
              <h3 className="font-semibold text-white mb-4">Quick Links</h3>
              <ul className="space-y-2">
                {footerLinks.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-gray-400 hover:text-primary-400 transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <h3 className="font-semibold text-white mb-4">By The Numbers</h3>
              <div className="space-y-2">
                <p className="text-sm text-gray-400">
                  <span className="text-primary-400 font-semibold">67%</span> Fewer API Calls
                </p>
                <p className="text-sm text-gray-400">
                  <span className="text-primary-400 font-semibold">6</span> Specialized Agents
                </p>
                <p className="text-sm text-gray-400">
                  <span className="text-primary-400 font-semibold">100%</span> Autonomous
                </p><p className="text-sm text-gray-400">
                  <span className="text-primary-400 font-semibold">67% </span> Cost Reduction
                </p>
              </div>
            </motion.div>
          </div>

          {/* Bottom Bar */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            viewport={{ once: true }}
            className="pt-8 border-t border-white/10"
          >
            <p className="text-sm text-gray-500 text-center">
              © {currentYear} Intellixa. All rights reserved.
            </p>
          </motion.div>
        </motion.div>
      </div>
    </footer>
  )
}

export default Footer
