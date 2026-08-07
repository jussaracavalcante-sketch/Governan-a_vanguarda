---
id: CRI-001
titulo: Legenda com Brand Voice
area: Criação
categoria: Social Media
versao: 1.2.0
status: homologado
modelo_alvo: [GPT-4, Claude 3]
classificacao_dados: uso-interno
autor: Equipe de Criação
homologado_por: Diretoria de IA
data_criacao: 2026-01-15
data_revisao: 2026-06-30
tags: [social, caption, tom-de-voz, brand]
usos: 143
---

# Legenda com Brand Voice

## 🎯 Objetivo
Gerar legendas para redes sociais fiéis ao tom de voz e ao brand book do cliente,
prontas para revisão humana antes da publicação.

## 👤 Público / caso de uso
Redatores e social media da equipe de Criação, na produção de conteúdo recorrente
para contas governadas.

## 🧩 Prompt

```text
Você é redator sênior de social media da Vanguarda Martech.
Contexto: cliente {{cliente}}, campanha {{campanha}}, canal {{canal}}.
Tarefa: escrever {{n}} opções de legenda para o post descrito abaixo.
Post: {{descricao_do_post}}
Restrições:
- Siga estritamente o tom de voz do brand book de {{cliente}}: {{resumo_tom_de_voz}}.
- Máximo de {{limite}} caracteres por legenda.
- Inclua no máximo {{n_hashtags}} hashtags relevantes e {{n_emojis}} emojis.
- Não faça promessas, dados ou claims não confirmados pelo cliente.
- Não utilize informações confidenciais fora de ferramentas homologadas.
Formato de saída: lista numerada, uma legenda por item, com CTA ao final.
```

## 🔤 Variáveis
| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{{cliente}}` | Conta alvo | Conta Aurora |
| `{{campanha}}` | Campanha em curso | Lançamento Verão |
| `{{canal}}` | Rede social | Instagram |
| `{{descricao_do_post}}` | Briefing visual/tema | Foto do produto na praia |
| `{{resumo_tom_de_voz}}` | Diretriz de voz | Descontraído, jovem, inclusivo |

## ✅ Exemplo de saída esperada
```
1. O verão chegou e a vibe é só boa. ☀️ Bora aproveitar? #VeraoAurora
2. ...
```

## ⚠️ Riscos e cuidados
- Dados **uso-interno**: não inserir informações de contrato ou verba.
- **Revisão humana obrigatória** antes de publicação externa (NIA-001 §6).

## 📝 Histórico de versões
| Versão | Data | Autor | Mudança |
|--------|------|-------|---------|
| 1.0.0 | 2026-01-15 | Equipe de Criação | Criação e homologação |
| 1.1.0 | 2026-04-10 | Equipe de Criação | Adição de controle de hashtags/emojis |
| 1.2.0 | 2026-06-30 | Equipe de Criação | Reforço de brand safety e CTA |
