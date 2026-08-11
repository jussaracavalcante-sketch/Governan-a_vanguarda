# Diário de Sessão — PrMO (Prompt Management Office)

Registro cronológico do trabalho por sessão. Entrada mais recente no topo.

---

## 2026-08-10 (sessão 5) — Painéis com dados reais e prompts do mapeamento na Biblioteca

### 🎯 Objetivo
Fazer os painéis contabilizarem a base migrada (dados reais) e levar os prompts identificados no mapeamento para a Biblioteca.

### ✅ Entregas
- **`/overview` reescrito** para contabilizar a partir dos 258 registros (Diagnóstico + Asset/Risk/Knowledge/Opportunity). Passa a devolver KPIs reais e listas (`adocao`, `prioridades`, `riscos`, `stack_top`, `capacidade`, `knowledge_tipos`).
- **Frontend religado ao overview real** em todos os menus do controlador:
  - Visão executiva: 93 colaboradores · 28 dado sensível · 52 ativos (41 prompts) · 33 riscos (3 críticos/25 altos) · 147 gaps (68 colaboradores) · 8 oportunidades (4 P1) · 2,95 ferramentas/colab · 274 menções.
  - Adoção por macroárea (real), Backlog de oportunidades (prioridades), Ferramentas mais usadas (ChatGPT 81…), Capacidade por macroárea, Ativos por tipo, Riscos declarados (top), Compliance (exposição 35%, coorte crítica 3).
- **Importação de 52 candidatos** do Knowledge Registry para a **Biblioteca de prompts** (status "Revisão pendente", com KNOW-ID/área/tarefa) — fila de triagem/homologação. Biblioteca: 3 curados + 52 candidatos = 55.

### 🧪 Validações ao vivo
- `/overview` real ativo (dashboard/compliance/stack_top conferidos).
- Biblioteca com 55 prompts · 52 candidatos em Revisão pendente.

### 🧭 Decisões
- Biblioteca curada e "ativos do mapeamento" convivem: candidatos entram como Revisão pendente e são homologados pelo admin (com preenchimento do conteúdo).
- Dados sempre anonimizados enquanto o repositório for público.

### ⏳ Pendências (mantidas)
- Render `prmo-api` (Manual sync + repointar frontend), Supabase (persistência + carga não-anonimizada), branch padrão → `main`, integração VanguardIA, filtro por status/tipo na Biblioteca (opcional).

---

## 2026-08-10 (sessão 4) — Migração dos registros de governança (30 dias)

### 🎯 Objetivo
Migrar a planilha "Governança IA Vanguarda — Registros 30 dias" para a base, com proteção de dados (repo público).

### ✅ Entregas
- **Migração anonimizada** de 258 registros: AI Asset Registry (93), AI Risk Register (33), AI Knowledge Registry (52), Opportunity Backlog (8), Diagnóstico (45), Plano 30 dias (27).
- **Anonimização (LGPD)**: removidas colunas de nomes de colaboradores/líderes; nomes que vazavam em textos livres foram redigidos por dicionário derivado das próprias colunas pessoais (224 tokens); sem e-mail/CPF/telefone. O **xlsx original não foi versionado** — apenas o JSON anonimizado em `backend/data/registros_30dias.json`.
- **Backend**: modelo `RegistryRecord` + carregador no seed (recarrega do JSON a cada deploy) + endpoints `GET /governance/registry` e `/registry/{name}` restritos a Manager/Admin.
- **Frontend**: nova aba **"Registros (30d)"** (só controlador) com seletor de registro, tabela dinâmica e filtro.

### 🧪 Validações ao vivo
- `GET /governance/registry` → total 258 com as contagens por registro.
- User → 403 nos endpoints de registro; Manager → 200.

### 🔐 Nota de privacidade
Dados completos (com nomes) só devem ir para ambiente **privado** (Supabase). Enquanto o repo for público, mantém-se apenas a versão anonimizada.

### ⏳ Pendências (mantidas)
- Render `prmo-api`, Supabase (billing "VTech" — habilita carga completa não-anonimizada), branch padrão → `main`, integração VanguardIA.

