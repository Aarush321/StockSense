import { useState, useEffect } from 'react'
import { StockProvider } from './context/StockContext'
import SearchBar from './components/SearchBar'
import Dashboard from './components/Dashboard'
import StockAnalysis from './components/StockAnalysis'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('search')
  const [selectedSymbol, setSelectedSymbol] = useState(null)

  return (
    <StockProvider>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">
                📈 Stock Analysis Tool
              </h1>
              <nav className="flex gap-4">
                <button
                  onClick={() => {
                    setCurrentView('search')
                    setSelectedSymbol(null)
                  }}
                  className={`px-4 py-2 rounded-md ${
                    currentView === 'search'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Search
                </button>
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className={`px-4 py-2 rounded-md ${
                    currentView === 'dashboard'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Dashboard
                </button>
              </nav>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {currentView === 'search' && (
            <div>
              <SearchBar onAnalysisComplete={(symbol) => {
                setSelectedSymbol(symbol)
                setCurrentView('analysis')
              }} />
            </div>
          )}

          {currentView === 'dashboard' && (
            <Dashboard
              onStockSelect={(symbol) => {
                setSelectedSymbol(symbol)
                setCurrentView('analysis')
              }}
            />
          )}

          {currentView === 'analysis' && selectedSymbol && (
            <StockAnalysis symbol={selectedSymbol} />
          )}
        </main>
      </div>
    </StockProvider>
  )
}

export default App

