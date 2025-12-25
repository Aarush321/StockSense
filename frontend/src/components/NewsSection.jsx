export default function NewsSection({ news }) {
  if (!news || news.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Recent News</h3>
        <p className="text-gray-500">No recent news available.</p>
      </div>
    )
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Date unknown'
    try {
      const date = new Date(timestamp * 1000)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Date unknown'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Recent News</h3>
      <div className="space-y-4">
        {news.map((article, index) => (
          <div
            key={index}
            className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2 hover:text-blue-600">
                  {article.headline || 'No headline available'}
                </h4>
                {article.summary && (
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                    {article.summary}
                  </p>
                )}
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{article.source || 'Unknown source'}</span>
                  <span>•</span>
                  <span>{formatDate(article.date)}</span>
                </div>
              </div>
              {article.url && (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium whitespace-nowrap"
                >
                  Read More →
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

