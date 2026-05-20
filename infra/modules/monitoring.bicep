// modules/monitoring.bicep
// Cria Log Analytics Workspace + Application Insights (workspace-based).

param location string
param environmentName string
param uniqueSuffix string
param tags object = {}

var abbrs = loadJsonContent('../abbreviations.json')
var sanitizedEnvName = toLower(replace(replace(replace(replace(environmentName, ' ', '-'), '--', '-'), '[^a-zA-Z0-9-]', ''), '_', '-'))
var logAnalyticsName = take('${abbrs.operationalInsightsWorkspaces}${sanitizedEnvName}-${uniqueSuffix}', 63)
var appInsightsName = take('${abbrs.insightsComponents}${sanitizedEnvName}-${uniqueSuffix}', 260)

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

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

output workspaceName string = logAnalyticsWorkspace.name
output workspaceId string = logAnalyticsWorkspace.id
output customerId string = logAnalyticsWorkspace.properties.customerId

output appInsightsName string = appInsights.name
output appInsightsId string = appInsights.id
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
