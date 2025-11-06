import React from 'react';

function JsonPanel({ data }) {
  if (!data) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-icon">🔄</span>
          <h2>2. Converted JSON</h2>
        </div>
        <p className="panel-description">
          SOAP XML transformed to modern JSON format
        </p>
        <div className="panel-content">
          <p style={{ color: '#999' }}>No data yet. Click "Get Transactions" to fetch data.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-icon">🔄</span>
        <h2>2. Converted JSON</h2>
      </div>
      <p className="panel-description">
        SOAP XML transformed to modern JSON format (unmasked)
      </p>
      <div className="panel-content">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  );
}

export default JsonPanel;
