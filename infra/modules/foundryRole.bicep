// modules/foundryRole.bicep
// Concede acesso à User-Assigned Managed Identity no recurso Azure AI Foundry
// (Microsoft.CognitiveServices/accounts) usado pelo agente.

param aiFoundryAccountName string
param principalId string

@description('Role definition ID. Default: Azure AI User (53ca6127-db72-4b80-b1b0-d745d6d5456d) — inclui data actions de agents/write necessárias para chamar Foundry OpenAI via projeto.')
param roleDefinitionId string = '53ca6127-db72-4b80-b1b0-d745d6d5456d'

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
