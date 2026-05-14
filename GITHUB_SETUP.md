# 🚀 Guia: Enviando para GitHub

O repositório foi inicializado e preparado para upload no GitHub. Siga os passos abaixo:

## 1. Criar Repositório Vazio no GitHub

1. Acesse https://github.com/new
2. **Nome do repositório:** `sap-ariba-mcp`
3. **Descrição:** `Workspace com servidor MCP e agente de procurement para SAP Ariba`
4. **Visibilidade:** Escolha entre Public ou Private
5. **NÃO** marque "Initialize this repository with" (sem README, .gitignore, LICENSE)
6. Clique "Create repository"

## 2. Adicionar Remote e Fazer Push

```bash
# Substitua SEU_USUARIO pelo seu username do GitHub
cd /workspaces/sap-ariba-mcp

# Adicionar o remote
git remote add origin https://github.com/SEU_USUARIO/sap-ariba-mcp.git

# Renomear branch de master para main (recomendado)
git branch -M main

# Fazer push
git push -u origin main
```

## 3. Verificar no GitHub

Acesse https://github.com/SEU_USUARIO/sap-ariba-mcp e confirme que:
- ✅ Todos os arquivos estão presentes
- ✅ `.env` e `__pycache__/` **NÃO** aparecem (protegidos por .gitignore)
- ✅ README.md está renderizado
- ✅ Branches estão sincronizadas

## 4. (Opcional) Adicionar Deploy Automático

Para Azure CI/CD:

```bash
# Criar arquivo GitHub Actions
mkdir -p .github/workflows
```

Crie `.github/workflows/deploy.yml` com pipeline de build/deploy.

## 5. (Opcional) Adicionar Branch Protection

No GitHub:
1. Settings → Branches
2. Add rule → Branch name pattern: `main`
3. ✅ Require pull request reviews
4. ✅ Require status checks to pass

## Comando Rápido (One-Liner)

Se já tiver criado o repositório vazio no GitHub:

```bash
cd /workspaces/sap-ariba-mcp
git remote add origin https://github.com/SEU_USUARIO/sap-ariba-mcp.git
git branch -M main
git push -u origin main
```

## ✨ Pronto!

Seu projeto está pronto para colaboração em GitHub. Para trabalhar com branches:

```bash
# Criar feature branch
git checkout -b feature/minha-feature

# Após finish
git push origin feature/minha-feature
# → Abrir Pull Request no GitHub
```

---

**Dúvidas?** Consulte:
- [GitHub Help](https://docs.github.com/en/github)
- [Git Documentation](https://git-scm.com/doc)
