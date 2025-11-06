# Azure Deployment Guide

## SOAP-to-REST Transaction Viewer - Production Deployment

Complete guide to deploying this AI-powered portfolio project to Azure using Infrastructure as Code.

---

## 📋 Prerequisites

### Required Tools

1. **Azure CLI** (v2.50+)
   ```bash
   # Install
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

   # Verify
   az --version
   ```

2. **Azure Functions Core Tools** (v4.x)
   ```bash
   # Install
   npm install -g azure-functions-core-tools@4 --unsafe-perm true

   # Verify
   func --version
   ```

3. **Azure Account**
   - Free tier available: https://azure.microsoft.com/free/
   - Required permissions: Contributor role on subscription

4. **Claude API Key** (Optional, for AI insights)
   - Get from: https://console.anthropic.com/
   - Free tier available for testing

### Optional Tools

- **Bicep CLI** (usually included with Azure CLI)
- **GitHub Account** (for Static Web App deployment)
- **jq** (for parsing deployment output)

---

## 🚀 Quick Start (5 Minutes)

### Option A: Automated Deployment

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Legacy-data-simulator-

# 2. Login to Azure
az login

# 3. Run deployment script
cd infrastructure
./deploy.sh dev eastus

# 4. Follow prompts to enter Claude API key

# Done! Your app is now live on Azure
```

### Option B: Manual Step-by-Step

See [Detailed Deployment](#detailed-deployment) section below.

---

## 🏗️ Architecture Overview

### Azure Resources Created

| Resource | Purpose | SKU | Cost Estimate |
|----------|---------|-----|---------------|
| **Static Web App** | React frontend hosting | Free | $0/month |
| **Function App** | Serverless API backend | Consumption | $0-5/month |
| **Application Insights** | Monitoring & telemetry | Pay-as-you-go | $0-5/month |
| **Log Analytics** | Log storage & queries | Pay-as-you-go | $0-5/month |
| **Key Vault** | Secret management | Standard | $0-1/month |
| **Storage Account** | Function app storage | Standard LRS | $1-2/month |

**Total Estimated Cost: $1-18/month** (mostly AI usage, infrastructure is ~free)

### Resource Naming Convention

```
Environment: dev
Location: eastus
Unique Suffix: abc123 (auto-generated)

Resources:
- soap-rest-viewer-dev (Static Web App)
- soap-rest-viewer-dev-abc123-func (Function App)
- soap-rest-viewer-dev-abc123-logs (Log Analytics)
- soap-rest-viewer-dev-abc123-insights (App Insights)
- soaprestviewerdevabc123st (Storage Account)
- soap-rest-viewer-dev-abc123-kv (Key Vault)
```

---

## 📦 Detailed Deployment

### Step 1: Prepare Environment

```bash
# Clone repository
git clone <your-repo-url>
cd Legacy-data-simulator-/infrastructure

# Login to Azure
az login

# Set subscription (if you have multiple)
az account list --output table
az account set --subscription "Your Subscription Name"

# Verify you're in the right subscription
az account show
```

### Step 2: Create Resource Group

```bash
# Set variables
ENVIRONMENT="dev"
LOCATION="eastus"
PROJECT_NAME="soap-rest-viewer"
RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-rg"

# Create resource group
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --tags Environment=$ENVIRONMENT Project=$PROJECT_NAME
```

### Step 3: Deploy Infrastructure

```bash
# Deploy using Bicep
az deployment group create \
    --name "soap-rest-$(date +%Y%m%d-%H%M%S)" \
    --resource-group $RESOURCE_GROUP \
    --template-file main.bicep \
    --parameters environment=$ENVIRONMENT \
                 location=$LOCATION \
                 claudeApiKey="your-claude-api-key-here"
```

**⏱️ Deployment time: ~3-5 minutes**

### Step 4: Deploy Function App Code

```bash
# Get Function App name from deployment
FUNCTION_APP_NAME=$(az deployment group show \
    --name <deployment-name> \
    --resource-group $RESOURCE_GROUP \
    --query 'properties.outputs.deploymentSummary.value.functionApp.name' \
    --output tsv)

# Deploy functions
cd ../azure-functions
func azure functionapp publish $FUNCTION_APP_NAME --python

