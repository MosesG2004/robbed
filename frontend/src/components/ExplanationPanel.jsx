import { useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import PanelWrapper from './PanelWrapper'

function ExplanationRow({ item, isCurrent, index }) {
  const rowRef = useRef(null)

  useEffect(() => {
    if (isCurrent && rowRef.current) {
      rowRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [isCurrent])

  return (
    <motion.div
      ref={rowRef}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05, ease: 'easeOut' }}
      className="relative rounded"
      style={{
        background: isCurrent
          ? 'linear-gradient(90deg, #00ff4118, transparent)'
          : 'transparent',
        boxShadow: isCurrent ? 'inset 3px 0 0 #00ff41' : 'none',
        padding: '6px 4px',
        marginBottom: '4px',
        borderRadius: '2px',
      }}
    >
      <div className="flex items-start gap-3">
        {/* Line number */}
        <span
          className="select-none text-right shrink-0 font-mono text-[13px]"
          style={{
            color: isCurrent ? '#00ff4180' : '#003b00',
            minWidth: '28px',
          }}
        >
          {item.line}
        </span>

        {/* Code + explanation */}
        <div className="flex-1 min-w-0">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="font-mono text-[13px] whitespace-pre"
            style={{ color: '#00ff41' }}
          >
            {item.python}
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="text-[12px] mt-0.5 leading-snug"
            style={{ color: '#4a7a4a', fontWeight: 400 }}
          >
            {item.explanation}
          </motion.div>
        </div>
      </div>

      {/* Glow pulse on current line */}
      {isCurrent && (
        <motion.div
          className="absolute inset-0 pointer-events-none rounded"
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          style={{ background: 'linear-gradient(90deg, #00ff4108, transparent)' }}
        />
      )}
    </motion.div>
  )
}

export default function ExplanationPanel({ explanations, currentLine, active }) {
  const scrollRef = useRef(null)

  return (
    <PanelWrapper title="CODE EXPLANATION" delay={0.3} active={active}>
      <div ref={scrollRef} className="h-full overflow-auto">
        {explanations.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <span className="text-xs italic" style={{ color: '#003b00' }}>
              Explanations will appear here...
            </span>
          </div>
        ) : (
          <AnimatePresence>
            {explanations.map((item, i) => (
              <ExplanationRow
                key={`explain-${i}`}
                item={item}
                isCurrent={currentLine === item.line - 1}
                index={i}
              />
            ))}
          </AnimatePresence>
        )}
      </div>
    </PanelWrapper>
  )
}
