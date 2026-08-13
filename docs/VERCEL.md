# Deploy do frontend na Vercel

O frontend do PrMO é um site **estático de arquivo único** (`frontend/index.html`) que consome a
API em `https://prmo-api.onrender.com`. Não requer build. Está hospedado na Vercel em paralelo
ao GitHub Pages.

## Serviço em produção (Vercel)
| Item | Valor |
|------|-------|
| URL de produção | **https://prmo-frontend.vercel.app** |
| Alias | `prmo-frontend-vanguardaos-projetos.vercel.app` |
| Projeto | `prmo-frontend` |
| Equipe/scope | `vanguardaos-projetos` |
| Origem | `frontend/index.html` (estático, sem build) |
| API consumida | `https://prmo-api.onrender.com` (CORS `*`) |
| Deployment Protection | **Desabilitada** (acesso público) |

> Deploy feito via CLI (`vercel deploy --prod --scope vanguardaos-projetos`). O token de deploy é
> de uso pontual e **não** é versionado — rotacione/revogue em https://vercel.com/account/tokens.
> Redeploys manuais: rode a CLI a partir de uma cópia de `frontend/` ou conecte o repositório ao projeto.

## Opção A — Importar o repositório (recomendado)
1. Acesse https://vercel.com/new e **importe** o repositório `jussaracavalcante-sketch/Governan-a_vanguarda`.
2. Em **Configure Project**:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Other
   - **Build Command:** (vazio) · **Output Directory:** (vazio) · **Install Command:** (vazio)
3. **Branch de produção:** `claude/prompts-repo-infrastructure-08dmf1` (ou `main`, conforme o padrão do repo).
4. **Deploy.** A Vercel publica `index.html` na raiz e gera uma URL `*.vercel.app`.

Com Root Directory = `frontend`, o `index.html` é servido em `/` automaticamente (não precisa de `vercel.json`).

## Opção B — Deploy da raiz do repositório
Se importar sem alterar o Root Directory, o [`vercel.json`](../vercel.json) na raiz reescreve `/`
para `/frontend/index.html`, e o [`.vercelignore`](../.vercelignore) evita publicar `backend/`, `docs/`, etc.

## Opção C — CLI (requer token)
```bash
npm i -g vercel
vercel login            # ou: export VERCEL_TOKEN=...
cd frontend && vercel --prod
```

## Observações
- **CORS:** a API já permite qualquer origem, então o domínio `*.vercel.app` funciona sem ajustes.
- **Domínio/API:** para apontar a outra API, edite a constante `API` em `frontend/index.html`.
- **Cold start:** primeira chamada após ociosidade pode levar ~50s (plano gratuito do Render).