# Verify deployment
curl https://${FUNCTION_APP_NAME}.azurewebsites.net/api/soap
```

### Step 5: Deploy Static Web App

#### Option A: GitHub Actions (Recommended)

```bash
# 1. Get Static Web App deployment token
STATIC_APP_TOKEN=$(az staticwebapp secrets list \
    --name soap-rest-viewer-$ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --query 'properties.apiKey' \
    --output tsv)

# 2. Add as GitHub secret
# Go to: GitHub repo → Settings → Secrets → Actions
# Create secret: AZURE_STATIC_WEB_APPS_API_TOKEN = $STATIC_APP_TOKEN

# 3. Create GitHub workflow file
# (See .github/workflows/azure-static-web-apps.yml)

# 4. Push to trigger deployment
git add .
git commit -m "Deploy to Azure"
git push
```

#### Option B: Manual Build & Deploy

```bash
# Build React app
cd frontend
npm install
npm run build

# Deploy to Static Web App
az staticwebapp upload \
    --name soap-rest-viewer-$ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --source ./build
```

### Step 6: Verify Deployment

```bash
# Get URLs
STATIC_URL=$(az staticwebapp show \
    --name soap-rest-viewer-$ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --query 'defaultHostname' \
    --output tsv)

FUNCTION_URL=$(az functionapp show \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query 'defaultHostName' \
    --output tsv)

# Test endpoints
echo "Frontend: https://$STATIC_URL"
echo "API: https://$FUNCTION_URL/api"

# Test SOAP endpoint
curl -X POST https://$FUNCTION_URL/api/soap \
  -H "Content-Type: text/xml" \
  -d '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bank="http://legacy-banking.example.com/transactions"><soap:Body><bank:GetCustomerTransactionsRequest><bank:CustomerID>42</bank:CustomerID></bank:GetCustomerTransactionsRequest></soap:Body></soap:Envelope>'

# Test REST endpoint
curl https://$FUNCTION_URL/api/transactions/42

# Test AI insights
curl -X POST https://$FUNCTION_URL/api/insights \
  -H "Content-Type: application/json" \
  -d '{"customer_data": {...}}'
```

---

## 🔐 Security Configuration

### Step 1: Configure Key Vault Access

```bash
# Get Function App managed identity
IDENTITY_ID=$(az functionapp identity show \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query 'principalId' \
    --output tsv)

# Verify Key Vault access
az keyvault secret show \
    --name claude-api-key \
    --vault-name soap-rest-viewer-$ENVIRONMENT-<suffix>-kv
```

### Step 2: Update CORS Settings

```bash
# Add your domains to CORS
az functionapp cors add \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --allowed-origins "https://your-domain.com"
```

### Step 3: Enable HTTPS Only

```bash
# Enforce HTTPS
az functionapp update \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set httpsOnly=true
```

---

## 📊 Monitoring & Observability

### Access Application Insights

```bash
# Get Application Insights URL
APP_INSIGHTS_URL="https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/*"

echo "Open: $APP_INSIGHTS_URL"
```

### Run Log Analytics Queries

```bash
# Get Log Analytics workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --resource-group $RESOURCE_GROUP \
    --workspace-name soap-rest-viewer-$ENVIRONMENT-<suffix>-logs \
    --query 'customerId' \
    --output tsv)

# Run query via CLI
az monitor log-analytics query \
    --workspace $WORKSPACE_ID \
    --analytics-query "traces | where customDimensions.function == 'ai-insights' | take 10"
```

### View AI Cost Tracking

```bash
# Query AI costs
az monitor log-analytics query \
    --workspace $WORKSPACE_ID \
    --analytics-query "traces | where customDimensions.ai_provider == 'Claude' | summarize total_cost = sum(todouble(customDimensions.total_cost_usd)) by bin(timestamp, 1d)"
```

### Set Up Alerts

```bash
# Create alert for high AI costs
az monitor metrics alert create \
    --name high-ai-cost-alert \
    --resource-group $RESOURCE_GROUP \
    --scopes /subscriptions/<subscription-id>/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/<app-insights-name> \
    --condition "total customDimensions.total_cost_usd > 50" \
    --description "Alert when daily AI cost exceeds $50" \
    --evaluation-frequency 5m \
    --window-size 1h \
    --action <action-group-id>
