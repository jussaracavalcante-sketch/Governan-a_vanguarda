# Banco de Dados — Supabase (infraestrutura externa)

> O banco de dados de produção do VANGUARDIAN é provisionado no **Supabase**, tratado
> como **infraestrutura externa** a este repositório. O código é agnóstico: usa
> **SQLite** por padrão (dev) e qualquer `DATABASE_URL` PostgreSQL em produção.

## 1. Princípio

- O repositório **não** contém credenciais nem cria o banco.
- A conexão é definida **exclusivamente** por variável de ambiente (`DATABASE_URL`).
- O projeto Supabase é gerido à parte (outra conta/organização/infra), com seu
  próprio ciclo de vida, backups e billing.

## 2. Provisionamento (feito fora do repositório)

1. Crie um projeto no Supabase (região sugerida: `sa-east-1` / São Paulo).
2. Em **Project Settings → Database**, copie a **Connection string** (URI).
3. Guarde a senha do banco em um cofre de segredos — **nunca** neste repositório.

## 3. Formato do `DATABASE_URL`

O backend usa SQLAlchemy + `psycopg2` (driver já incluído em
[`../backend/requirements.txt`](../backend/requirements.txt)).

**Connection pooler (recomendado para apps serverless / muitas conexões):**
```
postgresql://postgres.<project-ref>:<SENHA>@aws-1-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

**Conexão direta (migrações / jobs):**
```
postgresql://postgres:<SENHA>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require
```

> ⚠️ Caracteres especiais na senha (`@`, `#`, `:` …) devem ser **URL-encoded**
> (`@`→`%40`, `#`→`%23`). Sempre inclua `sslmode=require`.

## 4. Como apontar o backend para o Supabase

### Local (`.env`)
```env
DATABASE_URL=postgresql://postgres.<ref>:<SENHA>@aws-1-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

### Render (`render.yaml`)
Não versione a URL. Deixe `DATABASE_URL` **sem valor** no `render.yaml`
(`sync: false`) e configure o valor real no painel do Render (Environment).

### Docker Compose
Defina `DATABASE_URL` no `.env` (lido por `docker-compose.yml`). O `.env` é
ignorado pelo `git`.

## 5. Criação do schema

Na primeira execução, o backend cria as tabelas automaticamente
(`Base.metadata.create_all`) e roda o seed inicial (ver
[`../backend/main.py`](../backend/main.py)). Não é necessário migração manual para
o modelo atual. Para versionar mudanças de schema no futuro, considere Alembic.

## 6. Segurança

- Rotacione a senha do banco periodicamente e sempre que houver suspeita de vazamento.
- Restrinja acessos por rede/policies no Supabase.
- Mantenha a `SECRET_KEY` da aplicação separada da `DATABASE_URL`.
- Confira [`SECURITY.md`](../SECURITY.md) e [`PROPRIEDADE-INTELECTUAL.md`](PROPRIEDADE-INTELECTUAL.md).
