import Header from './components/Header'
import HumanTerminal from './components/HumanTerminal'
import PythonPanel from './components/PythonPanel'
import VariableMemory from './components/VariableMemory'
import OutputConsole from './components/OutputConsole'
import { useProteus } from './hooks/useProteus'

function App() {
  const {
    englishCode,
    setEnglishCode,
    pythonCode,
    variables,
    output,
    phase,
    currentLine,
    runProgram,
    aiEnabled,
  } = useProteus()

  const isTranslating = phase === 'translating' || phase === 'parsing'
  const isExecuting = phase === 'executing'

  return (
    <div className="scanlines h-screen w-screen flex flex-col overflow-hidden" style={{ background: '#0a0a0a' }}>
      <Header phase={phase} onRun={runProgram} aiEnabled={aiEnabled} />

      <main
        className="flex-1 grid gap-2 p-2 min-h-0"
        style={{
          gridTemplateColumns: '1fr 1fr',
          gridTemplateRows: '1fr 1fr',
        }}
      >
        <HumanTerminal
          value={englishCode}
          onChange={setEnglishCode}
          active={isTranslating}
        />
        <PythonPanel
          pythonCode={pythonCode}
          currentLine={currentLine}
          active={isTranslating || pythonCode.length > 0}
        />
        <VariableMemory
          variables={variables}
          active={isExecuting || variables.length > 0}
        />
        <OutputConsole
          output={output}
          active={output.length > 0}
        />
      </main>
    </div>
  )
}

export default App
