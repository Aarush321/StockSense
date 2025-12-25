export default function AnalystOpinions({ analyst }) {
  if (!analyst) {
    return null
  }

  const { buyCount, holdCount, sellCount, averagePriceTarget, highPriceTarget, lowPriceTarget, recommendationKey } = analyst

  const total = buyCount + holdCount + sellCount
  const buyPercent = total > 0 ? (buyCount / total) * 100 : 0
  const holdPercent = total > 0 ? (holdCount / total) * 100 : 0
  const sellPercent = total > 0 ? (sellCount / total) * 100 : 0

  const getRecommendationText = () => {
    if (buyCount > sellCount * 2) return 'Strong Buy'
    if (buyCount > sellCount) return 'Buy'
    if (sellCount > buyCount) return 'Sell'
    return 'Hold'
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Professional Analyst Opinions</h3>
      
      {total > 0 ? (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600 mb-1">{buyCount}</div>
              <div className="text-sm text-gray-600">Buy</div>
              <div className="text-xs text-gray-500 mt-1">{buyPercent.toFixed(0)}%</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-3xl font-bold text-yellow-600 mb-1">{holdCount}</div>
              <div className="text-sm text-gray-600">Hold</div>
              <div className="text-xs text-gray-500 mt-1">{holdPercent.toFixed(0)}%</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-3xl font-bold text-red-600 mb-1">{sellCount}</div>
              <div className="text-sm text-gray-600">Sell</div>
              <div className="text-xs text-gray-500 mt-1">{sellPercent.toFixed(0)}%</div>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Recommendation</span>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                {getRecommendationText()}
              </span>
            </div>
          </div>
        </>
      ) : (
        <p className="text-gray-500 mb-4">No analyst ratings available</p>
      )}

      {averagePriceTarget && (
        <div className="border-t border-gray-200 pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Price Targets</h4>
          <div className="grid grid-cols-3 gap-4">
            {lowPriceTarget && (
              <div>
                <div className="text-xs text-gray-500 mb-1">Low Target</div>
                <div className="text-lg font-semibold text-gray-900">${lowPriceTarget.toFixed(2)}</div>
              </div>
            )}
            <div>
              <div className="text-xs text-gray-500 mb-1">Average Target</div>
              <div className="text-lg font-semibold text-blue-600">${averagePriceTarget.toFixed(2)}</div>
            </div>
            {highPriceTarget && (
              <div>
                <div className="text-xs text-gray-500 mb-1">High Target</div>
                <div className="text-lg font-semibold text-gray-900">${highPriceTarget.toFixed(2)}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

