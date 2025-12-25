export default function SentimentDisplay({ sentiment }) {
  if (!sentiment) {
    return null
  }

  const reddit = sentiment.reddit || {}
  const twitter = sentiment.twitter || {}

  const SentimentBar = ({ label, positive, neutral, negative, totalMentions }) => {
    const total = positive + neutral + negative
    if (total === 0) {
      return (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">{label}</span>
            <span className="text-xs text-gray-500">No data available</span>
          </div>
        </div>
      )
    }

    const posPercent = (positive / total) * 100
    const neuPercent = (neutral / total) * 100
    const negPercent = (negative / total) * 100

    return (
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-xs text-gray-500">{totalMentions || total} mentions</span>
        </div>
        <div className="flex h-6 rounded-md overflow-hidden border border-gray-200">
          <div
            className="bg-green-500 flex items-center justify-center text-white text-xs font-semibold"
            style={{ width: `${posPercent}%` }}
            title={`${posPercent.toFixed(1)}% Positive`}
          >
            {posPercent > 10 ? `${posPercent.toFixed(0)}%` : ''}
          </div>
          <div
            className="bg-yellow-500 flex items-center justify-center text-white text-xs font-semibold"
            style={{ width: `${neuPercent}%` }}
            title={`${neuPercent.toFixed(1)}% Neutral`}
          >
            {neuPercent > 10 ? `${neuPercent.toFixed(0)}%` : ''}
          </div>
          <div
            className="bg-red-500 flex items-center justify-center text-white text-xs font-semibold"
            style={{ width: `${negPercent}%` }}
            title={`${negPercent.toFixed(1)}% Negative`}
          >
            {negPercent > 10 ? `${negPercent.toFixed(0)}%` : ''}
          </div>
        </div>
        <div className="flex gap-4 mt-1 text-xs text-gray-600">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 bg-green-500 rounded"></span>
            {positive}% Positive
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 bg-yellow-500 rounded"></span>
            {neutral}% Neutral
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 bg-red-500 rounded"></span>
            {negative}% Negative
          </span>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Social Sentiment</h3>
      
      <SentimentBar
        label="📱 Reddit"
        positive={reddit.positive || 0}
        neutral={reddit.neutral || 0}
        negative={reddit.negative || 0}
        totalMentions={reddit.totalMentions}
      />

      <SentimentBar
        label="🐦 Twitter/X"
        positive={twitter.positive || 0}
        neutral={twitter.neutral || 0}
        negative={twitter.negative || 0}
        totalMentions={twitter.totalMentions}
      />

      {(reddit.sample || twitter.sample) && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 italic">
            {reddit.sample || twitter.sample}
          </p>
        </div>
      )}
    </div>
  )
}

