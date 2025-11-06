import React from 'react';

function SoapPanel({ data }) {
  if (!data) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-icon">📡</span>
          <h2>1. Raw SOAP Response</h2>
        </div>
        <p className="panel-description">
          Original XML response from the legacy SOAP service
        </p>
        <div className="panel-content">
          <p style={{ color: '#999' }}>No data yet. Click "Get Transactions" to fetch data.</p>
        </div>
      </div>
    );
  }

  // Format XML for better readability
  const formatXml = (xml) => {
    try {
      const formatted = xml
        .replace(/></g, '>\n<')
        .split('\n')
        .map((line, index) => {
          const indent = '  '.repeat(Math.max(0, line.split('<').length - line.split('</').length - 1));
          return indent + line.trim();
        })
        .join('\n');
      return formatted;
    } catch (e) {
      return xml;
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-icon">📡</span>
        <h2>1. Raw SOAP Response</h2>
      </div>
      <p className="panel-description">
        Original XML response from the legacy SOAP service
      </p>
      <div className="panel-content">
        <pre>{formatXml(data)}</pre>
      </div>
    </div>
  );
}

export default SoapPanel;
