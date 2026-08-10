# Runbook — Migração do app Lovable "Vanguarda Builder" para Supabase + Vercel

> **App:** Vanguarda Builder (gerador de landing pages com IA) · protótipo em
> <https://vanguardabuilder.lovable.app/>
> **Origem:** hospedagem Lovable + Supabase gerenciado (Lovable Cloud)
> **Destino:** código na **Vercel** + **Supabase próprio** (org `jussaracavalcante-sketch's Org`)
> **Stack esperada:** React + Vite + TypeScript + Tailwind/shadcn + `@supabase/supabase-js`

Este runbook é auto-contido: siga fase a fase. Os templates prontos estão em
`migration/vercel.json` e `migration/.env.vercel.example`.

---

## ⚠️ Bloqueios/pré-requisitos conhecidos

1. **Billing do Supabase (BLOQUEIO ATIVO).** A criação de projeto falhou com
   `PaymentRequiredException: There are overdue invoices in the organization(s) VTech`.
   Enquanto houver faturas em aberto na org **VTech**, a conta inteira fica
   impedida de criar novos projetos.
   **Ação:** Supabase Dashboard → org **VTech** → *Billing / Invoices* → quitar as
   faturas em aberto. Depois disso a criação do projeto (Fase 1) volta a funcionar.

2. **Acesso ao código-fonte.** O código do app não está em nenhum repositório
   desta sessão. Traga-o para um repo da conta `jussaracavalcante-sketch/…`:
   - No Lovable: **projeto → GitHub → Connect/Transfer to GitHub** (recomendado); **ou**
   - Ative o **conector "Lovable"** no chat do Claude para inspecionar/exportar via MCP.

3. **Ferramentas locais** (para a pessoa que executar manualmente):
   - Node 18+ e npm
   - Supabase CLI: `npm i -g supabase` (ou `npx supabase`)
   - Vercel CLI (opcional): `npm i -g vercel`

---

## Fase 0 — Inventário do que existe no Lovable

Antes de migrar, catalogue o que o projeto de origem usa. No código Lovable,
procure em `supabase/`:

- `supabase/config.toml` — id do projeto, config de auth/storage
- `supabase/migrations/*.sql` — **schema** (tabelas, RLS, funções, triggers, enums)
- `supabase/functions/*/` — **Edge Functions** (Deno)
- No dashboard Supabase de origem: **Auth providers**, **Storage buckets**,
  **Database → Functions/Triggers**, e **Edge Functions → Secrets** (nomes das chaves)

> Se `supabase/migrations/` existir no repo, ele é a fonte da verdade do schema.
> Se não existir, gere um dump (Fase 1.3).

Liste também as integrações do app: pela landing, ele fala com **HubSpot,
RD Station e Pipedrive** e provavelmente um provedor de IA (OpenAI/Anthropic).
Cada um vira um **secret de Edge Function** no destino.

---

## Fase 1 — Provisionar o Supabase próprio

### 1.1 Criar o projeto
Região **São Paulo (`sa-east-1`)**, org `jussaracavalcante-sketch's Org`.
(Pode ser feito via Supabase MCP no Claude assim que o billing for resolvido,
ou no dashboard.) Guarde: `Project URL`, `project-ref`, `anon/publishable key`,
`service_role key` e a **senha do banco**.

### 1.2 Aplicar o schema (caminho preferido: migrations versionadas)
No repo do app já ligado ao Supabase novo:
```bash
supabase login
supabase link --project-ref <NOVO_project-ref>
supabase db push          # aplica supabase/migrations/*.sql no destino
```

### 1.3 Se NÃO houver migrations — dump do projeto de origem
Com a connection string do projeto **de origem** (Lovable Cloud):
```bash
# Schema
supabase db dump --db-url "postgresql://postgres:<SENHA_ORIGEM>@db.<ref-origem>.supabase.co:5432/postgres" -f schema.sql
# Dados (somente dados)
supabase db dump --db-url "postgresql://postgres:<SENHA_ORIGEM>@db.<ref-origem>.supabase.co:5432/postgres" --data-only -f data.sql
```
Depois aplique no **destino**:
```bash
psql "postgresql://postgres:<SENHA_DESTINO>@db.<ref-destino>.supabase.co:5432/postgres?sslmode=require" -f schema.sql
psql "postgresql://postgres:<SENHA_DESTINO>@db.<ref-destino>.supabase.co:5432/postgres?sslmode=require" -f data.sql
```
> A connection string da origem, sendo Lovable Cloud, aparece em
> Supabase (do projeto Lovable) → **Project Settings → Database → Connection string**.

### 1.4 Migrar dados (se aplicável)
Se usou migrations (1.2), migre só os **dados** com o `--data-only` acima. Se o
app ainda não tem dados reais de produção, pule.

### 1.5 Edge Functions
Para cada função em `supabase/functions/<nome>/`:
```bash
supabase functions deploy <nome> --project-ref <NOVO_project-ref>
```
(ou via Supabase MCP `deploy_edge_function`).

### 1.6 Secrets das Edge Functions
Recrie no destino **todas** as chaves que a origem usava (não são migradas
automaticamente):
```bash
supabase secrets set OPENAI_API_KEY=... HUBSPOT_TOKEN=... RD_STATION_TOKEN=... --project-ref <NOVO_project-ref>
```

### 1.7 Storage (buckets + policies)
Recrie os buckets (mesmos nomes e visibilidade public/private) e as policies de
storage no destino. Para copiar arquivos existentes, use um script com
`@supabase/supabase-js` (download da origem → upload no destino) ou `rclone`.

