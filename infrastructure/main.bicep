// Main Bicep template for SOAP-to-REST Transaction Viewer
// AI Architect Portfolio Project - Azure Infrastructure

@description('The name of the environment. This will be used to generate resource names.')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string = 'dev'

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Claude API Key for AI insights (stored in Key Vault)')
@secure()
param claudeApiKey string

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

// Variables
var projectName = 'soap-rest-viewer'
var resourcePrefix = '${projectName}-${environment}-${uniqueSuffix}'

// Resource names
var staticWebAppName = '${projectName}-${environment}'
var functionAppName = '${resourcePrefix}-func'
var appServicePlanName = '${resourcePrefix}-plan'
var storageAccountName = toLower(replace('${resourcePrefix}st', '-', ''))
var logAnalyticsName = '${resourcePrefix}-logs'
var appInsightsName = '${resourcePrefix}-insights'
var keyVaultName = toLower(take('${resourcePrefix}-kv', 24))

// Tags for all resources
var commonTags = {
  Environment: environment
  Project: 'SOAP-to-REST-Viewer'
  ManagedBy: 'Bicep'
  CostCenter: 'AI-Architecture-Portfolio'
}

// ============================================================================
// Log Analytics Workspace
// ============================================================================

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: commonTags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// ============================================================================
// Application Insights
// ============================================================================

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: commonTags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Storage Account for Azure Functions
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  tags: commonTags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// ============================================================================
// Key Vault for Secrets
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: keyVaultName
  location: location
  tags: commonTags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    publicNetworkAccess: 'Enabled'
  }
}

// Store Claude API Key in Key Vault
resource claudeApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: keyVault
  name: 'claude-api-key'
  properties: {
    value: claudeApiKey
    contentType: 'API Key'
  }
}

// ============================================================================
// App Service Plan for Azure Functions
// ============================================================================

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  tags: commonTags
  sku: {
    name: 'Y1'  // Consumption plan
    tier: 'Dynamic'
  }
  properties: {
    reserved: true  // Required for Linux
  }
}

// ============================================================================
// Azure Function App
// ============================================================================

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  tags: commonTags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'CLAUDE_API_KEY'
          value: '@Microsoft.KeyVault(SecretUri=${claudeApiKeySecret.properties.secretUri})'
        }
        {
          name: 'SOAP_SERVICE_URL'
          value: 'https://${functionAppName}.azurewebsites.net/api/soap'
        }
      ]
      cors: {
        allowedOrigins: [
          'https://${staticWebAppName}.azurestaticapps.net'
          'http://localhost:3000'
        ]
        supportCredentials: false
      }
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
}

// Grant Function App access to Key Vault
resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Static Web App
// ============================================================================

resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: location
  tags: commonTags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: '' // Set this to your GitHub repo URL
    branch: '' // Set this to your branch name
    buildProperties: {
      appLocation: '/frontend'
      apiLocation: ''
      outputLocation: 'build'
    }
  }
}

// Link Static Web App to Function App API
resource staticWebAppSettings 'Microsoft.Web/staticSites/config@2022-09-01' = {
  parent: staticWebApp
  name: 'appsettings'
  properties: {
    REACT_APP_API_URL: 'https://${functionAppName}.azurewebsites.net/api'
  }
}

// ============================================================================
// Outputs
// ============================================================================

output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
output keyVaultName string = keyVault.name
output resourceGroupName string = resourceGroup().name

output deploymentSummary object = {
  environment: environment
  location: location
  staticWebApp: {
    name: staticWebApp.name
    url: 'https://${staticWebApp.properties.defaultHostname}'
  }
  functionApp: {
    name: functionApp.name
    url: 'https://${functionApp.properties.defaultHostName}'
  }
  monitoring: {
    logAnalytics: logAnalyticsWorkspace.name
    appInsights: appInsights.name
  }
  security: {
    keyVault: keyVault.name
    managedIdentity: functionApp.identity.principalId
  }
}
