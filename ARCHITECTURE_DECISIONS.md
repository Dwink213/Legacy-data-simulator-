# Architectural Decision Record (ADR)

## SOAP-to-REST Transaction Viewer - Technology Decisions

**Date:** 2024
**Status:** Implemented
**Context:** Portfolio project demonstrating API transformation, security practices, and AI integration

---

## Table of Contents
1. [Backend Framework](#1-backend-framework)
2. [Frontend Framework](#2-frontend-framework)
3. [SOAP Implementation](#3-soap-implementation)
4. [Data Generation Strategy](#4-data-generation-strategy)
5. [PII Masking Approach](#5-pii-masking-approach)
6. [AI Platform Choice](#6-ai-platform-choice)
7. [Architecture Pattern](#7-architecture-pattern)
8. [Development Simplifications](#8-development-simplifications)

---

## 1. Backend Framework

### Decision: **Python Flask**

### Alternatives Considered
- **Node.js + Express**: JavaScript ecosystem consistency
- **Django**: Full-featured Python framework
- **FastAPI**: Modern async Python framework

### Why Flask?

✅ **Simplicity and Speed**
- Minimal boilerplate for REST APIs
- Quick prototype-to-production path
- Perfect for microservices architecture

✅ **SOAP Support**
- Excellent `zeep` library for SOAP client/server
- Easy XML manipulation with `lxml`
- Python's strong XML ecosystem

✅ **Portfolio Clarity**
- Code is readable and self-documenting
- Easy for interviewers to understand
- Demonstrates focused skillset

❌ **Why Not Alternatives?**
- **Django**: Too heavyweight for this use case, includes ORM/admin we don't need
- **FastAPI**: Async complexity not needed for this demo
- **Node.js**: SOAP libraries less mature than Python's zeep

---

## 2. Frontend Framework

### Decision: **React 18**

### Alternatives Considered
- **Vue.js**: Progressive framework
- **Angular**: Full-featured framework
- **Vanilla JavaScript**: No framework

### Why React?

✅ **Industry Standard**
- Most popular frontend framework (2024)
- Highest demand in job market
- Demonstrates modern skillset

✅ **Component Architecture**
- Perfect for our four-panel layout
- Reusable components (SoapPanel, JsonPanel, etc.)
- Clean separation of concerns

✅ **State Management**
- Simple useState hooks for this scale
- No need for Redux/complex state libraries
- Shows understanding of React fundamentals

✅ **Development Experience**
- Create React App for quick setup
- Hot reload for rapid development
- Large ecosystem and community

❌ **Why Not Alternatives?**
- **Vue**: Less industry adoption than React
- **Angular**: Steeper learning curve, verbose for this use case
- **Vanilla JS**: Would require custom state management, less impressive

---

## 3. SOAP Implementation

### Decision: **Mock SOAP Service (Flask + lxml)**

### Alternatives Considered
- **Real legacy integration**: Connect to actual SOAP service
- **SOAP framework**: Use Spyne or pysimplesoap
- **WSDL generation**: Full SOAP specification

### Why Mock SOAP?

✅ **Portfolio Focus**
- Demonstrates understanding without external dependencies
- Runs anywhere without credentials
- Shows transformation logic clearly

✅ **Realistic Enough**
- Proper SOAP envelope structure
- Namespace-aware XML
- Simulates legacy banking system

✅ **Simplicity**
- No WSDL complexity
- Direct XML generation
- Easy to understand and modify

❌ **Why Not Alternatives?**
- **Real integration**: Requires credentials, brittle for demos
- **Full SOAP framework**: Overkill for demo purposes
- **WSDL**: Adds complexity without portfolio value

---

## 4. Data Generation Strategy

### Decision: **In-Memory Faker with Seeded Randomness**

### Alternatives Considered
- **Database**: PostgreSQL/MongoDB with seed data
- **External API**: Use mock data services
- **JSON files**: Static transaction data

### Why In-Memory Generation?

✅ **Zero Setup**
- No database installation required
- Works immediately after `pip install`
- Runs on any machine

✅ **Consistent Demo**
- Seeded random ensures same customer = same data
- Predictable for presentations
- But appears realistic to viewers

✅ **Variety**
- Can generate 100+ unique customers
- Realistic merchant names and categories
- Varied transaction amounts and dates

✅ **Performance**
- Instant generation (no DB queries)
- No latency concerns
- Scales easily

❌ **Why Not Alternatives?**
- **Database**: Setup friction, not needed for demo
- **External API**: Network dependency, rate limits
- **Static JSON**: Less impressive, no variety

### Implementation Details

```python
# Seeded for consistency
random.seed(customer_id)

# Realistic categories and merchants
MERCHANTS = ["Amazon.com", "Starbucks", "Shell Gas", ...]
CATEGORIES = ["Shopping", "Groceries", "Restaurants", ...]

# Summary statistics calculated
total_spent = sum(t["amount"] for t in transactions)
```

---

## 5. PII Masking Approach

### Decision: **Custom Regex-Based Masking Library**

### Alternatives Considered
- **Microsoft Presidio**: Enterprise PII detection
- **AWS Comprehend**: Cloud-based PII service
- **Scrubadub**: Python PII scrubbing library

### Why Custom Masking?

✅ **Portfolio Demonstration**
- Shows security awareness
- Demonstrates regex skills
- Easy to explain in interviews

✅ **Deterministic Rules**
- Names: First letter + `***`
- Accounts: Last 4 digits only
- Emails: First letter + `***@domain`
- Phones: Last 4 digits

✅ **Visual Impact**
- Clear highlighting in UI
- Before/after comparison
- Demonstrates practical security

✅ **No Dependencies**
- Pure Python implementation
- No API calls or credits needed
- Fast and reliable

❌ **Why Not Alternatives?**
- **Presidio**: Heavy dependency, overkill for demo
- **AWS Comprehend**: Requires AWS account, costs money
- **Scrubadub**: Less control over masking format

### Security Note

This is **demonstration-grade** masking, not production security. Real applications should use:
- Tokenization services
- Encryption at rest
- Role-based access control
- Audit logging

---

## 6. AI Platform Choice

### Decision: **Anthropic Claude API**

### Alternatives Considered
- **OpenAI GPT-4**: Most popular LLM
- **Google Gemini**: Multimodal capabilities
- **Open-source LLM**: Llama, Mistral

### Why Claude?

✅ **Technical Excellence**
- Superior reasoning for financial analysis
- Strong at structured output
- Excellent instruction following

✅ **Portfolio Alignment**
- Shows awareness of Claude Code environment
- Demonstrates API integration skills
- Modern AI integration example

✅ **API Quality**
- Clean Python SDK
- Good error handling
- Reasonable pricing for demos

✅ **Graceful Degradation**
- Works without API key (shows error handling)
- Optional feature, doesn't break app
- Clear setup instructions

❌ **Why Not Alternatives?**
- **OpenAI**: More expensive, similar capabilities
- **Gemini**: Less mature Python SDK
- **Open-source**: Requires local hosting, complex setup

### Integration Pattern

```python
# Optional with clear error handling
if not api_key:
    return {"error": "API key not configured"}

# Structured insights
insights = {
    "summary": {...},
    "top_categories": [...],
    "recommendations": [...]
}
```

---

## 7. Architecture Pattern

### Decision: **API Gateway Pattern (Simulated APIM)**

### Alternatives Considered
- **Direct frontend-to-SOAP**: No gateway layer
- **GraphQL**: Modern query language
- **Event-driven**: Message queue architecture

### Why API Gateway?

✅ **Real-World Pattern**
- Mimics Azure APIM functionality
- Industry-standard architecture
- Shows enterprise awareness

✅ **Separation of Concerns**
- SOAP service: Legacy system simulation
- Gateway: Transformation + security
- Frontend: Pure presentation

✅ **Portfolio Value**
- Demonstrates layered architecture
- Shows transformation logic
- Clear responsibility boundaries

✅ **Features Simulated**
- Request/response logging
- Protocol transformation
- Security layer (PII masking)
- Multi-backend aggregation

❌ **Why Not Alternatives?**
- **Direct connection**: No transformation layer to demo
- **GraphQL**: Adds complexity, not industry standard for SOAP
- **Event-driven**: Overkill for synchronous demo

### Gateway Responsibilities

```python
def get_transactions(customer_id):
    # 1. Log request (APIM logging)
    log_request(customer_id, endpoint)

    # 2. Call backend (proxy)
    soap_response = call_soap_service(customer_id)

    # 3. Transform (APIM policy)
    json_data = parse_soap_response(soap_response)

    # 4. Mask PII (security policy)
    masked_data = masker.mask_customer_data(json_data)

    # 5. Return
    return jsonify(masked_data)
```

---

## 8. Development Simplifications

### Decision: **Local-First, Cloud-Optional Architecture**

### Why Local-First?

✅ **Zero Friction**
- Runs on any machine
- No cloud account needed
- No credit card required

✅ **Interviewer Friendly**
- Can demo offline
- Quick setup (<5 minutes)
- No deployment debugging

✅ **Learning Focus**
- Showcases code, not DevOps
- Architecture over infrastructure
- Core concepts over cloud config

### Deliberate Simplifications

| Aspect | Production | Demo | Rationale |
|--------|-----------|------|-----------|
| **Database** | PostgreSQL | In-memory | Setup friction vs portfolio value |
| **Authentication** | OAuth/JWT | None | Focus on transformation, not auth |
| **HTTPS** | Required | HTTP | Local development, certs not needed |
| **Caching** | Redis | None | Adds complexity, not core demo |
| **Rate Limiting** | Implemented | None | Not needed for single-user demo |
| **Monitoring** | Datadog/New Relic | Console logs | File logging sufficient |
| **Deployment** | Docker/K8s | Local | Easy to add later if needed |

### What Could Be Added?

Future enhancements (mentioned in README):
- [ ] Docker containerization
- [ ] Database persistence (PostgreSQL)
- [ ] Authentication/authorization
- [ ] Redis caching layer
- [ ] Unit and integration tests
- [ ] CI/CD pipeline
- [ ] Cloud deployment (Heroku/Railway)

---

## 9. File Structure Decisions

### Decision: **Flat Backend, Component-Based Frontend**

### Backend Structure
```
backend/
├── soap_service.py      # Standalone SOAP server
├── rest_gateway.py      # Standalone REST server
├── data_generator.py    # Pure utility
├── pii_masker.py        # Pure utility
└── claude_client.py     # Pure utility
```

✅ **Why Flat?**
- Each service is independent
- Can run separately for testing
- Clear entry points
- Portfolio clarity

❌ **Not MVC/Layered**
- Would add structure but reduce clarity
- Overkill for 5 files
- Harder to understand at a glance

### Frontend Structure
```
frontend/src/
├── App.js
├── index.js
└── components/
    ├── SoapPanel.jsx
    ├── JsonPanel.jsx
    ├── MaskedPanel.jsx
    └── InsightsPanel.jsx
```

✅ **Why Component-Based?**
- React best practice
- Each panel is independent
- Reusable if needed
- Clear responsibility

---

## 10. Startup Script Strategy

### Decision: **Shell Scripts Over Docker/Docker-Compose**

### Why Shell Scripts?

✅ **Simplicity**
- One command: `./start.sh`
- No Docker knowledge required
- Works on all platforms (start.bat for Windows)

✅ **Transparency**
- Easy to see what's running
- Can modify ports/config easily
- Educational for learners

✅ **Portfolio Context**
- Shows automation skills
- Cross-platform thinking (sh + bat)
- Good documentation

❌ **Why Not Docker?**
- Adds setup barrier
- Not all interviewers have Docker
- Can be added later if needed

### Script Features
- ✅ Dependency checking
- ✅ Parallel service startup
- ✅ PID tracking for shutdown
- ✅ Log file creation
- ✅ Browser auto-open

---

## Summary: Key Decision Themes

### 1. **Portfolio Over Production**
Every decision optimized for:
- Easy to understand
- Quick to demo
- Impressive but not overwhelming

### 2. **Local-First**
Runs anywhere, no credentials, no cloud dependency

### 3. **Modern Stack**
Current industry standards (React, Flask, Claude)

### 4. **Clear Architecture**
Gateway pattern, separation of concerns, layered design

### 5. **Practical Security**
Demonstrates awareness without overengineering

### 6. **AI Enhancement**
Shows modern skills, optional feature, graceful degradation

---

## Trade-Offs We Made

| Decision | Pro | Con | Worth It? |
|----------|-----|-----|-----------|
| No Database | Zero setup | Not "real" persistence | ✅ Yes - Demo focused |
| Mock SOAP | Self-contained | Not truly legacy | ✅ Yes - Shows concept |
| Custom Masking | Easy to explain | Not enterprise-grade | ✅ Yes - Educational |
| Local-only | Works anywhere | No live URL | ✅ Yes - Can deploy later |
| No Tests | Faster development | Less professional | ⚠️ Could add later |

---

## Conclusion

This architecture prioritizes:
1. **Portfolio impact** over production readiness
2. **Clarity** over completeness
3. **Modern tech** over bleeding edge
4. **Independence** over cloud services
5. **Demonstration** over deployment

Every technology choice serves the goal: **impress in interviews while being easy to explain and demo**.

The result is a project that:
- ✅ Runs in under 5 minutes
- ✅ Works on any laptop
- ✅ Demonstrates 5+ key skills
- ✅ Is interview-ready
- ✅ Can be extended to production

---

**Next Review Date:** When adding production features (auth, DB, Docker)
**Decision Authority:** Portfolio owner
**Stakeholders:** Future employers, technical interviewers, portfolio viewers
