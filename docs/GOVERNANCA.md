# Modelo de Governança — VANGUARDIAN

> Papéis, fluxos e regras que garantem que o repositório de prompts e PI opere
> com qualidade, segurança e conformidade.

## 1. Papéis (RBAC)

| Papel | Responsabilidade | Permissões no repositório |
|-------|------------------|---------------------------|
| **Admin** (Diretoria de IA) | Define normas, aprova exceções | Merge, gestão de acessos |
| **Manager** (Líderes de área) | Homologa prompts, revisa PRs | Aprovar/mesclar PRs da sua área |
| **User** (Colaboradores) | Cria e propõe prompts | Abrir PRs, comentar |

O mesmo RBAC é aplicado na API (ver [`../backend/auth/`](../backend/auth/)).

### Regra de acesso na plataforma (app)

| Perfil | Menus visíveis | Ações |
|--------|----------------|-------|
| **User** (comum) | Somente **Biblioteca de prompts** | Apenas **visualizar** e copiar (sem cadastro) |
| **Manager / Admin** (controlador) | **Todos** os menus | Visualizar e **cadastrar** em todos os módulos |

No frontend, os menus e botões de cadastro são ocultados para o perfil User; no
backend, os endpoints de criação (`POST /governance/*`) exigem Manager/Admin
(HTTP 403 para User), garantindo a regra também no servidor.

## 2. Fluxo de contribuição de prompt

```
Autor cria (rascunho) ─▶ PR ─▶ Revisão (Manager) ─▶ Homologação ─▶ Merge ─▶ Índice atualizado
```

Detalhes operacionais em [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## 2.1 Teto de custo por chamada (governado pelo PrMO)

O PrMO define um **teto de custo por chamada** (valor + moeda) como política global,
editável **somente por Admin/Manager** (`PUT /governance/cost-policy`, auditado).

- Cada prompt registra seu **custo estimado por chamada** (`cost_per_call`).
- A Biblioteca **sinaliza** os prompts **acima do teto** vigente (badge de alerta).
- O painel expõe `custo` (teto, moeda, prompts acima/avaliados) via `/governance/overview`.
- Enforcement em tempo de execução depende da camada de execução de IA (VanguardIA);
  no PrMO a função é **governar, sinalizar e auditar** o teto.

## 3. Regras inegociáveis

1. Dados confidenciais **somente** em ferramentas homologadas.
2. Toda entrega externa passa por **revisão humana** registrada.
3. Todo prompt/automação novo deve ser **registrado** via PR (NIA-001 §4).
4. Ocorrências e incidentes são reportados **imediatamente**.

## 4. Comitê de IA

O Comitê de IA prioriza a evolução do ecossistema (briefs inteligentes, agentes de
performance, bases de conhecimento de marca, relatórios automatizados) e revisa a
stack homologada e as normas periodicamente.

## 5. Auditoria

Todas as operações sensíveis na API são auditadas (quem, quando, o quê, antes/depois)
— ver [`../backend/audit/`](../backend/audit/) e o modelo `AuditLog`. No repositório,
o `git log` cumpre o papel de trilha de auditoria dos ativos de PI.

## 6. Métricas de governança

- Adoção por área, ROI por hora investida, conformidade da stack.
- Cobertura de homologação (prompts homologados / prompts em uso).
- Incidentes abertos e tempo de resolução.

Ver o painel executivo no [`frontend`](../frontend/index.html) e os endpoints de
[`../backend/observability/`](../backend/observability/).
