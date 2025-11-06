import React from 'react';

function MaskedPanel({ data }) {
  if (!data) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-icon">🔒</span>
          <h2>3. Masked Data</h2>
        </div>
        <p className="panel-description">
          PII fields masked for security and privacy
        </p>
        <div className="panel-content">
          <p style={{ color: '#999' }}>No data yet. Click "Get Transactions" to fetch data.</p>
        </div>
      </div>
    );
  }

  // Highlight masked fields in the JSON
  const highlightMasked = (obj) => {
    const str = JSON.stringify(obj, null, 2);
    // Highlight patterns like *** or ****
    return str.split('\n').map((line, index) => {
      if (line.includes('***') || /\*{4,}/.test(line)) {
        return (
          <div key={index} style={{ background: '#fff3cd' }}>
            {line}
          </div>
        );
      }
      return <div key={index}>{line}</div>;
    });
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-icon">🔒</span>
        <h2>3. Masked Data</h2>
      </div>
      <p className="panel-description">
        PII fields masked for security and privacy (highlighted)
      </p>
      <div className="panel-content">
        <pre style={{ margin: 0 }}>{highlightMasked(data)}</pre>
      </div>
    </div>
  );
}

export default MaskedPanel;
