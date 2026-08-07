---
id: MID-001
titulo: Insights de Performance
area: Mídia
categoria: Análise de Campanhas
versao: 1.0.0
status: homologado
modelo_alvo: [GPT-4, Claude 3]
classificacao_dados: confidencial
autor: Equipe de Mídia
homologado_por: Diretoria de IA
data_criacao: 2026-03-05
data_revisao: 2026-06-15
tags: [midia, performance, analytics, relatorio]
usos: 48
---

# Insights de Performance

## 🎯 Objetivo
Transformar dados brutos de campanhas em insights acionáveis e recomendações de
otimização, com linguagem executiva.

## 👤 Público / caso de uso
Analistas de Mídia, na produção de relatórios quinzenais/mensais de performance.

## 🧩 Prompt

```text
Você é analista sênior de mídia de performance da Vanguarda Martech.
Contexto: cliente {{cliente}}, período {{periodo}}, objetivo da campanha {{objetivo}}.
Dados: {{tabela_de_metricas}}
Tarefa: produzir uma análise com:
1. Resumo executivo (3 bullets)
2. Principais destaques (o que funcionou)
3. Pontos de atenção (o que não performou e por quê)
4. Recomendações de otimização priorizadas (impacto x esforço)
5. Próximos passos sugeridos
Restrições:
- Baseie-se apenas nos dados fornecidos; sinalize hipóteses como tais.
- Use benchmarks somente se informados no contexto.
- Não exponha dados de verba do cliente fora de ferramentas homologadas.
Formato de saída: markdown, tom executivo, com números citando a métrica de origem.
```

## 🔤 Variáveis
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{{cliente}}` | Conta alvo | Conta Atlas |
| `{{periodo}}` | Janela analisada | 01–15/jun |
| `{{objetivo}}` | Meta da campanha | Conversão |
| `{{tabela_de_metricas}}` | CTR, CPC, ROAS, etc. | ... |

## ✅ Exemplo de saída esperada
```
## Resumo executivo
- ROAS de 3.4x, acima da meta de 3.0x...
```

## ⚠️ Riscos e cuidados
- Dados **confidenciais** (verba, ROAS): apenas em ferramentas homologadas.
- Revisão humana antes de envio ao cliente.

## 📝 Histórico de versões
| Versão | Data | Autor | Mudança |
|--------|------|-------|---------|
| 1.0.0 | 2026-03-05 | Equipe de Mídia | Criação e homologação |
