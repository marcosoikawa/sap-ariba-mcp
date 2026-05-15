// main.bicep
// Infraestrutura mínima para Container Apps + Container Registry

param location string = resourceGroup().location
param envName string = 'ariba-mcp'

resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: '${envName}acr'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource mcpApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${envName}-mcp'
  location: location
  properties: {
    managedEnvironmentId: '' // Preencher conforme ambiente
    configuration: {
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          password: acr.listCredentials().passwords[0].value
        }
      ]
      secrets: []
    }
    template: {
      containers: [
        {
          name: 'ariba-mcp'
          image: '${acr.properties.loginServer}/ariba-mcp:latest'
          env: []
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
    ingress: {
      external: true
      targetPort: 8000
    }
  }
}

resource agentApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${envName}-agent'
  location: location
  properties: {
    managedEnvironmentId: '' // Preencher conforme ambiente
    configuration: {
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          password: acr.listCredentials().passwords[0].value
        }
      ]
      secrets: []
    }
    template: {
      containers: [
        {
          name: 'ariba-agent'
          image: '${acr.properties.loginServer}/ariba-agent:latest'
          env: []
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
    ingress: {
      external: true
      targetPort: 5000
    }
  }
}
