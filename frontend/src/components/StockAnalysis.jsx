import { useState, useEffect } from 'react'
import { analyzeStock, refreshStock } from '../services/api'
import { useStock } from '../context/StockContext'
import NewsSection from './NewsSection'
import SentimentDisplay from './SentimentDisplay'
import AnalystOpinions from './AnalystOpinions'
import AIRecommendation from './AIRecommendation'

export default function StockAnalysis({ symbol }) {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const { isStarred, addStarredStock, removeStarredStock } = useStock()

  useEffect(() => {
    loadAnalysis()
  }, [symbol])

  const loadAnalysis = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await analyzeStock(symbol)
      setAnalysis(data)
    } catch (err) {
      setError(err.message || 'Failed to load analysis')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      const data = await refreshStock(symbol)
      setAnalysis(data)
    } catch (err) {
      setError(err.message || 'Failed to refresh data')
    } finally {
      setRefreshing(false)
    }
  }

  const handleStarToggle = async () => {
    try {
      if (isStarred(symbol)) {
        await removeStarredStock(symbol)
      } else {
        await addStarredStock(symbol)
      }
    } catch (err) {
      alert('Failed to update starred stocks: ' + err.message)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Analyzing {symbol}...</p>
          <p className="text-sm text-gray-500 mt-2">This may take 10-20 seconds</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error</h3>
        <p className="text-red-600">{error}</p>
        <button
          onClick={loadAnalysis}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (!analysis) {
    return null
  }

  const { company, news, sentiment, analyst, ai_recommendation } = analysis

  return (
    <div className="space-y-6">
      {/* Header with company info and actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-3xl font-bold text-gray-900">{company?.name || symbol}</h2>
              <span className="text-xl text-gray-500">({symbol})</span>
              <button
                onClick={handleStarToggle}
                className="text-2xl hover:scale-110 transition-transform"
                title={isStarred(symbol) ? 'Remove from starred' : 'Add to starred'}
              >
                {isStarred(symbol) ? '⭐' : '☆'}
              </button>
            </div>
            <div className="flex flex-wrap gap-4 text-sm text-gray-600">
              <span>
                <span className="font-semibold">Sector:</span> {company?.sector || 'N/A'}
              </span>
              {company?.yearsPublic && (
                <span>
                  <span className="font-semibold">Public Since:</span> {company.yearsPublic} years
                </span>
              )}
            </div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50 flex items-center gap-2"
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
              '🔄 Refresh'
            )}
          </button>
        </div>

        <div className="flex items-baseline gap-4">
          <span className="text-4xl font-bold text-gray-900">
            ${company?.currentPrice?.toFixed(2) || '0.00'}
          </span>
          <span
            className={`text-2xl font-semibold ${
              (company?.changePercent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {(company?.changePercent || 0) >= 0 ? '↑' : '↓'} {Math.abs(company?.changePercent || 0).toFixed(2)}%
          </span>
        </div>
      </div>

      {/* AI Recommendation */}
      {ai_recommendation && (
        <AIRecommendation recommendation={ai_recommendation} />
      )}

      {/* Social Sentiment */}
      {sentiment && (
        <SentimentDisplay sentiment={sentiment} />
      )}

      {/* Analyst Opinions */}
      {analyst && (
        <AnalystOpinions analyst={analyst} />
      )}

      {/* Recent News */}
      {news && news.length > 0 && (
        <NewsSection news={news} />
      )}
    </div>
  )
}

