import { createContext, useContext, useState, useEffect } from 'react'
import { getStarredStocks, starStock, unstarStock } from '../services/api'

const StockContext = createContext()

export function StockProvider({ children }) {
  const [starredStocks, setStarredStocks] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadStarredStocks()
  }, [])

  const loadStarredStocks = async () => {
    try {
      setLoading(true)
      const stocks = await getStarredStocks()
      setStarredStocks(stocks)
    } catch (error) {
      console.error('Failed to load starred stocks:', error)
    } finally {
      setLoading(false)
    }
  }

  const addStarredStock = async (symbol) => {
    try {
      await starStock(symbol)
      await loadStarredStocks()
    } catch (error) {
      console.error('Failed to star stock:', error)
      throw error
    }
  }

  const removeStarredStock = async (symbol) => {
    try {
      await unstarStock(symbol)
      await loadStarredStocks()
    } catch (error) {
      console.error('Failed to unstar stock:', error)
      throw error
    }
  }

  const isStarred = (symbol) => {
    return starredStocks.some(stock => stock.symbol === symbol.toUpperCase())
  }

  return (
    <StockContext.Provider
      value={{
        starredStocks,
        loading,
        addStarredStock,
        removeStarredStock,
        isStarred,
        refreshStarredStocks: loadStarredStocks
      }}
    >
      {children}
    </StockContext.Provider>
  )
}

export function useStock() {
  const context = useContext(StockContext)
  if (!context) {
    throw new Error('useStock must be used within StockProvider')
  }
  return context
}

