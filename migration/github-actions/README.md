# Workflows de CI/CD — repo do app (VanguardaHub/Vanguardabuilders)

Estes arquivos são **templates**. Copie-os para a raiz do repositório do app,
dentro de `.github/workflows/`:

```
Vanguardabuilders/
└── .github/
    └── workflows/
        ├── deploy-vercel.yml          # <- migration/github-actions/deploy-vercel.yml
        └── supabase-migrations.yml    # <- migration/github-actions/supabase-migrations.yml
```

## Secrets a cadastrar (Repo → Settings → Secrets and variables → Actions)

| Secret | Onde obter | Usado por |
|--------|-----------|-----------|
| `VERCEL_TOKEN` | Vercel → Account Settings → Tokens | deploy-vercel |
| `VERCEL_ORG_ID` | `.vercel/project.json` após `vercel link` | deploy-vercel |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` após `vercel link` | deploy-vercel |
| `SUPABASE_ACCESS_TOKEN` | Supabase → Account → Access Tokens | supabase-migrations |
| `SUPABASE_PROJECT_REF` | subdomínio da URL do projeto novo | supabase-migrations |
| `SUPABASE_DB_PASSWORD` | senha do banco do projeto novo | supabase-migrations |

> As variáveis `VITE_SUPABASE_*` **não** ficam aqui — elas vão no projeto da
> Vercel (Settings → Environment Variables). Ver `../.env.vercel.example`.

## Decisão: Actions vs. integração nativa da Vercel

O jeito mais simples de deploy é conectar o repo pela **integração
Vercel↔GitHub** (deploy automático a cada push, previews em PR, zero YAML). Use
o `deploy-vercel.yml` apenas se quiser o pipeline dentro do GitHub Actions
(ex.: para rodar testes/migrations antes do deploy). Os dois não precisam
coexistir — escolha um para produção.
