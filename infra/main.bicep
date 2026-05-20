// main.bicep
// Infraestrutura para SAP Ariba MCP & Agent
// Deploy: Container Apps (ariba-mcp + ariba-agent) + Container Registry + Log Analytics
//
// O Resource Group de destino é fornecido pelo usuário (via `azd env set AZURE_RESOURCE_GROUP <nome>`
// ou via prompt do `azd up`). Este template NÃO cria o resource group.

targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Nome do ambiente - usado para gerar um hash único em todos os recursos.')
param environmentName string

@minLength(1)
@description('Localização principal para todos os recursos.')
@allowed([
  'eastus'
  'eastus2'
  'brazilsouth'
  'swedencentral'
  'westeurope'
])
param location string

@description('Endpoint do projeto Azure AI Foundry usado pelo agente. Vazio = usa o endpoint do Foundry provisionado por este template.')
param aiProjectEndpoint string = ''

@description('Nome do deployment do modelo no Foundry. Vazio = usa o deployment criado por este template.')
param aiModelDeploymentName string = ''

@description('Nome do modelo a ser deployado no Foundry provisionado.')
param foundryModelName string = 'gpt-5.4'

@description('Versão do modelo a ser deployado no Foundry provisionado.')
param foundryModelVersion string = '2026-03-05'

@description('SKU do deployment do modelo no Foundry (ex.: GlobalStandard, Standard).')
param foundryModelSkuName string = 'GlobalStandard'

@description('Capacity (kTPM) do deployment do modelo.')
param foundryModelCapacity int = 10

@description('Nome do recurso Azure AI Foundry externo (Microsoft.CognitiveServices/accounts). Vazio = usa o Foundry provisionado por este template.')
param aiFoundryAccountName string = ''

@description('Resource group do recurso Azure AI Foundry externo. Vazio = usa o Foundry provisionado por este template.')
param aiFoundryResourceGroup string = ''

@description('Se true, o Ariba-MCP usa dados mock e ignora credenciais SAP.')
param aribaUseMock string = 'true'

@description('SAP Ariba App ID (opcional, ignorado em modo mock).')
param aribaAppId string = ''

@description('SAP Ariba Client ID (opcional, ignorado em modo mock).')
param aribaClientId string = ''

@secure()
@description('SAP Ariba Client Secret (opcional, ignorado em modo mock).')
param aribaClientSecret string = ''

@description('SAP Ariba Realm (opcional, ignorado em modo mock).')
param aribaRealm string = ''

// Token determinístico padrão azd. Não muda entre deploys do mesmo ambiente,
// nem se o template for movido para outro RG / scope.
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var uniqueSuffix = substring(resourceToken, 0, 5)
var tags = {
  'azd-env-name': environmentName
}
var sanitizedEnvName = toLower(replace(replace(replace(replace(environmentName, ' ', '-'), '--', '-'), '[^a-zA-Z0-9-]', ''), '_', '-'))

var mcpAppName = take('ca-mcp-${sanitizedEnvName}-${uniqueSuffix}', 32)
var agentAppName = take('ca-agent-${sanitizedEnvName}-${uniqueSuffix}', 32)
var foundryAccountName = take('aif-${sanitizedEnvName}-${uniqueSuffix}', 24)
var foundryProjectName = take('aip-${sanitizedEnvName}-${uniqueSuffix}', 24)

// ====== User Assigned Identity ======
module appIdentity './modules/identity.bicep' = {
  name: 'uami'
  params: {
    location: location
    environmentName: environmentName
    uniqueSuffix: uniqueSuffix
  }
}

// ====== Log Analytics Workspace ======
module monitoring './modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    location: location
    environmentName: environmentName
    uniqueSuffix: uniqueSuffix
    tags: tags
  }
}

// ====== Container Registry ======
module containerRegistry './modules/containerregistry.bicep' = {
  name: 'registry'
  params: {
    location: location
    environmentName: environmentName
    uniqueSuffix: uniqueSuffix
    identityName: appIdentity.outputs.name
    tags: tags
  }
}

// ====== Container Apps Managed Environment (compartilhado) ======
module containerAppEnv './modules/containerappenv.bicep' = {
  name: 'cae'
  params: {
    location: location
    environmentName: environmentName
    uniqueSuffix: uniqueSuffix
    tags: tags
    logAnalyticsWorkspaceName: monitoring.outputs.workspaceName
  }
}

// ====== Azure AI Foundry (account + project + model deployment) ======
module foundry './modules/foundry.bicep' = {
  name: 'foundry'
  params: {
    location: location
    tags: tags
    foundryAccountName: foundryAccountName
    foundryProjectName: foundryProjectName
    modelName: foundryModelName
    modelVersion: foundryModelVersion
    modelDeploymentName: foundryModelName
    modelSkuName: foundryModelSkuName
    modelCapacity: foundryModelCapacity
    appInsightsId: monitoring.outputs.appInsightsId
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
  }
}

var effectiveProjectEndpoint = empty(aiProjectEndpoint) ? foundry.outputs.projectEndpoint : aiProjectEndpoint
var effectiveDeploymentName = empty(aiModelDeploymentName) ? foundry.outputs.deploymentName : aiModelDeploymentName

