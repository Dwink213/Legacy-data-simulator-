# AI Architecture Patterns & Best Practices

## SOAP-to-REST Transaction Viewer - AI Integration Guide

This document outlines the AI architecture patterns, cost optimization strategies, and best practices implemented in this portfolio project, specifically tailored for **AI Architect roles**.

---

## Table of Contents

1. [AI Integration Overview](#ai-integration-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Prompt Engineering](#prompt-engineering)
4. [Cost Optimization](#cost-optimization)
5. [Observability & Monitoring](#observability--monitoring)
6. [Security & Compliance](#security--compliance)
7. [Error Handling & Resilience](#error-handling--resilience)
8. [Performance Optimization](#performance-optimization)
9. [Production Considerations](#production-considerations)

---

## AI Integration Overview

### Purpose
The AI layer enhances transaction data with intelligent insights, demonstrating how to integrate large language models (LLMs) into production systems while maintaining cost efficiency, security, and observability.

### Key Capabilities
- **Transaction Analysis**: Spending patterns, category breakdown
- **Anomaly Detection**: Unusual transactions and spending behavior
- **Personalized Recommendations**: Budget suggestions, savings opportunities
- **Natural Language Insights**: Human-readable analysis

### Technology Stack
- **AI Provider**: Anthropic Claude 3.5 Sonnet
- **Infrastructure**: Azure Functions (serverless)
- **Secrets Management**: Azure Key Vault with Managed Identity
- **Observability**: Application Insights + Log Analytics

---

## Architecture Patterns

### Pattern 1: API Gateway + AI Enhancement

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Frontend   │────▶│  REST Gateway   │────▶│ SOAP Service │
│              │◀────│  (Mask PII)     │◀────│              │
└──────────────┘     └─────────────────┘     └──────────────┘
       │                      │
       │                      │
       └──────────────────────┴──────────▶ AI Insights Function
                                           (Secure, Observable)
```

**Why This Pattern?**
- ✅ Separation of concerns (data vs insights)
- ✅ PII masked before AI processing
- ✅ Optional feature (graceful degradation)
- ✅ Independent scaling
- ✅ Cost control through selective calling

### Pattern 2: Managed Identity for Secrets

```
┌────────────────────┐
│  AI Insights Func  │
│  (Managed ID)      │
└─────────┬──────────┘
          │
          │ RBAC: Key Vault Secrets User
          ▼
┌────────────────────┐
│   Azure Key Vault  │
│   - Claude API Key │
│   - Encrypted      │
└────────────────────┘
```

**Benefits:**
- No secrets in code or environment variables
- Automatic rotation support
- Audit logging of secret access
- Enterprise-grade security

### Pattern 3: Structured Logging for AI Operations

```python
logger.info('Claude API call successful', extra={
    'custom_dimensions': {
        'function': 'ai-insights',
        'ai_provider': 'Claude',
        'ai_model': 'claude-3-5-sonnet-20241022',
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': total_tokens,
        'input_cost_usd': round(input_cost, 6),
        'output_cost_usd': round(output_cost, 6),
        'total_cost_usd': round(total_cost, 6),
        'duration_ms': duration,
        'transaction_count': len(transactions),
        'customer_id': customer_id,
        'status': 'success'
    }
})
```

**Why Structured Logging?**
- Query-able metrics in Log Analytics
- Cost tracking per request
- Performance monitoring
- Troubleshooting and debugging
- Compliance and auditing

---

## Prompt Engineering

### Strategy: Concise Context + Clear Instructions

**Bad Prompt (Wasteful):**
```python
# Sends ALL transaction details (high token count)
prompt = f"Here are all transactions: {json.dumps(transactions)}"
```

**Good Prompt (Optimized):**
```python
# Summarized data (low token count)
prompt = f"""Analyze these customer transactions and provide insights:

Transaction Summary:
- Total Transactions: 15
- Total Spent: $1,234.56
- Average Transaction: $82.30

Spending by Category:
- Shopping: $450.00
- Groceries: $320.00
- Restaurants: $280.00

Recent Transactions:
- 2024-01-15: Amazon.com - $89.99 (Shopping)
- 2024-01-14: Whole Foods - $65.43 (Groceries)
- 2024-01-13: Starbucks - $12.50 (Restaurants)

Please provide:
1. Spending pattern analysis
2. Top spending categories
3. Budget recommendations
"""
```

**Token Reduction: ~75%**

### Prompt Template

Location: `azure-functions/ai-insights/__init__.py`

```python
def _create_transaction_summary(self, transactions, summary):
    """
    Create optimized prompt with:
    1. Aggregate statistics (not individual records)
    2. Category groupings (not per-transaction categories)
    3. Top 5 recent (not all 100 transactions)
    4. Clear instructions (specific output format)
    """
```

### Output Parsing

```python
def _parse_insights(self, insights_text, transactions, summary):
    """
    Extract structured data from Claude's text response:
    - Summary metrics
    - Top categories with percentages
    - Largest transactions
    - Actionable recommendations
    """
```

---

## Cost Optimization

### Real-Time Cost Tracking

Every AI request logs:
```python
{
    'input_tokens': 245,
    'output_tokens': 892,
    'total_tokens': 1137,
    'input_cost_usd': 0.000735,   # $3 per million
    'output_cost_usd': 0.013380,  # $15 per million
    'total_cost_usd': 0.014115    # ~$0.014 per request
}
```

### Cost Breakdown (Claude 3.5 Sonnet)

| Component | Tokens | Cost per Million | Cost per Request |
|-----------|--------|------------------|------------------|
| Input     | ~250   | $3.00           | $0.00075        |
| Output    | ~900   | $15.00          | $0.01350        |
| **Total** | ~1,150 | -               | **$0.01425**    |

### Monthly Cost Estimation

**Scenario**: 1,000 users, 10 requests/month each

- **Requests**: 10,000/month
- **Cost**: $142.50/month
- **Per-user**: $0.14/month

### Optimization Strategies

#### 1. **Caching Layer** (Not yet implemented, but recommended)

```python
# Pseudocode
def get_insights(customer_id, transactions_hash):
    cache_key = f"insights:{customer_id}:{transactions_hash}"

    # Check cache (Azure Redis)
    cached = redis.get(cache_key)
    if cached:
        return cached  # $0 cost!

    # Call Claude only if not cached
    insights = claude.analyze(transactions)
    redis.set(cache_key, insights, expire=3600)  # 1 hour TTL
    return insights
```

**Potential Savings**: 70%+ (for repeat queries)

#### 2. **Tiered AI Models**

```python
# Simple queries → Cheaper model
if transaction_count < 5:
    model = "claude-3-haiku-20240307"  # $0.25/$1.25 per M
else:
    model = "claude-3-5-sonnet-20241022"  # $3/$15 per M
```

**Potential Savings**: 50-90% for simple requests

#### 3. **Batch Processing**

```python
# Process multiple customers in one request
prompt = "Analyze these 10 customers:\n\nCustomer 1: ...\nCustomer 2: ..."
```

**Potential Savings**: 30-40% (reduced overhead)

#### 4. **Summary-Only Mode**

```python
# Quick insights without detailed recommendations
max_tokens = 256  # vs 1024 for full analysis
```

**Potential Savings**: 75% on output tokens

---

## Observability & Monitoring

### Key Metrics Tracked

**Performance Metrics:**
- Request duration (p50, p95, p99)
- AI call latency
- Token usage per request
- Throughput (requests/sec)

**Cost Metrics:**
- Cost per request (input + output)
- Daily/monthly AI spend
- Cost per customer
- Token efficiency

**Quality Metrics:**
- Error rate
- Timeout rate
- Retry count
- Customer satisfaction (future)

### Log Analytics Queries

See `monitoring/log-analytics-queries.kql` for:

1. **AI Token Usage & Cost Tracking**
   ```kusto
   traces | where customDimensions.ai_provider == "Claude"
   | summarize total_cost = sum(todouble(customDimensions.total_cost_usd))
   ```

2. **Daily Cost Trends**
   ```kusto
   traces | where customDimensions.ai_provider == "Claude"
   | summarize cost = sum(todouble(customDimensions.total_cost_usd))
     by bin(timestamp, 1d)
   ```

3. **Token Efficiency Analysis**
   ```kusto
   traces | where customDimensions.ai_provider == "Claude"
   | extend tokens_per_txn = total_tokens / transaction_count
   | summarize avg(tokens_per_txn)
   ```

### Application Insights Dashboard

**Recommended Widgets:**
1. AI Request Volume (line chart)
2. Average Cost per Request (metric)
3. Token Usage by Hour (bar chart)
4. Error Rate (%) (metric)
5. P95 Latency (line chart)
6. Monthly Cost Projection (KPI)

---

## Security & Compliance

### PII Handling

**✅ Correct Flow:**
```
Raw Data → Mask PII → Send to AI → Return Insights
```

**❌ Incorrect Flow:**
```
Raw Data → Send to AI → Mask Response  ❌ (PII leaked!)
```

**Implementation:**

1. **Mask Before AI**
   ```python
   masked_data = masker.mask_customer_data(json_data)
   insights = claude.analyze(masked_data)  # AI never sees PII
   ```

2. **What Gets Masked:**
   - Customer names → `J*** S***`
   - Account numbers → `****9012`
   - Email addresses → `j***@email.com`
   - Phone numbers → `***-***-4567`

3. **What AI Sees:**
   ```json
   {
     "customer_name": "J*** S***",
     "transactions": [
       {"merchant": "Amazon.com", "amount": 89.99}
     ]
   }
   ```

### Secret Management

**Azure Key Vault + Managed Identity:**

```bicep
// Bicep template
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  identity: {
    type: 'SystemAssigned'  // Auto-creates managed identity
  }
  properties: {
    siteConfig: {
      appSettings: [
        {
          name: 'CLAUDE_API_KEY'
          value: '@Microsoft.KeyVault(SecretUri=${secret.uri})'
        }
      ]
    }
  }
}
```

**Benefits:**
- ✅ No hardcoded secrets
- ✅ Automatic rotation
- ✅ Audit logs
- ✅ RBAC enforcement

### Compliance Considerations

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| **GDPR** | PII masking before AI | ✅ |
| **Data Residency** | Azure region selection | ✅ |
| **Audit Logging** | Application Insights | ✅ |
| **Encryption at Rest** | Key Vault | ✅ |
| **Encryption in Transit** | HTTPS only | ✅ |

---

## Error Handling & Resilience

### Graceful Degradation

```python
if not self.client:
    return {
        "error": "Claude API not configured",
        "message": "Please set CLAUDE_API_KEY",
        "insights": None  # App still works without AI
    }
```

**Result:** Frontend shows helpful error, not crash

### Retry Logic (Recommended Addition)

```python
from anthropic import APITimeoutError, RateLimitError

@retry(
    retry=retry_if_exception_type((APITimeoutError, RateLimitError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_claude_api(prompt):
    return client.messages.create(...)
```

### Timeout Handling

```python
# Azure Functions timeout: 5 minutes (host.json)
# Set reasonable timeouts for AI calls
message = client.messages.create(
    ...,
    timeout=30.0  # 30 seconds max
)
```

### Circuit Breaker (Future Enhancement)

```python
from pybreaker import CircuitBreaker

claude_breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@claude_breaker
def get_ai_insights(data):
    return claude.analyze(data)
```

---

## Performance Optimization

### Parallel Processing

```javascript
// Frontend makes parallel requests
Promise.all([
  fetch('/api/transactions/42/raw'),
  fetch('/api/transactions/42')
]).then(([raw, masked]) => {
  // Then fetch AI insights with masked data
  return fetch('/api/insights', { body: masked })
})
```

### Response Streaming (Advanced)

```python
# Claude supports streaming responses
stream = client.messages.create(
    ...,
    stream=True
)

for chunk in stream:
    yield chunk  # Send insights as they generate
```

**Benefits:**
- Lower perceived latency
- Better UX (progressive rendering)
- Early error detection

### Token Limits

```python
max_tokens=1024  # Cap output tokens

# Calculate input tokens before calling
estimated_input = len(prompt.split()) * 1.3
if estimated_input > 4000:
    # Truncate or summarize further
    prompt = create_shorter_summary(data)
```

---

## Production Considerations

### Scaling Strategy

| Load Level | Architecture | Cost |
|------------|-------------|------|
| **Dev/Demo** | Single function instance | ~$0/month |
| **Low (< 10K req/month)** | Consumption plan | ~$10-50/month |
| **Medium (10K-100K)** | Premium plan + caching | ~$200-500/month |
| **High (> 100K)** | Dedicated + Redis + CDN | ~$1K-5K/month |

### Rate Limiting

```python
# Azure APIM policy (recommended)
<rate-limit calls="100" renewal-period="60" />

# Or in function code
from ratelimit import limits

@limits(calls=10, period=60)  # 10 calls per minute
def get_insights(customer_id):
    ...
```

### Monitoring Alerts

**Recommended Azure Alerts:**

1. **High AI Cost**
   - Condition: Daily cost > $50
   - Action: Email + Slack notification

2. **High Error Rate**
   - Condition: Error rate > 5%
   - Action: PagerDuty alert

3. **Slow Performance**
   - Condition: P95 latency > 5 seconds
   - Action: Email notification

4. **Token Spike**
   - Condition: Tokens/request > 2000
   - Action: Investigate prompt optimization

### Cost Guardrails

```python
# Environment variable
MAX_DAILY_AI_COST = float(os.getenv('MAX_DAILY_AI_COST', '100.0'))

# Track daily spend in Redis or Application Insights
daily_spend = get_daily_spend()

if daily_spend > MAX_DAILY_AI_COST:
    logger.warning(f"Daily AI cost limit reached: ${daily_spend}")
    return {"error": "AI budget exhausted for today"}
```

---

## AI Architecture Interview Talking Points

### What You Can Say:

> "I integrated Claude API using serverless Azure Functions with comprehensive observability. Every AI call is logged with token usage and cost tracking to Application Insights, allowing real-time monitoring through Log Analytics queries."

> "Security was critical—I implemented PII masking before AI processing and used Azure Managed Identity with Key Vault for secret management, eliminating hardcoded API keys."

> "For cost optimization, I engineered prompts to minimize token usage by sending aggregated summaries instead of raw transaction data, reducing tokens by ~75%. The architecture supports future enhancements like Redis caching for 70% cost savings on repeat queries."

> "The system gracefully degrades if the AI service is unavailable—the app continues to function, just without insights. This demonstrates understanding of resilience patterns for AI-enhanced systems."

> "I structured logs with custom dimensions for cost per request, token usage, and latency percentiles, enabling queries like 'what's our monthly AI spend?' or 'which prompts are most expensive?'"

### Technical Depth:

**Interviewer**: "How would you reduce AI costs in production?"

**You**: "Multiple strategies:
1. **Caching**: Azure Redis with transaction hash keys—70% savings on repeat queries
2. **Model tiering**: Use Claude Haiku for simple queries (90% cheaper)
3. **Prompt optimization**: Already reduced tokens 75% through summarization
4. **Batching**: Process multiple customers per request
5. **Rate limiting**: Prevent abuse and runaway costs
6. **Monitoring**: Daily cost alerts and automatic cutoffs"

**Interviewer**: "How do you handle PII with AI?"

**You**: "Defense in depth:
1. Mask PII *before* sending to AI (never expose raw data)
2. Audit logs track what data was sent (compliance)
3. Customer consent for AI processing (future)
4. Data residency controls via Azure region
5. Encryption in transit (HTTPS) and at rest (Key Vault)"

---

## Future Enhancements

- [ ] **Redis caching layer** for duplicate query detection
- [ ] **Model routing** based on query complexity
- [ ] **Response streaming** for real-time insights
- [ ] **A/B testing** different prompts
- [ ] **Fine-tuning** Claude on domain-specific data
- [ ] **Multi-modal AI** (process receipt images)
- [ ] **Feedback loop** (user ratings improve prompts)
- [ ] **Cost forecasting** with ML predictions

---

## Conclusion

This AI architecture demonstrates:

✅ **Production-ready patterns** (Managed Identity, structured logging)
✅ **Cost awareness** (token tracking, optimization strategies)
✅ **Security best practices** (PII masking, secret management)
✅ **Observability** (comprehensive metrics and queries)
✅ **Resilience** (graceful degradation, error handling)
✅ **Scalability** (serverless, stateless design)

**Perfect for AI Architect interviews!** 🚀
