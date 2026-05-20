// modules/foundry.bicep
// Provisiona um recurso Azure AI Foundry (Microsoft.CognitiveServices/accounts
// kind=AIServices), um project filho e um deployment de modelo.

param location string
param tags object = {}
param foundryAccountName string
param foundryProjectName string

@description('Nome do modelo a ser deployado (ex.: gpt-5.4).')
param modelName string

@description('Versão do modelo (consulte o catálogo do Foundry).')
param modelVersion string

@description('Nome do deployment (env AZURE_AI_MODEL_DEPLOYMENT_NAME).')
param modelDeploymentName string = modelName

@description('SKU do deployment (ex.: GlobalStandard, Standard).')
param modelSkuName string = 'GlobalStandard'

@description('Capacity (kTPM) do deployment.')
param modelCapacity int = 10

@description('Resource ID do Application Insights a conectar ao project (vazio = não cria connection).')
param appInsightsId string = ''

@description('Connection string do Application Insights (vazio = não cria connection).')
param appInsightsConnectionString string = ''

resource foundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: foundryAccountName
  location: location
  tags: tags
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: foundryAccountName
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  parent: foundry
  name: foundryProjectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: foundry
  name: modelDeploymentName
  sku: {
    name: modelSkuName
    capacity: modelCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

// ===== Application Insights connection =====
// Vincula o App Insights ao Foundry project para que as abas "Tracing" e
// "Monitoring" do portal ai.azure.com fiquem populadas.
resource appInsightsConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = if (!empty(appInsightsId) && !empty(appInsightsConnectionString)) {
  parent: project
  name: 'appinsights'
  properties: {
    category: 'AppInsights'
    target: appInsightsId
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: appInsightsConnectionString
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: appInsightsId
    }
  }
}

output accountName string = foundry.name
output projectName string = project.name
output projectEndpoint string = 'https://${foundry.name}.services.ai.azure.com/api/projects/${project.name}'
output deploymentName string = modelDeployment.name
