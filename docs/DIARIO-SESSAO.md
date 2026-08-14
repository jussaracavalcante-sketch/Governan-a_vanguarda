# Diário de Sessão — PrMO (Prompt Management Office)

Registro cronológico do trabalho por sessão. Entrada mais recente no topo.

---

## 2026-08-14 (sessão 11) — Base de conhecimento (Udemy + gamificação Hacker Rangers)

### 🎯 Objetivo
Criar uma aba de capacitação (estilo Udemy) para treinamentos de IA, Compliance e Segurança da Informação, com progresso do aluno — e, na sequência, a camada estilo **Hacker Rangers**: cursos **obrigatórios com prazo**, **quiz com nota**, **certificado** ao concluir e **ranking** por pontos.

### ✅ Entregas — Engajamento (níveis, painel e lembretes)
- **Níveis por pontuação**: Aprendiz → Bronze (100) → Prata (250) → Ouro (500) → Platina (1000); card "Meu progresso" com barra até o próximo nível.
- **Medalhas**: primeiro curso, maratonista (3+), nota máxima (quiz 100%), "em dia" (todos os obrigatórios), e trilha completa por categoria (IA/Compliance/Segurança).
- **Painel do gestor** (`GET /academy/mandatory-status`): por treinamento obrigatório, % de conclusão da equipe e lista de pendentes (com flag "em andamento").
- **Lembretes automáticos de prazo** (`GET /academy/me`): banner exibido ao abrir a aba com os obrigatórios pendentes e status do prazo (vence em Nd / atrasado). In-app; envio por e-mail requer SMTP (pode ser plugado no mesmo endpoint).
- Ranking passou a exibir nível + ícone. Validações: TestClient (níveis, medalhas, painel, RBAC 403) e Playwright **13/13** (v3), sem regressão em v1 (14/14) e v2 (13/13).

### ✅ Entregas — Gamificação (Hacker Rangers)
- **Obrigatórios com prazo**: `Course.mandatory` + `due_date`; cards com selo "Obrigatório" e chip de prazo (no prazo / vence em Nd / atrasado). Seed marca *Política de IA* (30d) e *Segurança da Informação* (45d).
- **Quiz com nota**: `Course.quiz` (JSON com gabarito, nunca exposto no GET) + `pass_score`. `POST /courses/{id}/quiz` corrige e grava `quiz_score`/`quiz_passed`. O quiz só libera após as aulas; a conclusão exige aulas **e** aprovação na nota mínima.
- **Certificado**: emitido ao concluir (`certificate_code` + `completed_at`); `GET /courses/{id}/certificate`. UI abre um certificado imprimível (window.print / salvar PDF) com nome, curso, nota e código de validação.
- **Ranking**: `GET /courses-ranking` (pontos por cursos concluídos) + painel "🏆 Ranking de aprendizado" na aba.
- Migração Supabase: novas colunas em `gov_courses`/`gov_course_progress` (RLS mantida); tabelas re-semeadas com o conteúdo enriquecido.
- Validações: TestClient (gating quiz→conclusão→certificado→ranking, 422/403) e Playwright **13/13 PASS** (v2) + **14/14** (base, sem regressão).

### 🎯 Objetivo (base — Udemy)
Criar uma aba de capacitação (estilo Udemy) para treinamentos e cursos de IA, Compliance e Segurança da Informação, com acompanhamento de progresso do aluno.

### ✅ Entregas
- **Backend**: modelos `Course` (`gov_courses`) e `CourseProgress` (`gov_course_progress`). Endpoints `/governance/courses` (catálogo com filtros de categoria/nível/busca; `/mine`; `/{id}`; POST/PUT restritos a gestor com regra R1 e validação de categoria) e `POST /courses/{id}/progress` (marca/desmarca aula, recalcula % e status Concluído).
- **Seed**: 6 cursos iniciais (2 por trilha) com aulas — ex.: *Fundamentos de IA Generativa*, *Engenharia de Prompts (NIA-001)*, *Política de IA e uso responsável*, *LGPD na prática*, *Segurança da Informação essencial*, *Uso seguro de IA e proteção de segredos*.
- **Frontend**: aba "🎓 Base de conhecimento" com chips de categoria (IA/Compliance/Seg. Informação), busca, filtro de nível, cards com capa/nível/duração e **barra de progresso**, modal do curso com aulas marcáveis + links "Assistir", trilho **"Continue de onde parou"** e formulário de **novo curso** (gestor). O catálogo carrega ao abrir a aba (robusto a falhas do dashboard).
- **db/supabase_schema.sql**: DDL de `gov_courses` e `gov_course_progress`.

