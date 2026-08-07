---
id: GOV-001
titulo: Revisão de Brand Safety
area: Governança
categoria: Compliance
versao: 1.0.0
status: homologado
modelo_alvo: [GPT-4, Claude 3]
classificacao_dados: uso-interno
autor: Diretoria de IA
homologado_por: Diretoria de IA
data_criacao: 2026-03-20
data_revisao: 2026-06-25
tags: [compliance, brand-safety, revisao, lgpd]
usos: 31
---

# Revisão de Brand Safety

## 🎯 Objetivo
Fazer uma verificação assistida de brand safety, conformidade e LGPD em uma peça
antes da entrega externa — como apoio à revisão humana, nunca em substituição a ela.

## 👤 Público / caso de uso
Governança e líderes de conta, no gate de revisão obrigatória (NIA-001 §6).

## 🧩 Prompt

```text
Você é revisor de governança e brand safety da Vanguarda Martech.
Contexto: cliente {{cliente}}, canal {{canal}}, tipo de peça {{tipo_de_peca}}.
Peça a revisar: {{conteudo}}
Diretrizes do cliente: {{brand_book_resumo}}
Tarefa: avaliar a peça e retornar:
1. Veredito: APROVADO | APROVADO COM RESSALVAS | REPROVADO
2. Checklist:
   - [ ] Tom de voz aderente ao brand book
   - [ ] Sem claims não comprovados
   - [ ] Sem dados sensíveis/confidenciais expostos (LGPD)
   - [ ] Sem conteúdo sensível/ofensivo/discriminatório
   - [ ] Direitos de imagem/música/terceiros observados
3. Ajustes recomendados (lista objetiva)
Restrições:
- Seja conservador: na dúvida, sinalize como ressalva.
- Esta análise NÃO substitui a aprovação humana registrada.
Formato de saída: markdown com o veredito em destaque.
```

## 🔤 Variáveis
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{{cliente}}` | Conta alvo | Conta Atlas |
| `{{tipo_de_peca}}` | Formato | Post estático |
| `{{conteudo}}` | Texto/descrição da peça | ... |
| `{{brand_book_resumo}}` | Diretrizes-chave | ... |

## ✅ Exemplo de saída esperada
```
**Veredito: APROVADO COM RESSALVAS**
- [x] Tom de voz aderente
- [ ] Claim "o melhor do mercado" precisa de comprovação...
```

## ⚠️ Riscos e cuidados
- Ferramenta de **apoio**: a decisão final e o registro de aprovação são humanos.
- Não inserir dados confidenciais do cliente fora de ferramentas homologadas.

## 📝 Histórico de versões
| Versão | Data | Autor | Mudança |
|--------|------|-------|---------|
| 1.0.0 | 2026-03-20 | Diretoria de IA | Criação e homologação |
