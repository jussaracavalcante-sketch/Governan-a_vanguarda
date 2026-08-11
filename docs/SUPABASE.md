# Banco de Dados — Supabase (PrMO)

> O banco de dados de produção do **PrMO** é o **Supabase/PostgreSQL**, tratado como
> infraestrutura externa a este repositório. O código é agnóstico: usa **SQLite**
> por padrão (dev) e qualquer `DATABASE_URL` PostgreSQL em produção.

## 1. Projeto provisionado

| Item | Valor |
|------|-------|
| Projeto | `prmo-governanca` |
| Ref | `ubixfcoigwpjdrioymdq` |
| Região | `sa-east-1` (São Paulo) |
| Postgres | 17.x |
| API URL | `https://ubixfcoigwpjdrioymdq.supabase.co` |
| Organização | `jussaracavalcante-sketch's Org` |

O **schema completo** (18 tabelas + 4 enums + índices/FKs) e os **dados migrados**
já foram aplicados neste projeto (ver §5). O repositório **não** contém credenciais.

## 2. Princípio

- A conexão é definida **exclusivamente** por variável de ambiente (`DATABASE_URL`).
- A senha do banco **nunca** entra no repositório (público). No Render, `DATABASE_URL`
  está como `sync: false` (valor definido só no painel).

## 3. Obter a senha e a connection string

A senha do banco é gerada no provisionamento e **não** fica exposta. Para obter uma
senha conhecida:

1. Supabase → **Project Settings → Database → Reset database password** → copie a senha.
2. Ainda em **Database**, botão **Connect** → aba **Session pooler** → copie a URI.

> Use o **Session pooler** (IPv4, porta 5432). A conexão direta
> (`db.<ref>.supabase.co`) é **IPv6-only** e o Render não a alcança.

## 4. Formato do `DATABASE_URL`

O backend usa SQLAlchemy + `psycopg2` — prefixe o driver com `postgresql+psycopg2://`.

**Session pooler (recomendado — Render/serverless):**
```
postgresql+psycopg2://postgres.ubixfcoigwpjdrioymdq:<SENHA>@aws-0-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

**Conexão direta (migrações/jobs, ambiente com IPv6):**
```
postgresql+psycopg2://postgres:<SENHA>@db.ubixfcoigwpjdrioymdq.supabase.co:5432/postgres?sslmode=require
```

> ⚠️ Confira o host exato do pooler no painel (`aws-0-...` ou `aws-1-...`).
> Caracteres especiais na senha devem ser **URL-encoded** (`@`→`%40`, `#`→`%23`).
> Sempre inclua `sslmode=require`.

## 5. O que já foi migrado

Aplicado via MCP do Supabase (migrações `prmo_initial_schema` e
`prmo_reset_identity_and_enable_rls`):

- **Schema**: 18 tabelas (`users`, `gov_*`, `audit_logs`, `integration_*`, …),
  4 enums (`userrole`, `userstatus`, `skilllevel`, `toolstatus`), PKs `IDENTITY`,
  índices e FKs — idênticos ao `Base.metadata.create_all` do backend.
- **Dados** (carregados a partir do seed, anonimizados):
  - `gov_registry`: **258** registros (asset 93, diagnostic 45, knowledge 52,
    opportunity 8, plan30 27, risk 33);
  - `gov_prompts`: **55** (3 curados + **52 candidatos** do mapeamento, `Revisão pendente`);
  - `users` 5, `gov_clients` 4, `gov_stack_tools` 4, `gov_skills` 4, `gov_training` 4,
    `gov_initiatives` 4, `gov_adoption` 4, `gov_incidents` 3, `gov_cost_policy` 1,
    `activities` 4, `tools` 4, `skills` 4, `prompts` 4.
- Sequências `IDENTITY` reajustadas para `max(id)+1` (inserts novos não colidem).

O seed do backend é **idempotente** (guardas por “já existe”): apontar o Render
para este banco já populado **não duplica** dados.

## 6. Segurança — RLS

- **RLS ativado em todas as tabelas** do schema `public`, **sem policies**
  (deny-by-default): a Data API (chaves `anon`/`publishable`) **não** lê nem escreve.
- O backend conecta como papel **`postgres`**, que **ignora RLS** — acesso total
  mediado pela API FastAPI (com JWT + RBAC do PrMO).
- Advisor de segurança: apenas avisos `INFO rls_enabled_no_policy` — que é
  justamente o estado pretendido nesta arquitetura (sem acesso direto do cliente).
- Rotacione a senha do banco periodicamente e mantenha a `SECRET_KEY` da aplicação
  separada da `DATABASE_URL`.

## 7. Apontar o backend para o Supabase

### Render (produção)
1. Painel do Render → serviço `prmo-api` → **Environment**.
2. Defina `DATABASE_URL` com a URI do **Session pooler** (§4), incluindo a senha.
3. **Manual Deploy / Save** → o backend cria/reaproveita o schema e valida o seed no boot.

### Local (`.env`)
```env
DATABASE_URL=postgresql+psycopg2://postgres.ubixfcoigwpjdrioymdq:<SENHA>@aws-0-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

## 8. Schema versionado

O DDL autoritativo aplicado está em [`db/supabase_schema.sql`](../db/supabase_schema.sql).
Para versionar mudanças futuras de schema, considere Alembic.
