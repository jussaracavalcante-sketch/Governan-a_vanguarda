---
id: AREA-000
titulo: Título descritivo do prompt
area: Área de negócio
categoria: Categoria/subcategoria
versao: 0.1.0
status: rascunho            # rascunho | em-revisao | homologado | descontinuado
modelo_alvo: [GPT-4, Claude 3]
classificacao_dados: uso-interno   # publico | uso-interno | confidencial | restrito
autor: Seu Nome
homologado_por: ""
data_criacao: AAAA-MM-DD
data_revisao: AAAA-MM-DD
tags: [tag1, tag2]
usos: 0
---

# {titulo}

## 🎯 Objetivo
Descreva em uma frase o que este prompt entrega e para qual contexto de negócio.

## 👤 Público / caso de uso
Quem usa, em que momento do fluxo e com que finalidade.

## 🧩 Prompt

> Copie o bloco abaixo. Substitua os campos entre `{{ }}` pelas variáveis reais.

```text
Você é {{papel/persona}} da Vanguarda Martech.
Contexto: {{contexto do cliente/projeto}}.
Tarefa: {{o que deve ser produzido}}.
Restrições:
- Respeite o brand book e o tom de voz do cliente {{cliente}}.
- Não utilize dados confidenciais fora de ferramentas homologadas.
- {{outras restrições}}
Formato de saída: {{formato esperado}}.
```

## 🔤 Variáveis
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{{papel/persona}}` | Persona que o modelo assume | Redator sênior |
| `{{cliente}}` | Conta/cliente alvo | Conta Atlas |

## ✅ Exemplo de saída esperada
Cole um exemplo curto e representativo do resultado ideal.

## ⚠️ Riscos e cuidados
- Classificação de dados aplicável e o que **não** inserir.
- Necessidade de revisão humana antes de entrega externa (política NIA-001).

## 📝 Histórico de versões
| Versão | Data | Autor | Mudança |
|--------|------|-------|---------|
| 0.1.0 | AAAA-MM-DD | Seu Nome | Criação (rascunho) |
