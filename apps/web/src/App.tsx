import '@/index.css'

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-cork-50">
      <header className="bg-cork-700 text-white">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold">Cork Mobility Lab</h1>
          <p className="text-cork-100 text-sm mt-1">Agent-based traffic simulation and optimisation platform</p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-cork-900 mb-4">Welcome</h2>
          <p className="text-gray-600 mb-4">
            Cork Mobility Lab is a research-grade simulation platform for analysing and optimising 
            traffic in Cork, Ireland. This is the initial project scaffolding.
          </p>
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="bg-cork-50 p-4 rounded">
              <h3 className="font-semibold text-cork-700">Simulation</h3>
              <p className="text-sm text-gray-600 mt-2">Agent-based traffic simulation</p>
            </div>
            <div className="bg-cork-50 p-4 rounded">
              <h3 className="font-semibold text-cork-700">Analysis</h3>
              <p className="text-sm text-gray-600 mt-2">Comprehensive traffic metrics</p>
            </div>
            <div className="bg-cork-50 p-4 rounded">
              <h3 className="font-semibold text-cork-700">Optimisation</h3>
              <p className="text-sm text-gray-600 mt-2">Scenario-based optimisation</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