```

---

## 🔄 Continuous Deployment

### GitHub Actions Workflow

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Azure Deployment

on:
  push:
    branches: [main]

jobs:
  deploy-functions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd azure-functions
          pip install -r requirements.txt

      - name: Deploy to Azure Functions
        uses: Azure/functions-action@v1
        with:
          app-name: ${{ secrets.AZURE_FUNCTION_APP_NAME }}
          package: './azure-functions'
          publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}

  deploy-static-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build React App
        run: |
          cd frontend
          npm install
          npm run build

      - name: Deploy to Static Web App
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/frontend"
          output_location: "build"
```

### Required GitHub Secrets

```bash
# Get function app publish profile
az functionapp deployment list-publishing-profiles \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --xml

# Get Static Web App token
az staticwebapp secrets list \
    --name soap-rest-viewer-$ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --query 'properties.apiKey' \
    --output tsv
```

Add these as GitHub secrets:
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
- `AZURE_STATIC_WEB_APPS_API_TOKEN`
- `AZURE_FUNCTION_APP_NAME`

---

## 🧹 Cleanup & Teardown

### Delete All Resources

```bash
# Delete entire resource group (removes all resources)
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Verify deletion
az group exists --name $RESOURCE_GROUP
```

### Partial Cleanup (Keep infra, remove data)

```bash
# Delete specific resources
az functionapp delete --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP
az staticwebapp delete --name soap-rest-viewer-$ENVIRONMENT --resource-group $RESOURCE_GROUP
```

---

## 💰 Cost Management

### View Current Costs

```bash
# Get cost for resource group (last 30 days)
az consumption usage list \
    --start-date $(date -d '30 days ago' +%Y-%m-%d) \
    --end-date $(date +%Y-%m-%d) \
    | jq '[.[] | select(.instanceName | contains("soap-rest-viewer"))] | .[].pretaxCost' | jq -s 'add'
```

### Set Budget Alerts

```bash
# Create budget (requires Billing Reader role)
az consumption budget create \
    --budget-name soap-rest-viewer-monthly-budget \
    --amount 50 \
    --category Cost \
    --time-grain Monthly \
    --start-date $(date +%Y-%m-01) \
    --resource-group $RESOURCE_GROUP
```

### Cost Optimization Tips

1. **Use Free Tiers**
   - Static Web App: Free tier (100GB bandwidth)
   - Functions: First 1M executions free
   - Application Insights: First 5GB free

2. **Scale Down Non-Prod**
   ```bash
   # Stop Function App when not in use
   az functionapp stop --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

   # Start when needed
   az functionapp start --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP
   ```

3. **Monitor AI Costs**
   - See Log Analytics queries in `monitoring/log-analytics-queries.kql`
   - Set daily cost limits in Function App config

---

## 🐛 Troubleshooting

### Function App Not Starting

```bash
# Check logs
az functionapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Check app settings
az functionapp config appsettings list \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP
```

### Key Vault Access Denied

```bash
# Verify managed identity has access
az keyvault set-policy \
    --name <key-vault-name> \
    --object-id $IDENTITY_ID \
    --secret-permissions get list
```

### CORS Issues

```bash
# Add localhost for testing
az functionapp cors add \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --allowed-origins "http://localhost:3000"
```

### Static Web App 404 Errors

```bash
# Check deployment status
az staticwebapp show \
    --name soap-rest-viewer-$ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --query 'repositoryUrl,branch'
```

---

## 📚 Additional Resources

- **Azure CLI Reference**: https://docs.microsoft.com/cli/azure/
- **Bicep Documentation**: https://docs.microsoft.com/azure/azure-resource-manager/bicep/
- **Azure Functions Python**: https://docs.microsoft.com/azure/azure-functions/functions-reference-python
- **Static Web Apps**: https://docs.microsoft.com/azure/static-web-apps/
- **Application Insights**: https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview

---

## ✅ Post-Deployment Checklist

- [ ] Verify all endpoints are responding
- [ ] Test SOAP → REST transformation
- [ ] Confirm PII masking is working
- [ ] Test AI insights (if Claude API key configured)
- [ ] Review Application Insights data
- [ ] Run sample Log Analytics queries
- [ ] Set up cost alerts
- [ ] Configure GitHub Actions
- [ ] Update README with live URLs
- [ ] Share portfolio link!

---

**Your AI architecture portfolio project is now production-ready on Azure!** 🚀

For questions or issues, refer to:
- `AI_ARCHITECTURE.md` - AI patterns and best practices
- `monitoring/log-analytics-queries.kql` - Monitoring queries
- `ARCHITECTURE_DECISIONS.md` - Technology choices
