# Política de Propriedade Intelectual — VANGUARDIAN

> Como a Vanguarda Martech trata prompts, automações e artefatos de IA como
> **ativos de propriedade intelectual (PI)**.

## 1. Titularidade

Todos os prompts, templates, automações, bases de conhecimento e demais artefatos
depositados neste repositório são de **propriedade exclusiva da Vanguarda Martech**,
nos termos do arquivo [`../LICENSE`](../LICENSE). Contribuições de colaboradores,
prestadores e parceiros são cedidas à Vanguarda Martech no ato do commit/PR.

## 2. O que é protegido

| Ativo | Onde vive | Proteção |
|-------|-----------|----------|
| Prompts institucionais | [`../prompts/`](../prompts/) | Versionados, homologados (NIA-001) |
| Estrutura padrão de prompt | [`NIA-001-norma-prompts.md`](NIA-001-norma-prompts.md) | Norma corporativa |
| Automações e integrações | [`../backend/integrations/`](../backend/integrations/) | Código proprietário |
| Bases de conhecimento de marca | Contas/clientes | Confidencial por cliente |

## 3. Classificação de dados

Todo ativo declara sua sensibilidade no metadado `classificacao_dados`:

| Nível | Definição | Regra de uso |
|-------|-----------|--------------|
| `publico` | Pode ser divulgado externamente | Sem restrição interna |
| `uso-interno` | Circulação apenas interna | Não publicar externamente |
| `confidencial` | Dados de cliente/negócio | Somente ferramentas homologadas |
| `restrito` | Sensível (LGPD, contratos) | Acesso por necessidade, com registro |

## 4. Cadeia de custódia

O `git` garante rastreabilidade: cada alteração registra **quem, quando e o quê**.
Nenhum prompt entra em produção sem passar por Pull Request (ver
[`../CONTRIBUTING.md`](../CONTRIBUTING.md)), preservando a autoria e a cadeia de
custódia da PI.

## 5. Uso de terceiros e IA generativa

- Conteúdo gerado por IA deve respeitar direitos de terceiros (imagem, música, texto).
- É vedado inserir PI da Vanguarda ou de clientes em ferramentas **não homologadas**.
- Saídas de IA são insumo: a **revisão humana** é obrigatória antes de entrega externa.

## 6. Vedações

Conforme [`../LICENSE`](../LICENSE), é proibido copiar, distribuir, sublicenciar,
vender ou fazer engenharia reversa dos ativos, bem como remover avisos de PI.

## 7. Contato

Dúvidas de PI: **Diretoria de Inteligência Artificial · Vanguarda Martech**.
