#!/bin/bash

#############################################################################
# Azure Deployment Script for SOAP-to-REST Transaction Viewer
# AI Architect Portfolio Project
#############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SOAP-to-REST Azure Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
ENVIRONMENT="${1:-dev}"
LOCATION="${2:-eastus}"
PROJECT_NAME="soap-rest-viewer"
RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-rg"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Environment: $ENVIRONMENT"
echo "  Location: $LOCATION"
echo "  Resource Group: $RESOURCE_GROUP"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
echo -e "${YELLOW}Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}Not logged in to Azure. Please log in:${NC}"
    az login
fi

SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo -e "${GREEN}✓ Logged in to Azure${NC}"
echo "  Subscription: $SUBSCRIPTION_NAME"
echo ""

# Prompt for Claude API Key
echo -e "${YELLOW}Claude API Key Configuration:${NC}"
read -sp "Enter your Claude API Key (or press Enter to skip AI insights): " CLAUDE_API_KEY
echo ""

if [ -z "$CLAUDE_API_KEY" ]; then
    CLAUDE_API_KEY="not-configured"
    echo -e "${YELLOW}⚠ AI insights will not be available without Claude API key${NC}"
else
    echo -e "${GREEN}✓ Claude API key will be securely stored in Key Vault${NC}"
fi
echo ""

# Create Resource Group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --tags "Environment=$ENVIRONMENT" "Project=$PROJECT_NAME" "ManagedBy=Bicep" \
    --output none

echo -e "${GREEN}✓ Resource group created: $RESOURCE_GROUP${NC}"
echo ""

# Deploy infrastructure
echo -e "${YELLOW}Deploying Azure infrastructure...${NC}"
echo "  This will create:"
echo "    • Azure Static Web App (Frontend)"
echo "    • Azure Functions (Backend API)"
echo "    • Application Insights (Monitoring)"
echo "    • Log Analytics Workspace (Logs)"
echo "    • Key Vault (Secrets)"
echo "    • Storage Account (Functions storage)"
echo ""

DEPLOYMENT_NAME="${PROJECT_NAME}-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "main.bicep" \
    --parameters environment="$ENVIRONMENT" \
                 location="$LOCATION" \
                 claudeApiKey="$CLAUDE_API_KEY" \
    --output json > deployment-output.json

echo -e "${GREEN}✓ Infrastructure deployed successfully${NC}"
echo ""

# Extract outputs
echo -e "${YELLOW}Deployment Summary:${NC}"
echo ""

STATIC_WEB_APP_URL=$(jq -r '.properties.outputs.staticWebAppUrl.value' deployment-output.json)
FUNCTION_APP_URL=$(jq -r '.properties.outputs.functionAppUrl.value' deployment-output.json)
APP_INSIGHTS_KEY=$(jq -r '.properties.outputs.appInsightsInstrumentationKey.value' deployment-output.json)
KEY_VAULT_NAME=$(jq -r '.properties.outputs.keyVaultName.value' deployment-output.json)

echo -e "${GREEN}Frontend (Static Web App):${NC}"
echo "  URL: $STATIC_WEB_APP_URL"
echo ""

echo -e "${GREEN}Backend (Azure Functions):${NC}"
echo "  URL: $FUNCTION_APP_URL"
echo "  Endpoints:"
echo "    • POST $FUNCTION_APP_URL/api/soap"
echo "    • GET  $FUNCTION_APP_URL/api/transactions/{id}"
echo "    • POST $FUNCTION_APP_URL/api/insights"
echo ""

echo -e "${GREEN}Monitoring:${NC}"
echo "  Application Insights: $APP_INSIGHTS_KEY"
echo "  View in portal: https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/*"
echo ""

echo -e "${GREEN}Security:${NC}"
echo "  Key Vault: $KEY_VAULT_NAME"
echo "  Managed Identity: Enabled"
echo ""

# Deploy Function App code
echo -e "${YELLOW}Deploying Function App code...${NC}"
FUNCTION_APP_NAME=$(jq -r '.properties.outputs.deploymentSummary.value.functionApp.name' deployment-output.json)

cd ../azure-functions
func azure functionapp publish "$FUNCTION_APP_NAME" --python
cd ../infrastructure

echo -e "${GREEN}✓ Function App code deployed${NC}"
echo ""

# Deploy Static Web App
echo -e "${YELLOW}Static Web App deployment:${NC}"
echo "  Configure GitHub Actions for automatic deployment:"
echo "  1. Get deployment token:"
echo "     az staticwebapp secrets list --name $(jq -r '.properties.outputs.deploymentSummary.value.staticWebApp.name' deployment-output.json) -g $RESOURCE_GROUP --query 'properties.apiKey' -o tsv"
echo "  2. Add as GitHub secret: AZURE_STATIC_WEB_APPS_API_TOKEN"
echo "  3. Push to your repository to trigger build"
echo ""

# Save deployment info
cat > deployment-info.txt <<EOF
SOAP-to-REST Transaction Viewer - Azure Deployment
===================================================

Environment: $ENVIRONMENT
Deployed: $(date)

URLs:
  Frontend:  $STATIC_WEB_APP_URL
  Backend:   $FUNCTION_APP_URL

Resources:
  Resource Group: $RESOURCE_GROUP
  Function App:   $FUNCTION_APP_NAME
  Key Vault:      $KEY_VAULT_NAME

Next Steps:
  1. Configure GitHub Actions for Static Web App deployment
  2. View Application Insights: https://portal.azure.com
  3. Query logs in Log Analytics workspace
  4. Monitor AI costs and token usage

Estimated Monthly Cost: ~\$0-10 (Free tiers + AI usage)
EOF

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Deployment details saved to: ${YELLOW}deployment-info.txt${NC}"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  • Update frontend/.env with: REACT_APP_API_URL=$FUNCTION_APP_URL/api"
echo "  • Configure GitHub Actions for continuous deployment"
echo "  • Review costs in Azure Cost Management"
echo ""
echo -e "${GREEN}Your AI architecture portfolio project is now live on Azure! 🚀${NC}"