### 🧪 Validações
- Backend (TestClient/SQLite): catálogo com 6 cursos e 3 categorias; conclusão de todas as aulas → 100%/"Concluído"; desmarcar reduz %; `/mine`; índice inválido → 422; categoria inválida → 422; RBAC 403 (usuário comum não cria curso) e leitura/progresso liberados.
- Supabase: `gov_courses` e `gov_course_progress` criadas com **RLS** (seed roda no boot do backend).
- UI (Playwright/`file://` com mock): **14/14 PASS** (aba ativa; catálogo; filtro por categoria; busca; modal; aulas; link "Assistir"; conclusão; badge CONCLUÍDO; rail; novo curso; sem erros JS).

### ⏳ Pendências
- Sincronizar a produção na Vercel com esta mudança (o GitHub Pages já reflete).

## 2026-08-13 (sessão 10) — Suporte técnico, solicitação de ativos e "Sugestões e melhorias"

### 🎯 Objetivo
Abrir canais dos colaboradores (suporte/embaixadores de IA), permitir solicitação de novos ativos digitais de IA e reorganizar a Biblioteca separando os candidatos do mapeamento em um menu próprio.

### ✅ Entregas
- **Suporte técnico** (`gov_support`): reporte de uso indevido da IA, solicitações e canal dos embaixadores. Endpoints `/governance/support` (POST aberto, GET gestor, `/mine`, PUT triagem). Aba "🛟 Suporte" + modal.
- **Solicitar ativo digital** (`gov_asset_requests`): campos nome completo, funcionalidades, URL e repositório (público/institucional). Endpoints `/governance/asset-requests` (POST aberto com regra R1, GET gestor, `/mine`, PUT análise Aprovado/Reprovado/Pendente) + fila de análise.
- **Sugestões e melhorias** (`gov_suggestions`): novo modelo/endpoints `/governance/suggestions` (POST aberto R1, GET gestor com filtros, `/mine`, PUT triagem Nova|Em análise|Aceita|Recusada). Aba "💡 Sugestões e melhorias" com envio, "minhas sugestões" e quadro de triagem (gestor).
- **Limpeza da Biblioteca**: os 52 candidatos do mapeamento KNOW saíram da Biblioteca e passaram a alimentar `gov_suggestions` (`source="Mapeamento"`). A Biblioteca mantém somente os prompts curados (`PROMPT-*`). Seed renomeado para `seed_suggestions_from_knowledge`.
- **Deploy**: dois commits na branch; GitHub Pages redeployado; backend `prmo-api` (Render) redeployado.
- **Sincronização da produção na Vercel** (via CLI, `vercel deploy --prod`) — produção atualizada em **https://prmo-frontend.vercel.app** com o novo menu.
- **Correção `vercel.json`**: o rewrite apontava para `/frontend/index.html`, que o `cleanUrls` normalizava para `/frontend`, deixando a raiz `/` em 404. Rewrite ajustado para `/frontend` → raiz volta a servir o app (HTTP 200). `.gitignore` passa a ignorar `.vercel`/`.env.local`.

### 🧪 Validações
- Backend local (Postgres): Biblioteca = 3 prompts curados; quadro de sugestões = 52 (mapeamento); envio de colaborador → 201; RBAC 403 para usuário comum no quadro; triagem "Aceita"; regra R1 bloqueia segredo/PII (422).
- Migração Supabase: `gov_suggestions` criada com RLS; movimentação `INSERT … SELECT … WHERE title LIKE '%[KNOW-%'` + `DELETE` → biblioteca=3, sugestoes=52.
- UI (Playwright/`file://` com mock): **10/10 PASS** (Biblioteca sem KNOW; menu Sugestões ativo; formulário; quadro; modal de triagem; salvar; usuário vê envio, não vê o quadro).
- Produção pós-deploy: `prmo-frontend.vercel.app` e GitHub Pages em **HTTP 200** com "Sugestões e melhorias" e apontando para `prmo-api`; backend `/governance/suggestions` respondendo (401 = rota exige auth).

### 🔐 Segurança
- Token da Vercel usado de forma pontual (arquivo temporário `600`, sem log/commit) e **removido com `shred`** ao final, junto de `.vercel`/`.env.local`. Recomendada a revogação do token em vercel.com/account/tokens.

