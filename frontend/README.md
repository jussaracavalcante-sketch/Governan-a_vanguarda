# Gestão HEAD de IA — Frontend

SPA em **React + TypeScript + Vite** que consome a API FastAPI do backend.

## Scripts

```bash
npm install
npm run dev        # servidor de desenvolvimento (http://localhost:5173)
npm run build      # typecheck + build de produção em dist/
npm run preview    # pré-visualiza o build
npm run typecheck  # checagem de tipos
npm run lint       # ESLint
```

## Configuração da API

A URL da API vem de `VITE_API_BASE_URL` (ver `.env.example`):

- **Dev**: deixe vazio — o Vite faz proxy de `/api` → `http://localhost:8000`.
- **Prod**: aponte para o backend publicado, ex.: `https://head_ia-api.onrender.com`.

## Estrutura

```
src/
├── main.tsx              # bootstrap
├── App.tsx               # rotas (HashRouter) + providers
├── components/
│   ├── ui/               # Card, Button, Badge, Modal, Table, StatCard
│   └── layout/           # Layout (sidebar + topbar), PageHead
├── context/              # AuthContext (JWT), ThemeContext (dark/light)
├── lib/                  # api client, useAsync
├── pages/                # Login, Dashboard, Prompts, Tools, Skills, Access, Admin
├── styles/               # tokens (design system) + global
└── types/                # tipos compartilhados (alinhados aos schemas do backend)
```

## Autenticação

Login via `POST /auth/login`; o access token JWT é guardado em `localStorage` e
enviado no header `Authorization: Bearer`. Rotas são protegidas por `AuthContext`,
com controle de acesso por perfil (Admin/Manager/User) na navegação.

## Deploy

Build estático em `dist/` — publicado no GitHub Pages via workflow
`.github/workflows/deploy-frontend-pages.yml`. Usa `base: './'` e HashRouter para
funcionar em subcaminho sem 404 em refresh.
