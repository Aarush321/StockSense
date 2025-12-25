import { useState, useEffect } from 'react'
import { analyzeStock } from '../services/api'

export default function StockCard({ symbol, onSelect }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [symbol])

  const loadData = async () => {
    try {
      setLoading(true)
      const analysis = await analyzeStock(symbol)
      setData(analysis)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-red-200">
        <h3 className="font-semibold text-gray-900 mb-1">{symbol}</h3>
        <p className="text-sm text-red-600">Failed to load</p>
      </div>
    )
  }

  const company = data?.company
  const sentiment = data?.sentiment
  const aiRec = data?.ai_recommendation

  // Calculate overall sentiment
  const redditPos = sentiment?.reddit?.positive || 0
  const twitterPos = sentiment?.twitter?.positive || 0
  const avgSentiment = (redditPos + twitterPos) / 2

  const getSentimentEmoji = () => {
    if (avgSentiment >= 60) return '😊'
    if (avgSentiment >= 40) return '😐'
    return '😟'
  }

  const getSentimentColor = () => {
    if (avgSentiment >= 60) return 'text-green-600'
    if (avgSentiment >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getRecommendationColor = () => {
    const rec = aiRec?.recommendation?.toUpperCase() || ''
    if (rec.includes('BUY')) return 'bg-green-100 text-green-800'
    if (rec.includes('HOLD')) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div
      onClick={() => onSelect(symbol)}
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-blue-500"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{company?.name || symbol}</h3>
          <p className="text-sm text-gray-500">{symbol}</p>
        </div>
        <span className="text-2xl">{getSentimentEmoji()}</span>
      </div>

      <div className="mb-4">
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl font-bold text-gray-900">
            ${company?.currentPrice?.toFixed(2) || '0.00'}
          </span>
          <span
            className={`text-sm font-semibold ${
              (company?.changePercent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {(company?.changePercent || 0) >= 0 ? '↑' : '↓'} {Math.abs(company?.changePercent || 0).toFixed(2)}%
          </span>
        </div>
        <p className="text-xs text-gray-500">
          {company?.sector || 'N/A'}
        </p>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-600 mb-1">Sentiment</p>
          <p className={`text-sm font-semibold ${getSentimentColor()}`}>
            {avgSentiment.toFixed(0)}% Positive
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">AI Recommendation</p>
          <span className={`text-xs px-2 py-1 rounded-full font-semibold ${getRecommendationColor()}`}>
            {aiRec?.recommendation || 'N/A'}
          </span>
        </div>
      </div>
    </div>
  )
}

