---
id: ATD-001
titulo: Briefing Estratégico
area: Atendimento
categoria: Planejamento
versao: 1.1.0
status: homologado
modelo_alvo: [GPT-4, Claude 3]
classificacao_dados: confidencial
autor: Equipe de Atendimento
homologado_por: Diretoria de IA
data_criacao: 2026-02-01
data_revisao: 2026-06-20
tags: [briefing, planejamento, estrategia]
usos: 86
---

# Briefing Estratégico

## 🎯 Objetivo
Estruturar um briefing estratégico completo a partir de notas brutas de reunião,
padronizando o entendimento entre atendimento, criação e mídia.

## 👤 Público / caso de uso
Atendimento, ao converter o kickoff ou a demanda do cliente em um briefing acionável.

## 🧩 Prompt

```text
Você é planejador de atendimento da Vanguarda Martech.
Contexto: cliente {{cliente}}, demanda {{tipo_de_demanda}}.
Tarefa: transformar as notas abaixo em um briefing estratégico estruturado.
Notas: {{notas_da_reuniao}}
Estruture o briefing com as seções:
1. Objetivo de negócio
2. Público-alvo
3. Mensagem-chave e tom
4. Entregáveis e formatos
5. Canais e cronograma
6. KPIs e metas
7. Riscos e restrições (inclusive brand safety e LGPD)
8. Pendências / perguntas ao cliente
Restrições:
- Sinalize explicitamente qualquer informação ausente como "A CONFIRMAR".
- Não invente dados; use apenas o que consta nas notas.
Formato de saída: markdown com títulos por seção.
```

## 🔤 Variáveis
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{{cliente}}` | Conta alvo | Conta Nexo |
| `{{tipo_de_demanda}}` | Natureza do trabalho | Campanha de lançamento |
| `{{notas_da_reuniao}}` | Texto bruto do kickoff | ... |

## ✅ Exemplo de saída esperada
```
# Briefing — Conta Nexo
## 1. Objetivo de negócio
Aumentar em 20% os leads qualificados no Q3...
```

## ⚠️ Riscos e cuidados
- Dados **confidenciais**: usar exclusivamente em ferramentas homologadas.
- Não compartilhar o briefing fora da conta responsável.

## 📝 Histórico de versões
| Versão | Data | Autor | Mudança |
|--------|------|-------|---------|
| 1.0.0 | 2026-02-01 | Equipe de Atendimento | Criação e homologação |
| 1.1.0 | 2026-06-20 | Equipe de Atendimento | Inclusão de seções de KPI e riscos |
