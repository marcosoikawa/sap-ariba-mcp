// modules/containerapp.bicep
// Cria um Container App para um serviço específico (ariba-mcp ou ariba-agent)
// dentro de um Managed Environment já existente.

param location string
param tags object
param identityId string
param containerRegistryName string
param containerAppEnvId string

@description('Nome lógico do serviço (azd-service-name). Ex.: ariba-mcp, ariba-agent.')
param serviceName string

@description('Nome do recurso do Container App.')
param containerAppName string

@description('Porta interna exposta pelo container.')
param targetPort int

@description('Imagem inicial. Use um placeholder até o azd publicar a imagem real.')
param imageName string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Variáveis de ambiente extras (name/value ou name/secretRef).')
param envVars array = []

@description('Secrets do Container App (name/value).')
@secure()
param secrets object = {}

var secretNames = [for k in items(secrets): { name: k.key, value: k.value }]

resource containerApp 'Microsoft.App/containerApps@2024-10-02-preview' = {
  name: containerAppName
  location: location
  tags: union(tags, { 'azd-service-name': serviceName })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identityId}': {} }
  }
  properties: {
    managedEnvironmentId: containerAppEnvId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
      }
      registries: [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: identityId
        }
      ]
      secrets: secretNames
    }
    template: {
      containers: [
        {
          name: 'main'
          image: imageName
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: union([
            {
              name: 'PORT'
              value: string(targetPort)
            }
          ], envVars)
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaler'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output containerAppId string = containerApp.id
output containerAppName string = containerApp.name