### ⏳ Pendências
- **Revogar o token da Vercel** exposto no chat.
- Definir a Production Branch da Vercel para `claude/prompts-repo-infrastructure-08dmf1` (ou promover a branch a padrão do repo) para deploy automático a cada push — hoje a sincronização de produção é manual via CLI.

## 2026-08-13 (sessão 9) — Nova infra: frontend na Vercel

### 🎯 Objetivo
Publicar o frontend do PrMO como um **novo serviço/infra na Vercel**, reusando a API existente (`prmo-api`).

### ✅ Entregas
- **Repositório preparado para a Vercel**: `vercel.json` (reescreve `/` → `frontend/index.html`), `.vercelignore` (exclui backend/docs/db/workflows) e guia `docs/VERCEL.md`.
- **Deploy em produção via CLI** (`vercel deploy --prod --scope vanguardaos-projetos`):
  - Projeto **`prmo-frontend`** (equipe `vanguardaos-projetos`).
  - URL de produção: **https://prmo-frontend.vercel.app** (alias `prmo-frontend-vanguardaos-projetos.vercel.app`).
  - Publica o app atual (estático, sem build), apontando para `https://prmo-api.onrender.com`.
- **Deployment Protection desligada** (via API `ssoProtection: null`) para acesso público.
- Token de deploy usado de forma pontual (env/arquivo temporário 600), sem log/commit, e removido do scratchpad ao final.

### 🧪 Validações
- `https://prmo-frontend.vercel.app` → **HTTP 200**, 57 KB; título correto; `const API` = `prmo-api`; features presentes (ranking de setores, exportação, cadastro corporativo, barra de usuário, navegação).

### 🧭 Decisões / notas
- Sem integração VanguardIA por ora (a pedido) — os serviços VanguardIA no Render (`vanguarda-ia-api`=Bíblia da Marca, `-orchestrator`=`/v1/generate`, `-rag`=`/ask`) não expõem catálogo de prompts; integração reavaliada quando/for desejada.
- Frontend agora em **duas infra**: GitHub Pages + Vercel, ambos consumindo o mesmo `prmo-api`/Supabase.

### ⏳ Pendências
- **Revogar o token da Vercel** em vercel.com/account/tokens.
- Opcional: domínio customizado (ex.: `prmo.vanguardamartech.com.br`); conectar o repo ao projeto Vercel para deploy automático no push.

---

## 2026-08-12 (sessão 8) — Autocadastro, UX, edição de prompt, ranking de setores e exportação

### 🎯 Objetivo
Validar/ativar as funcionalidades existentes e evoluir a experiência: acesso, navegação, edição de prompts, ranking e exportação de relatórios.

### ✅ Entregas
- **Validação e ativação de tudo que existe**: varredura de todos os endpoints ao vivo (prmo-api → Supabase); corrigidos os 2 quebrados: `/admin/metrics` (faltavam métricas de runtime no schema) e `/admin/integrations` (registro `vanguardia` com `last_sync_status` nulo).
- **Autocadastro restrito ao domínio**: `POST /auth/signup` (público) aceita só `@vanguardamartech.com.br`, cria usuário **User** e autentica. Tela de login com alternância **Entrar / Criar conta corporativa** (validação de domínio no cliente).
- **Edição de prompt**: `PUT /governance/prompts/{id}` (manager) com regras R1/R4 e auditoria. Biblioteca: título clicável + ação **Ver/Editar** abrem modal (editável p/ controlador, leitura p/ usuário comum).
- **Ranking de setores por ativos digitais**: `/overview` → `ranking_setores` (macroáreas por nº de ativos da base de conhecimento, com `itens`). Card no dashboard com pódio (🥇🥈🥉), barra de participação e **linhas clicáveis que expandem** os ativos do setor (código KNOW · tipo · tarefa).
- **Exportação do relatório**: menu "Exportar ▾" com **PDF** (A4 paginado), **XLSX** (abas KPIs / Ranking / Biblioteca), **PNG** e **JPEG**. Libs (SheetJS, html2canvas, jsPDF) carregadas sob demanda; overlay de progresso; arquivos `PrMO-relatorio-AAAAMMDD.<ext>`.
- **UX**:
  - **Cold start** do Render mitigado: overlay "Carregando informações…" com aviso + ping de aquecimento a `/health/live` na tela de login.
  - **Hover flutuante** em cards, botões, itens de menu e ações de tabela (respeita `prefers-reduced-motion`).
  - **Navegação**: botão **‹ Voltar** no cabeçalho da página (histórico) + logo **PrMO** volta à tela inicial.
  - **Sidebar** reorganizada: nome do usuário + **Sair** no topo; menus abaixo; observabilidade no rodapé.
  - **Favicon** de biblioteca (📚). Modais roláveis (botão salvar não sai da viewport).

