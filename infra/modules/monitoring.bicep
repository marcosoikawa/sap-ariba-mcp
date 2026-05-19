// modules/monitoring.bicep
// Cria Log Analytics Workspace

param location string
param environmentName string
param uniqueSuffix string
param tags object = {}

var abbrs = loadJsonContent('../abbreviations.json')
var sanitizedEnvName = toLower(replace(replace(replace(replace(environmentName, ' ', '-'), '--', '-'), '[^a-zA-Z0-9-]', ''), '_', '-'))
var logAnalyticsName = take('${abbrs.operationalInsightsWorkspaces}${sanitizedEnvName}-${uniqueSuffix}', 63)

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

output workspaceName string = logAnalyticsWorkspace.name
output workspaceId string = logAnalyticsWorkspace.id
output customerId string = logAnalyticsWorkspace.properties.customerId
