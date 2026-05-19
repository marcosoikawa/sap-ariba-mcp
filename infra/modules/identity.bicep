// modules/identity.bicep
// Cria uma Managed Identity para o Container App acessar recursos do Azure

param location string
param environmentName string
param uniqueSuffix string

var sanitizedEnvName = toLower(replace(replace(replace(replace(environmentName, ' ', ''), '--', ''), '[^a-zA-Z0-9-]', ''), '_', ''))
var userIdentityName = take('${sanitizedEnvName}-${uniqueSuffix}-id', 32)

resource appIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: userIdentityName
  location: location
}

output identityId string = appIdentity.id
output clientId string = appIdentity.properties.clientId
output principalId string = appIdentity.properties.principalId
output name string = appIdentity.name
