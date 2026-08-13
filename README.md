# Gestão HEAD de IA

Painel de gestão do HEAD de IA — um app **independente** para o dia a dia da
operação, que **apenas consulta** a ferramenta de governança **PrMO** (somente
leitura).

## O que o app faz

| Módulo | Descrição |
|---|---|
| 🧠 Visão Geral | Painel inicial com indicadores do HEAD + Visão do PrMO (consulta) |
| 🗂️ Controle de Ativos | Cadastro de ativos digitais: custo/mês, criticidade, ambiente |
| ✅ Tarefas do Dia a Dia | Tarefas com horas, prioridade e status |
| 📈 Indicadores & KPIs | Metas vs. realizado |
| 🗓️ Relatórios Mensais | Consolidação por período |
| 🔑 Controle de Licenças | Assentos, renovação e custo |
| ⚙️ Otimização de Processos | PDCA + matriz Impacto × Esforço |
| 📖 Base de Conhecimento | Artigos com tags e busca |

## Arquitetura

```
frontend/   SPA React + TypeScript + Vite (deploy: GitHub Pages)
backend/    API FastAPI + SQLAlchemy (deploy: Render)
docs/       Guia de banco (Supabase/PostgreSQL)
```

- **Infra própria e separada:** banco e API exclusivos do HEAD de IA.
- **PrMO:** o app apenas **consulta** o PrMO (somente leitura) via `PRMO_BASE_URL`.

## Rodar localmente

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload        # http://localhost:8000  (docs em /docs)
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

Login inicial (seed): `admin@headia.app` · `admin123` (troque em produção).

## Deploy

- **Frontend → GitHub Pages:** workflow `.github/workflows/deploy-frontend-pages.yml`
  (dispara no push para `main`). Defina a variável de repositório
  `VITE_API_BASE_URL` com a URL do backend.
- **Backend → Render:** `render.yaml` (Blueprint). Ajuste `ADMIN_PASSWORD`,
  `ADMIN_EMAIL` e, para persistência, `DATABASE_URL` (Supabase/PostgreSQL — ver
  `docs/SUPABASE.md`).

## Testes

```bash
cd backend && pytest -v
cd frontend && npm run build
```
