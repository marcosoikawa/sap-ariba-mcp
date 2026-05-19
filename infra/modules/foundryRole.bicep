// modules/foundryRole.bicep
// Concede acesso à User-Assigned Managed Identity no recurso Azure AI Foundry
// (Microsoft.CognitiveServices/accounts) usado pelo agente.

param aiFoundryAccountName string
param principalId string

@description('Role definition ID. Default: Azure AI Developer (64702f94-c441-49e6-a78b-ef80e0188fee).')
param roleDefinitionId string = '64702f94-c441-49e6-a78b-ef80e0188fee'

resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: aiFoundryAccountName
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  name: guid(foundry.id, principalId, roleDefinitionId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
    principalType: 'ServicePrincipal'
    principalId: principalId
  }
}
