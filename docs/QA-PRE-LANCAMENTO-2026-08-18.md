# QA de pré-lançamento — 2026-08-18

**Projeto:** PrMO — Prompt Management Office · Vanguarda Martech
**Objetivo:** validar usabilidade e funcionalidades para liberar aos usuários.
**Branch:** `claude/prompts-repo-infrastructure-08dmf1`

## Veredito
**✅ Pronto para lançamento.** Bateria automatizada: **backend 58/58** e **UI 21/21** (100%). Fumaça em produção OK. Dois problemas encontrados e corrigidos durante o QA (abaixo).

---

## 1. Testes funcionais de backend (TestClient, 58/58)
Cobertura por área:
- **Autenticação:** login OK; senha errada → 401; autocadastro restrito ao domínio (@gmail → 422); senha curta → 422; cadastro corporativo → 201; duplicado → 400; `/auth/me`.
- **SSO Google (degradado):** `/auth/google/config` → `enabled:false`; `/auth/google/login` sem credenciais → 503.
- **Governança:** overview, regras R1–R4, biblioteca (prompts curados), registros, auditoria, observabilidade.
- **Regras de negócio:** R1 bloqueia segredo/PII (422); R2 barra aprovação com ferramenta não homologada (422).
- **RBAC:** usuário comum recebe **403** em criar curso, ver board de sugestões, fila de suporte, painel de obrigatórios, criar cliente e alterar teto de custo.
- **Suporte / Ativos / Sugestões:** criação aberta (201), filas do gestor, "minhas", triagem/atendimento/análise.
- **Base de conhecimento:** 6 cursos, 3 categorias, aulas com conteúdo, gabarito não exposto, quiz reprova/aprova, certificado só após aprovação, `/academy/me` (nível/pontos), ranking, painel do gestor, upload 503/403.
- **Cadastros do gestor:** cliente, stack, skill, iniciativa, incidente; teto de custo GET/PUT.

## 2. Testes de usabilidade (Playwright, 21/21)
Duas jornadas completas, sem erros de JS:
- **Gestor:** login → dashboard; navegação por todas as abas; Academy (catálogo, selo obrigatório, painel do gestor, ranking; abrir curso → ler aula → quiz → **conclusão → certificado com código e botão "Baixar PNG"**).
- **Usuário comum:** entra e **não** vê abas de gestor; Academy acessível; painel do gestor **oculto**; card "Meu progresso" e banner de lembrete visíveis; tela de cadastro; botão SSO oculto quando não configurado.

## 3. Fumaça em produção
- Backend `prmo-api` responde (login admin OK; `/academy/me` 200); rotas protegidas retornam 401/403 sem token; `/auth/google/config` → `enabled:false`.
- Frontend (Vercel e GitHub Pages) HTTP 200 com a aba Base de conhecimento e o botão institucional.
- *Observação:* o backend está no plano gratuito do Render (cold start ~50s); a primeira requisição após inatividade pode demorar — a UI já mostra aviso de carregamento.

## 4. Correções feitas durante o QA
1. **Bug 500 na análise de ativos** — `PUT /governance/asset-requests/{id}` lia `item.note`, ausente no schema `AssetReviewIn` → `AttributeError` → HTTP 500 em toda aprovação/reprovação. **Corrigido** (campo `note` opcional). Revalidado: 200 com e sem nota.
2. **Curso duplicado em produção** — havia um 7º curso de teste ("Engenharia de prompts", 0 aulas) criado durante experimentos. **Removido**; produção com exatamente 6 cursos.

## 5. Pendências (não bloqueiam o lançamento)
- **Upload de arquivos** (Supabase Storage): definir `SUPABASE_URL` e `SUPABASE_SERVICE_KEY` no Render. Sem isso, materiais por link/incorporado funcionam normalmente.
- **SSO Google**: provisionar OAuth Client e definir `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` no Render (guia em `docs/SSO-GOOGLE.md`). Sem isso, login por e-mail/senha (restrito ao domínio) funciona.
- **Vercel**: Production Branch → `claude/...` para deploy automático; **revogar** o token usado nas sincronizações.
- Recomendado antes de abrir a usuários reais: **trocar a senha do admin** semeado (`admin@vanguardian.com`).

## 6. Como reproduzir os testes
- Backend: `DATABASE_URL="sqlite:///.../qa.db" python - < scratchpad/qa_backend.py` (TestClient; base efêmera).
- UI: `python scratchpad/qa_ui.py` (Playwright headless, API mockada sobre `file://`).