### 1.8 Auth
- **Providers:** reative os mesmos provedores (Email, Google, etc.) no destino.
- **Templates de e-mail:** recopie se foram customizados.
- **URLs (crítico p/ login funcionar):** deixe para a Fase 3.3, quando já
  existir o domínio da Vercel.

---

## Fase 2 — Preparar o código para a Vercel

Trabalhe no repo do app (não neste repo de governança).

### 2.1 Apontar o client do Supabase para o projeto novo
Edite `src/integrations/supabase/client.ts`. O ideal é ler de env em vez de
valores fixos:
```ts
const url = import.meta.env.VITE_SUPABASE_URL as string;
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string; // ou VITE_SUPABASE_ANON_KEY
export const supabase = createClient(url, key);
```
Confira qual nome de variável o arquivo usa e mantenha o mesmo em todo lugar.

### 2.2 Remover acoplamentos do Lovable no build
Em `vite.config.ts`, o `lovable-tagger` (componentTagger) é só de dev — mantenha-o
condicionado ao modo development ou remova:
```ts
plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
```
Assim o build de produção na Vercel não depende dele.

### 2.3 Adicionar o `vercel.json`
Copie `migration/vercel.json` (deste repo) para a **raiz** do repo do app. Ele
define preset Vite, saída `dist` e o *rewrite* de SPA (todas as rotas →
`index.html`) — essencial para o React Router não dar 404 em refresh.

### 2.4 `.gitignore`
Garanta que `.env`, `.env.local` e `dist/` estejam ignorados. Nunca versione
`service_role` nem senhas.

---

## Fase 3 — Deploy na Vercel

### 3.1 Importar o projeto
Vercel → **Add New → Project** → importe o repo `jussaracavalcante-sketch/…`.
Framework Preset: **Vite** (detectado). Build: `npm run build` · Output: `dist`.

### 3.2 Variáveis de ambiente
Use `migration/.env.vercel.example` como referência. Cadastre em
**Settings → Environment Variables** (Production **e** Preview):
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY` **ou** `VITE_SUPABASE_ANON_KEY` (o que o app lê)
- `VITE_SUPABASE_PROJECT_ID`

Faça o primeiro **Deploy** e anote a URL (`https://<app>.vercel.app`).

### 3.3 Fechar o loop do Auth (Supabase → Vercel)
No Supabase do destino → **Authentication → URL Configuration**:
- **Site URL:** `https://<app>.vercel.app` (ou domínio custom)
- **Redirect URLs:** adicione `https://<app>.vercel.app/**` e os previews
  `https://*-<org>.vercel.app/**` se usar login em previews.
Sem isso, o login/OAuth redireciona errado.

### 3.4 CORS / origens permitidas
Se alguma Edge Function valida `Origin`, inclua o domínio da Vercel na allowlist.

### 3.5 Domínio custom (opcional)
Vercel → **Settings → Domains** → adicione o domínio e ajuste o DNS. Depois
atualize Site/Redirect URL do Supabase para o domínio final.

---

## Fase 4 — Cutover e verificação

Checklist de aceite (rodar na URL da Vercel):
- [ ] App carrega sem erros de console (sem 404 de assets)
- [ ] `/auth` — cadastro, login, logout e reset de senha funcionam
- [ ] Refresh em rota interna (ex.: `/projetos`) **não** dá 404 (rewrite OK)
- [ ] Fluxo principal: criar projeto → gerar landing page (chama Edge Function/IA)
- [ ] Upload de briefing (PDF/DOCX) grava no Storage do projeto novo
- [ ] Integrações: HubSpot / RD Station / Pipedrive respondem
- [ ] RLS: usuário só enxerga os próprios dados (teste com 2 contas)
- [ ] `supabase → Logs` e Vercel → Logs sem erros recorrentes

### Rollback
O app Lovable original continua no ar durante toda a migração. Se algo falhar,
o destino Vercel/Supabase é descartável: não aponte o domínio de produção para a
Vercel até o checklist passar 100%. Reverter = voltar o DNS/domínio para o Lovable.

---

## Mapa rápido de "de → para"

| Item | Origem (Lovable) | Destino |
|------|------------------|---------|
| Hospedagem do front | Lovable | **Vercel** (preset Vite) |
| Banco/Auth/Storage | Supabase gerenciado (Lovable Cloud) | **Supabase próprio** (`sa-east-1`) |
| Schema | `supabase/migrations/` ou dump | `supabase db push` / `psql` |
| Edge Functions | `supabase/functions/` | `supabase functions deploy` |
| Segredos de servidor | Secrets no Supabase de origem | **Secrets** no Supabase destino (recriar) |
| Config do front | valores fixos no `client.ts` | `VITE_*` na Vercel |
| Auth redirect | domínio `.lovable.app` | domínio `.vercel.app` / custom |

---

## Status desta sessão

- ✅ App de origem identificado (Vanguarda Builder) e stack mapeada.
- ✅ Conectores verificados: **Supabase** ativo; **Lovable/HubSpot/RD Station** presentes mas desligados no chat.
- ✅ Templates entregues: `migration/vercel.json`, `migration/.env.vercel.example`.
- ⛔ **Criação do Supabase bloqueada por billing** (faturas em aberto na org VTech) — ver Pré-requisito #1.
- ⏭️ Próximo: (a) quitar billing → criar projeto; (b) trazer o código para um repo `jussaracavalcante-sketch/…` ou ligar o conector Lovable.
