import { motion } from 'framer-motion'

const phaseLabels = {
  idle: 'READY',
  parsing: 'PARSING',
  translating: 'TRANSLATING',
  executing: 'EXECUTING',
  complete: 'COMPLETE',
}

function ProcessingDots() {
  return (
    <span className="inline-flex gap-0.5 ml-1">
      {[0, 1, 2].map(i => (
        <motion.span
          key={i}
          animate={{ opacity: [0.2, 1, 0.2] }}
          transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
          style={{ color: '#00ff41' }}
        >
          .
        </motion.span>
      ))}
    </span>
  )
}

export default function Header({ phase, onRun, aiEnabled }) {
  const isRunning = phase !== 'idle' && phase !== 'complete'
  const label = phaseLabels[phase] || 'READY'

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="flex items-center justify-between px-6 py-3 border-b"
      style={{ borderColor: '#0a3d0040', background: '#0a0a0a' }}
    >
      {/* Title */}
      <div className="flex items-center gap-4">
        <h1
          className="text-2xl font-bold tracking-wider text-glow"
          style={{ color: '#00ff41' }}
        >
          PROTEUS
        </h1>
        <span
          className="text-xs tracking-widest uppercase"
          style={{ color: '#4a7a4a' }}
        >
          ENGLISH &rarr; PYTHON TRANSLATOR
        </span>
        {aiEnabled && (
          <span
            className="text-xs px-2 py-0.5 rounded border"
            style={{ color: '#39ff14', borderColor: '#39ff1440', backgroundColor: '#39ff1410' }}
          >
            AI ENABLED
          </span>
        )}
      </div>

      {/* Status + Run Button */}
      <div className="flex items-center gap-6">
        {/* Phase indicator */}
        <div className="flex items-center gap-2 text-xs">
          <span
            className={`inline-block w-2 h-2 rounded-full ${isRunning ? 'active-dot' : ''}`}
            style={{
              backgroundColor: phase === 'complete' ? '#00ff41' : isRunning ? '#39ff14' : '#003b00',
            }}
          />
          <span style={{ color: isRunning ? '#00ff41' : '#4a7a4a' }}>
            {label}
            {isRunning && <ProcessingDots />}
          </span>
        </div>

        {/* Run button */}
        <motion.button
          onClick={onRun}
          disabled={isRunning}
          whileHover={!isRunning ? { scale: 1.05 } : {}}
          whileTap={!isRunning ? { scale: 0.95 } : {}}
          className={`px-5 py-2 text-sm font-bold tracking-wider border rounded cursor-pointer transition-colors duration-200 ${
            isRunning ? 'run-pulse cursor-not-allowed opacity-70' : 'hover:bg-[#003b00]/50'
          }`}
          style={{
            color: '#00ff41',
            borderColor: '#00ff41',
            backgroundColor: isRunning ? '#003b0040' : 'transparent',
          }}
        >
          {isRunning ? '/// RUNNING' : '\u25B6 RUN PROGRAM'}
        </motion.button>
      </div>
    </motion.header>
  )
}
