# NIA-001 — Norma Corporativa de Prompts

> Norma de Inteligência Artificial nº 001 · Vanguarda Martech
> Estrutura, homologação, versionamento e nomenclatura de prompts.

## §1. Objetivo

Padronizar a criação, o registro e a governança de prompts corporativos, garantindo
qualidade, rastreabilidade e proteção da propriedade intelectual.

## §2. Estrutura padrão do prompt

Todo prompt deve conter, no mínimo:

1. **Papel/persona** — quem o modelo assume.
2. **Contexto** — cliente, projeto, canal.
3. **Tarefa** — o que produzir, de forma inequívoca.
4. **Restrições** — brand safety, LGPD, limites de formato.
5. **Formato de saída** — estrutura esperada do resultado.

O modelo oficial está em [`../prompts/_template/PROMPT_TEMPLATE.md`](../prompts/_template/PROMPT_TEMPLATE.md).

## §3. Metadados obrigatórios (front matter)

| Campo | Obrigatório | Valores |
|-------|:-----------:|---------|
| `id` | ✅ | `AREA-NNN` |
| `titulo` | ✅ | texto |
| `area` | ✅ | Criação, Atendimento, Mídia, Comercial, Dados/BI, Governança |
| `categoria` | ✅ | texto livre |
| `versao` | ✅ | SemVer (`MAJOR.MINOR.PATCH`) |
| `status` | ✅ | `rascunho` \| `em-revisao` \| `homologado` \| `descontinuado` |
| `modelo_alvo` | ✅ | lista de modelos |
| `classificacao_dados` | ✅ | `publico` \| `uso-interno` \| `confidencial` \| `restrito` |
| `autor` | ✅ | nome |
| `homologado_por` | condicional | obrigatório quando `status: homologado` |
| `data_criacao` | ✅ | AAAA-MM-DD |
| `data_revisao` | ✅ | AAAA-MM-DD |
| `tags` | ✅ | lista |
| `usos` | opcional | inteiro |

## §4. Registro obrigatório

Nenhum prompt pode ser utilizado em produção sem estar registrado em
[`../prompts/`](../prompts/) e ter passado por Pull Request. Prompts "soltos" em
chats são considerados **não conformes**.

## §5. Nomenclatura

`<AREA>-<NNN>-<slug-curto>.md` (ex.: `MID-001-insights-performance.md`).
Siglas de área: `CRI`, `ATD`, `MID`, `COM`, `DAD`, `GOV`.

## §6. Homologação e revisão humana

- A promoção para `homologado` ocorre na revisão do PR por um **Manager/Admin**.
- Toda saída de IA destinada a **entrega externa** exige revisão humana registrada.
- Prompts homologados são revisados no mínimo a cada **6 meses** (`data_revisao`).

## §7. Versionamento (SemVer)

| Mudança | Incremento |
|---------|-----------|
| Correção mínima | `patch` |
| Melhoria compatível | `minor` |
| Reescrita / novo objetivo | `major` |

## §8. Descontinuação

Prompts obsoletos recebem `status: descontinuado`, mantêm o arquivo (histórico de PI)
e saem do índice de homologados no [`catálogo`](../prompts/README.md).

## §9. Ciclo de vida

```
rascunho ──▶ em-revisao ──▶ homologado ──▶ descontinuado
                 │                ▲
                 └──── ajustes ───┘
```
