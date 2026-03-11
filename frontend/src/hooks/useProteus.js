import { useState, useCallback, useRef, useEffect } from 'react'

const API_BASE = 'http://localhost:8000'

const PHASES = {
  IDLE: 'idle',
  PARSING: 'parsing',
  TRANSLATING: 'translating',
  EXECUTING: 'executing',
  COMPLETE: 'complete',
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export function useProteus() {
  const [englishCode, setEnglishCode] = useState('')
  const [pythonCode, setPythonCode] = useState([])
  const [variables, setVariables] = useState([])
  const [output, setOutput] = useState([])
  const [phase, setPhase] = useState(PHASES.IDLE)
  const [translations, setTranslations] = useState([])
  const [explanations, setExplanations] = useState([])
  const [currentLine, setCurrentLine] = useState(-1)
  const [error, setError] = useState(null)
  const [aiEnabled, setAiEnabled] = useState(false)
  const abortRef = useRef(false)

  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then(r => r.json())
      .then(data => setAiEnabled(data.ai_enabled))
      .catch(() => setAiEnabled(false))
  }, [])

  const addOutput = useCallback((line, type = 'info') => {
    setOutput(prev => [...prev, { text: line, type, id: Date.now() + Math.random() }])
  }, [])

  const runProgram = useCallback(async () => {
    if (phase !== PHASES.IDLE && phase !== PHASES.COMPLETE) return
    if (!englishCode.trim()) return

    abortRef.current = false
    setPythonCode([])
    setVariables([])
    setOutput([])
    setTranslations([])
    setExplanations([])
    setCurrentLine(-1)
    setError(null)

    // Phase 1: Parsing
    setPhase(PHASES.PARSING)
    addOutput('> Initializing Proteus engine...', 'system')
    await sleep(400)
    addOutput('> Parsing instructions...', 'system')
    await sleep(800)

    if (abortRef.current) return

    // Phase 2: Translating
    setPhase(PHASES.TRANSLATING)
    addOutput('> Translating to Python...', 'system')

    let translateData
    try {
      const response = await fetch(`${API_BASE}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: englishCode }),
      })

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }

      translateData = await response.json()
    } catch (err) {
      setError(err.message)
      addOutput(`> ERROR: ${err.message}`, 'error')
      addOutput('> Connection to backend failed. Is the server running on port 8000?', 'error')
      setPhase(PHASES.IDLE)
      return
    }

    if (abortRef.current) return

    // Animate translations appearing one by one
    const lines = translateData.translations || []
    for (let i = 0; i < lines.length; i++) {
      if (abortRef.current) return
      setTranslations(prev => [...prev, lines[i]])
      setPythonCode(prev => [...prev, lines[i].python])
      await sleep(200)
    }

    // Animate explanations appearing one by one
    const explainData = translateData.explanations || []
    for (let i = 0; i < explainData.length; i++) {
      if (abortRef.current) return
      setExplanations(prev => [...prev, explainData[i]])
      await sleep(150)
    }

    addOutput('> Translation complete.', 'system')
    await sleep(300)

    if (abortRef.current) return

    // Phase 3: Executing
    setPhase(PHASES.EXECUTING)
    addOutput('> Executing program...', 'system')

    let runData
    try {
      const response = await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: englishCode }),
      })

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }

      runData = await response.json()
    } catch (err) {
      setError(err.message)
      addOutput(`> ERROR: ${err.message}`, 'error')
      setPhase(PHASES.IDLE)
      return
    }

    if (abortRef.current) return

    // Animate execution step by step using variable snapshots
    const snapshots = runData.variables || []
    for (let i = 0; i < snapshots.length; i++) {
      if (abortRef.current) return
      const snapshot = snapshots[i]
      setCurrentLine(snapshot.step ?? i)

      if (snapshot.variables) {
        setVariables(prev => {
          const updated = []
          const existing = new Map(prev.map(v => [v.name, v]))

          for (const [name, value] of Object.entries(snapshot.variables)) {
            const type = typeof value === 'number'
              ? (Number.isInteger(value) ? 'int' : 'float')
              : typeof value === 'string'
              ? 'str'
              : typeof value === 'boolean'
              ? 'bool'
              : Array.isArray(value)
              ? 'list'
              : 'object'

            const existingVar = existing.get(name)
            const changed = existingVar && JSON.stringify(existingVar.value) !== JSON.stringify(value)

            updated.push({
              name,
              value,
              type,
              isNew: !existingVar,
              changed,
              id: existingVar?.id || `${name}-${Date.now()}`,
            })
          }
          return updated
        })
      }

      await sleep(400)
    }

    // Display program output line by line
    if (runData.output) {
      const outputLines = runData.output.split('\n')
      for (const line of outputLines) {
        if (line.trim()) {
          addOutput(line, 'output')
          await sleep(100)
        }
      }
    }

    if (runData.error) {
      addOutput(`> Runtime Error: ${runData.error}`, 'error')
    }

    setCurrentLine(-1)
    addOutput('> Program complete.', 'system')
    setPhase(PHASES.COMPLETE)
  }, [englishCode, phase, addOutput])

  const reset = useCallback(() => {
    abortRef.current = true
    setPythonCode([])
    setVariables([])
    setOutput([])
    setTranslations([])
    setExplanations([])
    setCurrentLine(-1)
    setError(null)
    setPhase(PHASES.IDLE)
  }, [])

  return {
    englishCode,
    setEnglishCode,
    pythonCode,
    variables,
    output,
    phase,
    translations,
    explanations,
    currentLine,
    error,
    runProgram,
    reset,
    aiEnabled,
  }
}
