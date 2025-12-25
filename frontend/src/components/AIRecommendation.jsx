export default function AIRecommendation({ recommendation }) {
  if (!recommendation) {
    return null
  }

  const { recommendation: rec, reasoning, riskLevel, note } = recommendation

  const getRecommendationColor = () => {
    const recUpper = rec?.toUpperCase() || ''
    if (recUpper.includes('BUY')) return 'bg-green-50 border-green-500'
    if (recUpper.includes('HOLD')) return 'bg-yellow-50 border-yellow-500'
    return 'bg-red-50 border-red-500'
  }

  const getRecommendationIcon = () => {
    const recUpper = rec?.toUpperCase() || ''
    if (recUpper.includes('BUY')) return '✅'
    if (recUpper.includes('HOLD')) return '⏸️'
    return '❌'
  }

  const getRiskColor = () => {
    if (riskLevel === 'Low') return 'text-green-600 bg-green-100'
    if (riskLevel === 'High') return 'text-red-600 bg-red-100'
    return 'text-yellow-600 bg-yellow-100'
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${getRecommendationColor()}`}>
      <div className="flex items-start gap-4 mb-4">
        <span className="text-4xl">{getRecommendationIcon()}</span>
        <div className="flex-1">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            AI Recommendation: {rec || 'N/A'}
          </h3>
          {riskLevel && (
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getRiskColor()}`}>
              Risk Level: {riskLevel}
            </span>
          )}
        </div>
      </div>

      {reasoning && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Reasoning:</h4>
          <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
            {reasoning}
          </div>
        </div>
      )}

      {note && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 italic">{note}</p>
        </div>
      )}
    </div>
  )
}