---

## 2026-08-10 (sessão 3) — Homologação in-app e teto de custo por chamada

### 🎯 Objetivo
Fechar o fluxo de homologação e introduzir o controle de custo por chamada sob governança do PrMO.

### ✅ Entregas
- **Homologação in-app**: Admin/Manager aprovam/reprovam prompts direto na Biblioteca (`POST /governance/prompts/{id}/homologar`), atualizando controle + última revisão e gravando `APPROVE`/`REJECT` na trilha de auditoria. User → 403.
- **Teto de custo por chamada (política global do PrMO)**: modelo `CostPolicy` (teto + moeda) editável só por Manager/Admin (`GET/PUT /governance/cost-policy`, PUT auditado); teto inicial **R$ 0,50**.
- **Custo por prompt + alerta**: campo `cost_per_call` no cadastro; coluna **Custo/chamada** na lista com badge **"acima do teto"**; indicador do teto e botão **"Teto de custo"** (admin). `/overview` expõe `custo` (teto, moeda, prompts acima/avaliados).
- **Limpeza**: nomes internos "VANGUARDIAN" → "PrMO" no backend. `render.yaml` com `name: prmo-api` (efetivo só em nova sync de blueprint).

### 🧪 Validações ao vivo
- Homologação: Manager aprova prompt → `control=Aprovado`, `last_review` atualizada, auditoria `APPROVE`.
- Custo: `GET /cost-policy` = R$ 0,50; `overview.custo` = 1 acima de 3; User cria com custo mas não altera o teto (403); Manager altera o teto (200).
- Frontend publicado com coluna Custo/chamada, indicador e editor do teto.

### ⏳ Pendências (mantidas)
- Render `prmo-api` (Manual sync + repointar frontend), Supabase (billing "VTech"), branch padrão → `main`, integração VanguardIA, enforcement real de custo (depende da execução de IA), migração de schema quando o banco for persistente.

---

## 2026-08-10 (sessão 2) — RBAC do usuário comum e rebrand para PrMO

### 🎯 Objetivo
Definir a regra de acesso do usuário comum e renomear o projeto.

### ✅ Entregas
- **RBAC — usuário comum (`User`)**: acesso e visão **somente da Biblioteca de prompts**.
  - Frontend: menus e botões de cadastro dos demais módulos ocultos (`ctrl-only`); User cai direto na Biblioteca.
  - Backend: `POST /governance/*` restrito a Manager/Admin (User → 403).
- **Cadastro de prompt pelo colaborador**: botão "+ Novo prompt" liberado para o User, porém o registro entra **sempre como "Revisão pendente"** (o campo Controle é ocultado e o backend força o status). Homologação (Aprovado/Reprovado) segue exclusiva de Manager/Admin.
- **Novo login comum**: `user@vanguardamartech.com.br` / `user123` (perfil User, ativo).
- **Rebrand do projeto → PrMO — Prompt Management Office**: frontend (marca, título, login, rodapé), backend (`app_name`, descrição da API), `render.yaml` (`APP_NAME`), README, CI (marcador) e diagrama BPMN (SVG+PNG). Slug do repositório e URLs (Pages/Render) mantidos para não quebrar links.

### 🧪 Validações ao vivo
- User: `GET /governance/prompts` 200; `POST` prompt 201 com `control` forçado a "Revisão pendente"; `POST` incident 403.
- Manager/Admin: cadastram e homologam normalmente.
- Login `user@vanguardamartech.com.br` ativo (HTTP 200, role User).

### 🧭 Decisões
- Nome do produto passa a ser **PrMO**; contexto corporativo "Vanguarda Martech" mantido.
- Fluxo de homologação: colaborador envia (Revisão pendente) → Admin/Manager aprova ou reprova.

### ⏳ Pendências (mantidas)
- Supabase (billing "VTech"), branch padrão → `main`, integração VanguardIA, botão de aprovar/reprovar in-app, KPI "Clientes governados", migração de schema quando o banco for persistente.

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