### 🧪 Validações
- Backend em Postgres/Supabase (TestClient + ao vivo): signup (domínio/RBAC), PUT edição (R1/R4/RBAC/404), `ranking_setores` com 52 itens, `/admin/metrics` e `/admin/integrations` 200.
- UI no navegador (Playwright, API mockada): 30/30 nos fluxos base; navegação/Sair/edição 10/10; ranking expansível + 4 exportações 8/8 (downloads com extensão correta).

### ⏳ Pendências (do usuário)
- **VanguardIA**: sem credenciais cadastradas no projeto — falta `base_url` + token para ligar o `sync`.
- **SSO Google Workspace**: implementável com OAuth Client ID + Secret (login com trava `hd=vanguardamartech.com.br`).
- **Cold start**: pinger externo (UptimeRobot/cron-job.org) ou upgrade do plano Render. Arquivar o serviço antigo `vanguardian-api-omg6`. Branch padrão → `main`.

---

## 2026-08-11 (sessão 7) — Normas corporativas: padrão NIA-001, regras de negócio e integração VanguardIA

### 🎯 Objetivo
Analisar os três normativos corporativos (Política de IA, Manual por Departamento, NIA-001) e implementar no PrMO o que é aplicável, além de atuar na integração do VanguardIA.

### ✅ Entregas
- **Padrão NIA-001 no prompt** (`gov_prompts`): novos campos `code` (nomenclatura `PROMPT-ÁREA-NNN`, auto-gerado), `version`, `ptype` (A–E, auto-classificado), `tool`, `author`, `data_class`. Código único por área (55/55).
- **Motor de regras de negócio** (`GET /governance/rules`), aplicado no ciclo do prompt:
  - **R1** (NIA-001 §13 / Política §6) — bloqueia cadastro com credenciais/segredos/PII (senha, token, CPF, cartão, fraude).
  - **R2** (Política §4) — só homologa prompt com **ferramenta homologada**.
  - **R3** (NIA-001 §5/§12) — aprovação exige código + objetivo + conteúdo.
  - **R4** (Política §7) — dado **Restrito** não pode ter repositório público externo.
  - Violações → HTTP 422 `{regras:[…]}` + trilha de auditoria. Reprovar é sempre permitido.
- **Integração VanguardIA**: conector `integrations/vanguardia/` (padrão rd_station/iclips/vjob), factory, settings `VANGUARDIA_*`, seed do `integration_config`. `test`/`sync` prontos; `sync` importa agentes/prompts homologados do VanguardIA para a Biblioteca como candidatos no padrão NIA-001.
- **Frontend**: formulário de prompt com Tipo/Ferramenta/Classificação; Biblioteca exibe código·versão·tipo; mensagens das regras (422) exibidas ao usuário.
- **Docs**: normas versionadas em `docs/normas/` (Política, Manual, NIA-001) + `docs/REGRAS-DE-NEGOCIO.md` (normas → sistema) + referência no `GOVERNANCA.md`.
- **Supabase**: `ALTER` de `gov_prompts` (6 colunas + índice), recarga dos 55 prompts com os campos NIA-001 (RLS reativado), integração `vanguardia` inserida.

### 🧪 Validações
- Backend em Postgres (TestClient): regras R1–R4 (bloqueios e caminho válido), 4 integrações, 55 prompts com 55 códigos únicos, `/overview` real (93 colaboradores).
- Supabase: 55 prompts com código único, RLS bloqueando anon, `integration_configs` com VanguardIA.

### ⚠️ Nota de acesso
- Não foi possível anexar o repo `VanguardaHub/vanguardIA` nesta sessão (bloqueio de owner cruzado). O conector ficou **configurável** por `base_url`/token, pronto para apontar ao endpoint real quando publicado.

### 🔧 Adendo — validação e ativação das funcionalidades existentes
- Varredura de **todos os endpoints** ao vivo (prmo-api → Supabase): 33 rotas OK; 2 quebradas corrigidas:
  - `/admin/metrics` (500) — `SystemMetricsResponse` exigia `active_connections`/`total_requests`/`error_rate`/`avg_response_time_ms`, ausentes no service. Adicionados. ✅
  - `/admin/integrations` (500) — registro `vanguardia` (inserido via SQL) com `last_sync_status` nulo. Schema tolerante + `server_default='pending'` no modelo + `UPDATE`/`ALTER DEFAULT` no Supabase. ✅
