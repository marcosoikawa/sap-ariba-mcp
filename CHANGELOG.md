# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2026-05-14

### Added
- Servidor MCP (FastMCP) expondo ferramentas de SAP Ariba Event Management API v2
  - `list_events`, `get_event`, `list_participants`, `list_bids`, `event_summary`
- Agente de procurement (Microsoft Agent Framework + Foundry)
  - Interface web Flask em `http://localhost:5000`
  - Autenticação via Azure DefaultAzureCredential (sem API key)
  - Suporte a histórico de chat
- Devcontainer configurado para VS Code
- Docker e docker-compose para fácil deployment
- Suporte a dados mock do Ariba para testes sem credenciais
- Documentation completa em README.md

### Fixed
- Compatibilidade com agent-framework 1.3.0
- Suporte correto a Message objects e FoundryChatClient
- Setup do devcontainer com validação de imports

### Known Issues
- Avisos experimentais do agent-framework (MemoryStore, SkillResource) são apenas informativos

## Roadmap

- [ ] Suporte a persistência de histórico em banco de dados
- [ ] Deploy em Azure Container Apps com Managed Identity
- [ ] Testes unitários e integração
- [ ] CI/CD via GitHub Actions
- [ ] Websocket para real-time updates
- [ ] Suporte a múltiplos usuários/sessões
