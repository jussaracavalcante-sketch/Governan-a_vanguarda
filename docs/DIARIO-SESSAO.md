# Diário de Sessão — VANGUARDIAN

Registro cronológico do trabalho por sessão. Entrada mais recente no topo.

---

## 2026-08-10 — Infraestrutura, backend, protótipo funcional e BPMN

**Responsável:** Jussara Cavalcante (Diretoria de IA) · **Repositório:** `jussaracavalcante-sketch/Governan-a_vanguarda` · **Branch:** `claude/prompts-repo-infrastructure-08dmf1`

### 🎯 Objetivo da sessão
Transformar o protótipo VANGUARDIAN em um repositório governado de **prompts e propriedade intelectual**, com plataforma (frontend + API) publicada e funcional.

### ✅ Entregas
1. **Infraestrutura do repositório**
   - Estrutura base (backend, frontend, workflows, configs) + **PR #1 mergeado** na `main`.
   - **Biblioteca de prompts versionada** (`prompts/`) com template e norma **NIA-001**, catálogo e 4 prompts seed homologados.
   - **Docs de governança/PI**: `PROPRIEDADE-INTELECTUAL`, `NIA-001-norma-prompts`, `GOVERNANCA`, `ARQUITETURA`, `SUPABASE`.
   - Governança de contribuição: `CONTRIBUTING`, `SECURITY`, `CODEOWNERS`, templates de issue/PR.
   - CI (testes backend + validador de prompts NIA-001 + checagem do frontend), Docker e `render.yaml`.
2. **Backend FastAPI — publicado no Render**
   - Módulo `governance`: clientes, stack, prompts, skills, trilhas, iniciativas, adoção, ocorrências.
   - `/governance/overview` (KPIs), `/governance/audit` (trilha de auditoria), `/governance/observability`.
   - Correção: e-mail do admin `.local → .com` (TLD reservado causava HTTP 422 no login).
   - Correção: `DATABASE_URL` com SQLite padrão (evita boot quebrado no Render).
   - `psycopg2-binary` adicionado para suporte a PostgreSQL/Supabase.
3. **Frontend — protótipo oficial publicado no GitHub Pages**
   - Publicado o protótipo exato (`vanguardian-martech.html`), tema VANGUARDA.IA.
   - Religado à API: **login (JWT)**, tabelas dinâmicas, **6 cadastros salvando de verdade**, **KPIs dinâmicos**, **trilha de auditoria** e **observabilidade** em tempo real.
   - Cadastro de prompt: novo campo **"Repositório hospedado"** (`repo_url`) e status **"Reprovado"**.
   - Removido o menu/página **"Portfólio de clientes"** (passará a ser administrado pelo VanguardIA).
4. **Diagrama de arquitetura em BPMN**: `docs/arquitetura-bpmn.svg` e `.png` (swimlanes Usuário → Frontend → API → Dados/Observabilidade).

### 🔗 Ambientes e acessos
| Recurso | URL |
|---------|-----|
| App (GitHub Pages) | https://jussaracavalcante-sketch.github.io/Governan-a_vanguarda/ |
| API (Render) | https://vanguardian-api-omg6.onrender.com · Swagger em `/docs` |
| Blueprint Render | `Governança_vanguarda` (`exs-d9r3abiju40c73e5gv4g`) |

**Credenciais demo:** `admin@vanguardian.com` / `admin123` (Admin) · `ana.souza@empresa.com` / `123456` (Manager).

### 🧪 Validações feitas ao vivo
- Login (Admin e Manager) → HTTP 200 com JWT.
- Criar ocorrência crítica → indicadores mudaram na hora (auditorias, pendências, incidentes críticos).
- Trilha de auditoria registrou o evento (usuário, recurso, timestamp).
- Campo `repo_url` + "Reprovado" confirmados no schema após redeploy.
- Menu "Portfólio de clientes" ausente no site publicado (nav com 5 itens).

### 🧭 Decisões
- Frontend = **protótipo estático** publicado, **religado à API real** (opção do usuário).
- Banco: SQLite efêmero no free tier do Render por ora; **Supabase** como infra externa quando liberado.
- Módulo de clientes migra para o **VanguardIA** (`VanguardaHub/vanguardIA`).

### ⏳ Pendências / próximos passos
- [ ] **Supabase**: provisionamento bloqueado por **faturas em atraso da org "VTech"**. Após regularizar, criar projeto e definir `DATABASE_URL` no Render (ver `docs/SUPABASE.md`).
- [ ] **Rotacionar** a senha do Supabase que apareceu nas variáveis de ambiente.
- [ ] **Branch padrão → `main`**: troca pela UI retornou "Could not change default branch" (transitório) — repetir.
- [ ] **Integração VanguardIA**: sem acesso ao repo `VanguardaHub/vanguardIA` nesta sessão — abrir sessão com esse repo como fonte ou fornecer endpoints.
- [ ] **KPI "Clientes governados"**: hoje vem do seed local; decidir se oculta ou passa a consumir do VanguardIA.
- [ ] **Persistência**: no free tier o SQLite reseta a cada deploy/restart; mudanças de schema exigirão migração (Alembic) quando o banco for persistente.

---

<!-- Modelo para novas entradas:
## AAAA-MM-DD — Título
### 🎯 Objetivo
### ✅ Entregas
### 🧪 Validações
### 🧭 Decisões
### ⏳ Pendências
-->
