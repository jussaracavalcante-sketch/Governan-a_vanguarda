# Regras de Negócio — PrMO (derivadas das normas corporativas)

Este documento amarra as **normas corporativas** ([Política](normas/POLITICA-IA.md),
[Manual por Departamento](normas/MANUAL-IA-DEPARTAMENTOS.md),
[NIA-001](normas/NIA-001-ENGENHARIA-DE-PROMPTS.md)) às **funcionalidades implementadas**
no PrMO (backend FastAPI + Biblioteca de prompts).

## 1. Padrão corporativo do prompt (NIA-001 §5–§9)
Cada prompt (`gov_prompts`) passou a carregar os metadados obrigatórios da norma:

| Campo | Origem na norma | Comportamento |
|-------|-----------------|---------------|
| `code` | §7 Nomenclatura | Gerado automático no formato `PROMPT-ÁREA-NNN` (sigla da macroárea + sequência) |
| `version` | §8 Versionamento | Default `1.0` |
| `ptype` | §6 Classificação | `A` Operacional · `B` Analítico · `C` Estratégico · `D` Automação · `E` Criativo (auto-classificado por palavras-chave, ajustável) |
| `tool` | §5 Ferramenta | Ferramenta utilizada (validada contra o stack homologado) |
| `author` | §9 Autor | Preenchido com o usuário autor no cadastro |
| `data_class` | Política §7 | `Público` · `Uso interno` · `Confidencial` · `Restrito` |

As siglas de área seguem o [Manual por Departamento](normas/MANUAL-IA-DEPARTAMENTOS.md):
CRI, ATD, PLA, MID, SOC, CML, INB, RH, FIN, ADM, DEV, CEO, PMO, DAT, KNW.

## 2. Regras aplicadas (motor de regras)
Endpoint consultável: **`GET /governance/rules`**. Aplicadas no ciclo de vida do prompt:

| ID | Base normativa | Momento | Regra |
|----|----------------|---------|-------|
| **R1** | NIA-001 §13 / Política §6 | Cadastro | Bloqueia prompt com **credenciais, segredos ou PII** (senha, token, `api_key`, CPF, cartão, termos de fraude/burla). |
| **R2** | Política §4 | Homologação | Só **aprova** prompt cuja **ferramenta** esteja **Homologada** no stack. |
| **R3** | NIA-001 §5/§12 | Homologação | **Aprovação** exige metadados mínimos: código, objetivo/descrição e conteúdo. |
| **R4** | Política §7 | Cadastro/Homologação | Dado **Restrito** não pode apontar para **repositório público externo** (github/gitlab/drive…). |

- Violações retornam **HTTP 422** com `{"regras": [...]}` e são registradas na **trilha de auditoria**.
- **Reprovar** um prompt é sempre permitido (não sujeito às regras de aprovação).
- Colaborador (`User`) cadastra sempre como **Revisão pendente**; homologação é de Manager/Admin (RBAC).

## 3. Fluxo de homologação (NIA-001 §10)
Criação → Teste → Validação → **Homologação (R1–R4)** → Publicação → Monitoramento → Melhoria contínua.
No PrMO: cadastro (`POST /governance/prompts`) → triagem na Biblioteca → `POST /governance/prompts/{id}/homologar` (`Aprovado`/`Reprovado`).

## 4. Ferramentas homologadas (Política §4)
O stack (`gov_stack_tools`) mantém o status `Homologada | Em análise | Restrita | Reprovada`.
A regra **R2** cruza a `tool` do prompt com as ferramentas `Homologada`.

## 5. Teto de custo (governança do PrMO)
Política global de **teto de custo por chamada** (`gov_cost_policy`) + custo por prompt;
prompts acima do teto são sinalizados na Biblioteca e no painel.

## 6. Integração VanguardIA
Conector `vanguardia` (padrão dos demais: `rd_station`, `iclips`, `vjob`), configurável por
`base_url` + `api_key` (painel admin ou variáveis `VANGUARDIA_BASE_URL` / `VANGUARDIA_API_KEY`).
- `POST /integrations/vanguardia/test` — testa conexão.
- `POST /integrations/vanguardia/sync` — importa o catálogo de agentes/prompts homologados
  do VanguardIA para a Biblioteca como candidatos (`Revisão pendente`), já no padrão NIA-001
  (código, tipo, ferramenta, autor `VanguardIA`), preservando a governança.
- Contrato esperado (ajustável): `GET {base_url}/api/v1/health` e `GET {base_url}/api/v1/agents`.

> Enquanto o endpoint do VanguardIA não é publicado, a integração fica **desabilitada** e o
> `test` responde "não configurado" — basta preencher `base_url`/`api_key` e habilitar.

## 7. Rastreabilidade
Toda criação, homologação, alteração de política e violação de regra é registrada em
`audit_logs` (`GET /governance/audit`), atendendo à auditoria prevista na Política §12 e NIA-001 §14.
