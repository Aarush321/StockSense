import { useState, useEffect } from 'react'
import { useStock } from '../context/StockContext'
import { refreshStock } from '../services/api'
import StockCard from './StockCard'

export default function Dashboard({ onStockSelect }) {
  const { starredStocks, loading, refreshStarredStocks } = useStock()
  const [refreshing, setRefreshing] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(5) // minutes

  useEffect(() => {
    if (autoRefresh && starredStocks.length > 0) {
      const interval = setInterval(() => {
        refreshAllStocks()
      }, refreshInterval * 60 * 1000)

      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval, starredStocks.length])

  const refreshAllStocks = async () => {
    setRefreshing(true)
    try {
      // Refresh each starred stock
      for (const stock of starredStocks) {
        try {
          await refreshStock(stock.symbol)
        } catch (err) {
          console.error(`Failed to refresh ${stock.symbol}:`, err)
        }
      }
      await refreshStarredStocks()
    } finally {
      setRefreshing(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    )
  }

  return (
    <div>
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Starred Stocks</h2>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-700">Auto-refresh</span>
            </label>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              disabled={!autoRefresh}
            >
              <option value={1}>Every 1 minute</option>
              <option value={5}>Every 5 minutes</option>
              <option value={10}>Every 10 minutes</option>
              <option value={30}>Every 30 minutes</option>
            </select>
            <button
              onClick={refreshAllStocks}
              disabled={refreshing}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {refreshing ? (
                <>
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Refreshing...
                </>
              ) : (
                '🔄 Refresh All'
              )}
            </button>
          </div>
        </div>
        {starredStocks.length === 0 && (
          <p className="text-gray-500 text-center py-8">
            No starred stocks yet. Search for a stock and click the star icon to save it here.
          </p>
        )}
      </div>

      {starredStocks.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {starredStocks.map((stock) => (
            <StockCard
              key={stock.symbol}
              symbol={stock.symbol}
              onSelect={onStockSelect}
            />
          ))}
        </div>
      )}
    </div>
  )
}

