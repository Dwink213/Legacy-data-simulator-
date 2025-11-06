import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import SoapPanel from './components/SoapPanel';
import JsonPanel from './components/JsonPanel';
import MaskedPanel from './components/MaskedPanel';
import InsightsPanel from './components/InsightsPanel';

function App() {
  const [customerId, setCustomerId] = useState('42');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // State for each panel
  const [soapData, setSoapData] = useState(null);
  const [jsonData, setJsonData] = useState(null);
  const [maskedData, setMaskedData] = useState(null);
  const [insights, setInsights] = useState(null);

  const fetchTransactions = async () => {
    if (!customerId || customerId < 1) {
      setError('Please enter a valid customer ID');
      return;
    }

    setLoading(true);
    setError(null);
    setSoapData(null);
    setJsonData(null);
    setMaskedData(null);
    setInsights(null);

    try {
      // Fetch raw SOAP/JSON data
      const rawResponse = await axios.get(
        `http://localhost:5001/api/transactions/${customerId}/raw`
      );

      if (rawResponse.data.success) {
        setSoapData(rawResponse.data.soap_xml);
        setJsonData(rawResponse.data.json_data);
      }

      // Fetch masked data
      const maskedResponse = await axios.get(
        `http://localhost:5001/api/transactions/${customerId}`
      );

      if (maskedResponse.data.success) {
        setMaskedData(maskedResponse.data.data);

        // Fetch AI insights
        try {
          const insightsResponse = await axios.post(
            'http://localhost:5001/api/insights',
            { customer_data: maskedResponse.data.data }
          );

          if (insightsResponse.data.success) {
            setInsights(insightsResponse.data.insights);
          }
        } catch (insightError) {
          console.error('Error fetching insights:', insightError);
          setInsights({
            error: 'AI insights unavailable',
            message: 'Claude API key not configured'
          });
        }
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.response?.data?.error || err.message || 'Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchTransactions();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔄 SOAP-to-REST Transaction Viewer</h1>
        <p className="subtitle">Legacy API Transformation Portfolio Project</p>
      </header>

      <div className="container">
        <div className="search-section">
          <form onSubmit={handleSubmit} className="search-form">
            <div className="input-group">
              <label htmlFor="customerId">Customer ID:</label>
              <input
                id="customerId"
                type="number"
                min="1"
                max="100"
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                placeholder="Enter customer ID (1-100)"
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Loading...' : 'Get Transactions'}
              </button>
            </div>
          </form>

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Fetching transaction data...</p>
          </div>
        )}

        {!loading && (soapData || jsonData || maskedData || insights) && (
          <div className="panels-grid">
            <SoapPanel data={soapData} />
            <JsonPanel data={jsonData} />
            <MaskedPanel data={maskedData} />
            <InsightsPanel insights={insights} />
          </div>
        )}

        {!loading && !soapData && !error && (
          <div className="welcome-message">
            <h2>Welcome!</h2>
            <p>Enter a customer ID (1-100) to see the magic of SOAP-to-REST transformation.</p>
            <div className="features">
              <div className="feature">
                <span className="icon">📡</span>
                <h3>SOAP Service</h3>
                <p>Legacy XML-based API</p>
              </div>
              <div className="feature">
                <span className="icon">🔄</span>
                <h3>REST Gateway</h3>
                <p>Modern JSON transformation</p>
              </div>
              <div className="feature">
                <span className="icon">🔒</span>
                <h3>PII Masking</h3>
                <p>Secure data handling</p>
              </div>
              <div className="feature">
                <span className="icon">🤖</span>
                <h3>AI Insights</h3>
                <p>Claude-powered analysis</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <footer className="App-footer">
        <p>Built with React, Flask, and Claude AI | Portfolio Project 2024</p>
      </footer>
    </div>
  );
}

export default App;