- Revalidado ao vivo após redeploy: ambos **200**; núcleo (overview/rules/prompts/integrations) 200.

---

## 2026-08-11 (sessão 6) — Migração para o Supabase com validação do backend em Postgres

### 🎯 Objetivo
Migrar o projeto para o **Supabase/PostgreSQL** validando o backend (não só rodar em SQLite).

### ✅ Entregas
- **Projeto Supabase provisionado**: `prmo-governanca` (ref `ubixfcoigwpjdrioymdq`, região `sa-east-1`, Postgres 17), free tier (US$ 0/mês).
- **Validação real do backend em Postgres**: subi um Postgres local, rodei o FastAPI contra ele (`create_all` + todos os seeds) e exercitei os endpoints via `TestClient` (login admin/usuário, RBAC, `/overview` com números reais, `/prompts`, `/registry`).
- **Bug de portabilidade corrigido**: `gov_registry.code` era `VARCHAR(60)`, mas rótulos de `Indicador` do diagnóstico chegam a 62 chars. SQLite ignora tamanho de `VARCHAR`; o Postgres rejeitava (`StringDataRightTruncation`) e abortava todo o seed de governança. Ampliado para `VARCHAR(255)`.
- **Schema aplicado no Supabase** (migração `prmo_initial_schema`): 18 tabelas, 4 enums, PKs `IDENTITY`, índices e FKs — idênticos ao `Base.metadata.create_all`.
- **Dados migrados para o Supabase** (via Data API/HTTPS, a partir do seed anonimizado): `gov_registry` 258, `gov_prompts` 55 (52 candidatos + 3 curados), `users` 5, e demais tabelas de governança. Sequências `IDENTITY` reajustadas (`prmo_reset_identity_and_enable_rls`).
- **Segurança (RLS)**: RLS ativado em todas as tabelas do schema `public`, sem policies (deny-by-default). A Data API (`anon`/`publishable`) fica bloqueada; o backend conecta como papel `postgres` e ignora RLS. Advisor: só `INFO rls_enabled_no_policy` (estado pretendido).
- **Robustez do engine**: `pool_pre_ping` + `pool_recycle=1800` para conexões atrás do pooler (`backend/database.py`).
- **Config de deploy**: `render.yaml` com `DATABASE_URL: sync:false` (senha nunca no repo público); `docs/SUPABASE.md` reescrito com dados reais do projeto e passo a passo; DDL versionado em `db/supabase_schema.sql`.

### 🧪 Validações
- Seed em Postgres: 258 registros (asset 93, diagnostic 45, knowledge 52, opportunity 8, plan30 27, risk 33), 55 prompts, 4 clientes, 5 usuários — **sem falhas**.
- `/overview` em Postgres: 93 colaboradores, 33 riscos (3 críticos/25 altos), ChatGPT 81 usos — idêntico ao esperado.
- Supabase: contagens conferidas por SQL; RLS confirmado (anon recebe `[]`).

### 🧭 Decisões
- Acesso ao banco é **mediado pelo backend** (JWT + RBAC); nenhum cliente fala direto com o Supabase → RLS deny-by-default é a postura correta.
- Sandbox não tem egress TCP para o Postgres do Supabase; por isso a validação do backend foi feita em Postgres **local** e o carregamento no Supabase via **Data API (HTTPS)** + MCP.

### ⚠️ Ponto de atenção
- `/governance/overview` responde 200 para usuário comum (RBAC do dashboard hoje só no frontend). Pré-existente, não é da migração — avaliar restringir no backend.

### ✅ Adendo — virada de chave concluída (mesmo dia)
- Usuário definiu `DATABASE_URL` (Session pooler) no serviço **`prmo-api`** e redeployou.
- **Validação ao vivo, ponta a ponta**: inseri um registro-sentinela direto no Supabase → apareceu na API do `prmo-api` (leitura OK); criei um prompt pela API → gravou no Supabase (escrita OK); registros de teste removidos. Persistência real confirmada (fim do SQLite efêmero).
- **Frontend repontado** de `vanguardian-api-omg6` → `https://prmo-api.onrender.com` (commit `de1fc26`); **GitHub Pages** republicado e confirmado servindo a nova URL.

### ⏳ Pendências (do usuário, opcionais)
- Arquivar/desativar o serviço antigo `vanguardian-api-omg6` no Render (ocioso).
- Trocar a branch padrão do repo para `main`.
- Integração VanguardIA e filtro por status/tipo na Biblioteca.

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
