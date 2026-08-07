# 📚 Biblioteca Corporativa de Prompts — VANGUARDIAN

> Repositório versionado, auditável e governado de **prompts** e **propriedade intelectual** de IA da **Vanguarda Martech**.

Esta pasta é a **fonte da verdade** dos prompts institucionais. Cada prompt é um
ativo de propriedade intelectual da Vanguarda Martech, homologado segundo a
**Norma Corporativa NIA-001** ([`../docs/NIA-001-norma-prompts.md`](../docs/NIA-001-norma-prompts.md))
e protegido pela política de PI ([`../docs/PROPRIEDADE-INTELECTUAL.md`](../docs/PROPRIEDADE-INTELECTUAL.md)).

---

## 🗂️ Taxonomia

Os prompts são organizados por **área de negócio**. Cada arquivo `.md` é um prompt
único, versionado, com metadados no cabeçalho (front matter).

```
prompts/
├── README.md                 # este catálogo
├── _template/
│   └── PROMPT_TEMPLATE.md     # modelo padrão NIA-001 (copie para criar um novo)
├── criacao/                  # Criação, redação, brand voice, conteúdo
├── atendimento/              # Atendimento, briefings, relacionamento
├── midia/                    # Mídia paga, performance, análise de campanhas
├── comercial/                # Comercial, propostas, prospecção
├── dados-bi/                 # Dados, BI, relatórios, insights
└── governanca/               # Governança, compliance, revisão, auditoria
```

> **Regra de ouro (NIA-001 §4):** todo prompt novo ou alterado **deve** ser
> registrado aqui via Pull Request antes de ser usado em produção.

---

## 🏷️ Nomenclatura de arquivos

```
<AREA>-<NNN>-<slug-curto>.md
```

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `AREA` | Sigla da área (CRI, ATD, MID, COM, DAD, GOV) | `CRI` |
| `NNN` | Número sequencial de 3 dígitos | `001` |
| `slug-curto` | Descrição em kebab-case | `legenda-brand-voice` |

Exemplo: `criacao/CRI-001-legenda-brand-voice.md`

---

## 🔖 Metadados obrigatórios (front matter)

Todo prompt inicia com um bloco YAML:

```yaml
---
id: CRI-001
titulo: Legenda com Brand Voice
area: Criação
categoria: Social Media
versao: 1.2.0
status: homologado          # rascunho | em-revisao | homologado | descontinuado
modelo_alvo: [GPT-4, Claude 3]
classificacao_dados: uso-interno   # publico | uso-interno | confidencial | restrito
autor: Nome do Autor
homologado_por: Nome do Aprovador
data_criacao: 2026-01-15
data_revisao: 2026-06-30
tags: [social, caption, tom-de-voz]
usos: 143
---
```

Consulte a especificação completa em [`../docs/NIA-001-norma-prompts.md`](../docs/NIA-001-norma-prompts.md).

---

## ➕ Como adicionar um prompt

1. Copie [`_template/PROMPT_TEMPLATE.md`](_template/PROMPT_TEMPLATE.md) para a pasta da área.
2. Renomeie seguindo a convenção de nomenclatura.
3. Preencha o front matter e todas as seções da estrutura padrão.
4. Defina `status: rascunho`.
5. Abra um **Pull Request** — a homologação ocorre na revisão (ver
   [`../CONTRIBUTING.md`](../CONTRIBUTING.md)).
6. Após aprovação, o revisor altera para `status: homologado` e registra o aprovador.

---

## 🔄 Versionamento (SemVer)

| Mudança | Incremento | Exemplo |
|---------|-----------|---------|
| Correção mínima (typo, ajuste de exemplo) | patch | `1.0.0 → 1.0.1` |
| Melhoria que mantém compatibilidade | minor | `1.0.1 → 1.1.0` |
| Reescrita / mudança de objetivo | major | `1.1.0 → 2.0.0` |

O histórico completo vive no `git log` do arquivo — cada alteração é rastreável
(quem, quando, o quê), garantindo a **cadeia de custódia** da propriedade intelectual.

---

## 📇 Índice de prompts homologados

| ID | Título | Área | Versão | Status |
|----|--------|------|--------|--------|
| [CRI-001](criacao/CRI-001-legenda-brand-voice.md) | Legenda com Brand Voice | Criação | 1.2.0 | ✅ homologado |
| [ATD-001](atendimento/ATD-001-briefing-estrategico.md) | Briefing Estratégico | Atendimento | 1.1.0 | ✅ homologado |
| [MID-001](midia/MID-001-insights-performance.md) | Insights de Performance | Mídia | 1.0.0 | ✅ homologado |
| [GOV-001](governanca/GOV-001-revisao-brand-safety.md) | Revisão de Brand Safety | Governança | 1.0.0 | ✅ homologado |

> Mantenha este índice atualizado a cada PR que adicione ou promova um prompt.
