import React from 'react';

function InsightsPanel({ insights }) {
  if (!insights) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-icon">🤖</span>
          <h2>4. AI Insights</h2>
        </div>
        <p className="panel-description">
          Claude AI-powered spending analysis and recommendations
        </p>
        <div className="panel-content">
          <p style={{ color: '#999' }}>No data yet. Click "Get Transactions" to fetch data.</p>
        </div>
      </div>
    );
  }

  // Handle error state
  if (insights.error) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-icon">🤖</span>
          <h2>4. AI Insights</h2>
        </div>
        <p className="panel-description">
          Claude AI-powered spending analysis and recommendations
        </p>
        <div className="panel-content">
          <div className="error-panel">
            <h3>{insights.error}</h3>
            <p>{insights.message}</p>
            <p style={{ marginTop: '15px', fontSize: '0.9rem' }}>
              To enable AI insights, set your CLAUDE_API_KEY in the .env file.
              <br />
              Get your API key from: <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer">console.anthropic.com</a>
            </p>
          </div>
        </div>
      </div>
    );
  }

  const insightData = insights.insights || {};

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-icon">🤖</span>
        <h2>4. AI Insights</h2>
      </div>
      <p className="panel-description">
        Claude AI-powered spending analysis and recommendations
      </p>
      <div className="insights-content">
        {/* Summary Section */}
        {insightData.summary && (
          <div className="insights-section">
            <h3>📊 Summary</h3>
            <div className="category-item">
              <strong>Total Spent:</strong> ${insightData.summary.total_spent?.toFixed(2)}
            </div>
            <div className="category-item">
              <strong>Transactions:</strong> {insightData.summary.transaction_count}
            </div>
            <div className="category-item">
              <strong>Average:</strong> ${insightData.summary.average_transaction?.toFixed(2)}
            </div>
          </div>
        )}

        {/* Top Categories */}
        {insightData.top_categories && insightData.top_categories.length > 0 && (
          <div className="insights-section">
            <h3>🏆 Top Spending Categories</h3>
            {insightData.top_categories.map((cat, index) => (
              <div key={index} className="category-item">
                <strong>{cat.category}:</strong> ${cat.amount?.toFixed(2)}
                ({cat.percentage?.toFixed(1)}%)
              </div>
            ))}
          </div>
        )}

        {/* Largest Transactions */}
        {insightData.largest_transactions && insightData.largest_transactions.length > 0 && (
          <div className="insights-section">
            <h3>💰 Largest Transactions</h3>
            {insightData.largest_transactions.map((txn, index) => (
              <div key={index} className="transaction-item">
                <strong>{txn.merchant}</strong> - ${txn.amount?.toFixed(2)}
                <br />
                <small style={{ color: '#666' }}>
                  {txn.date} • {txn.category}
                </small>
              </div>
            ))}
          </div>
        )}

        {/* AI Analysis */}
        {insightData.ai_analysis && (
          <div className="insights-section">
            <h3>🧠 AI Analysis</h3>
            <div className="ai-analysis">
              {insightData.ai_analysis}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {insightData.recommendations && insightData.recommendations.length > 0 && (
          <div className="insights-section">
            <h3>💡 Recommendations</h3>
            {insightData.recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                {rec}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default InsightsPanel;