// ====== Container App: Ariba-MCP ======
module mcpApp './modules/containerapp.bicep' = {
  name: 'ca-ariba-mcp'
  params: {
    location: location
    tags: tags
    identityId: appIdentity.outputs.identityId
    containerRegistryName: containerRegistry.outputs.name
    containerAppEnvId: containerAppEnv.outputs.id
    serviceName: 'ariba-mcp'
    containerAppName: mcpAppName
    targetPort: 8000
    secrets: empty(aribaClientSecret) ? {} : {
      'ariba-client-secret': aribaClientSecret
    }
    envVars: union([
      { name: 'HOST', value: '0.0.0.0' }
      { name: 'ARIBA_USE_MOCK', value: aribaUseMock }
      { name: 'ARIBA_APP_ID', value: aribaAppId }
      { name: 'ARIBA_CLIENT_ID', value: aribaClientId }
      { name: 'ARIBA_REALM', value: aribaRealm }
      { name: 'AZURE_CLIENT_ID', value: appIdentity.outputs.clientId }
      { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: monitoring.outputs.appInsightsConnectionString }
      { name: 'OTEL_SERVICE_NAME', value: 'ariba-mcp' }
    ], empty(aribaClientSecret) ? [] : [
      { name: 'ARIBA_CLIENT_SECRET', secretRef: 'ariba-client-secret' }
    ])
  }
}

// ====== Container App: Ariba-Agent ======
module agentApp './modules/containerapp.bicep' = {
  name: 'ca-ariba-agent'
  params: {
    location: location
    tags: tags
    identityId: appIdentity.outputs.identityId
    containerRegistryName: containerRegistry.outputs.name
    containerAppEnvId: containerAppEnv.outputs.id
    serviceName: 'ariba-agent'
    containerAppName: agentAppName
    targetPort: 5000
    envVars: [
      { name: 'HOST', value: '0.0.0.0' }
      { name: 'ARIBA_MCP_URL', value: 'https://${mcpApp.outputs.containerAppFqdn}/mcp' }
      { name: 'AZURE_AI_PROJECT_ENDPOINT', value: effectiveProjectEndpoint }
      { name: 'FOUNDRY_PROJECT_ENDPOINT', value: effectiveProjectEndpoint }
      { name: 'AZURE_AI_MODEL_DEPLOYMENT_NAME', value: effectiveDeploymentName }
      { name: 'AZURE_CLIENT_ID', value: appIdentity.outputs.clientId }
      { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: monitoring.outputs.appInsightsConnectionString }
      { name: 'OTEL_SERVICE_NAME', value: 'ariba-agent' }
      { name: 'ENABLE_SENSITIVE_DATA', value: 'true' }
    ]
  }
}

// ====== Role assignment: UAMI -> Azure AI Foundry ======
// Sempre concede acesso ao Foundry provisionado por este template.
// Azure AI User -> data actions de agents/* (necessário para POST /api/projects/{name}/openai/*)
module foundryRoleProvisioned './modules/foundryRole.bicep' = {
  name: 'foundry-role-provisioned'
  params: {
    aiFoundryAccountName: foundry.outputs.accountName
    principalId: appIdentity.outputs.principalId
  }
}

// Cognitive Services User -> chamadas diretas ao endpoint OpenAI/CognitiveServices
module foundryRoleCogServices './modules/foundryRole.bicep' = {
  name: 'foundry-role-cogservices'
  params: {
    aiFoundryAccountName: foundry.outputs.accountName
    principalId: appIdentity.outputs.principalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908'
  }
}

// Cognitive Services OpenAI User -> permite POST /openai/deployments/{name}/chat/completions
module foundryRoleOpenAIUser './modules/foundryRole.bicep' = {
  name: 'foundry-role-openai-user'
  params: {
    aiFoundryAccountName: foundry.outputs.accountName
    principalId: appIdentity.outputs.principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
  }
}

// Role assignment adicional caso o usuário queira usar um Foundry externo já existente.
module foundryRole './modules/foundryRole.bicep' = if (!empty(aiFoundryAccountName) && !empty(aiFoundryResourceGroup)) {
  name: 'foundry-role-external'
  scope: resourceGroup(aiFoundryResourceGroup)
  params: {
    aiFoundryAccountName: aiFoundryAccountName
    principalId: appIdentity.outputs.principalId
  }
}

// ====== OUTPUTS ======
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup().name
output AZURE_SUBSCRIPTION_ID string = subscription().subscriptionId

output AZURE_USER_ASSIGNED_IDENTITY_ID string = appIdentity.outputs.identityId
output AZURE_USER_ASSIGNED_IDENTITY_CLIENT_ID string = appIdentity.outputs.clientId

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer

output APPLICATIONINSIGHTS_CONNECTION_STRING string = monitoring.outputs.appInsightsConnectionString
output APPLICATIONINSIGHTS_NAME string = monitoring.outputs.appInsightsName

output AZURE_AI_FOUNDRY_ACCOUNT_NAME string = foundry.outputs.accountName
output AZURE_AI_FOUNDRY_PROJECT_NAME string = foundry.outputs.projectName
output AZURE_AI_PROJECT_ENDPOINT string = effectiveProjectEndpoint
output AZURE_AI_MODEL_DEPLOYMENT_NAME string = effectiveDeploymentName

output ARIBA_MCP_ENDPOINT string = 'https://${mcpApp.outputs.containerAppFqdn}'
output ARIBA_AGENT_ENDPOINT string = 'https://${agentApp.outputs.containerAppFqdn}'

output SERVICE_API_ENDPOINTS array = [
  'https://${mcpApp.outputs.containerAppFqdn}/'
  'https://${agentApp.outputs.containerAppFqdn}/'
]
