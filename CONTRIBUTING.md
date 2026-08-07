# Guia de Contribuição — VANGUARDIAN

Obrigado por contribuir com o repositório de prompts e propriedade intelectual da
Vanguarda Martech. Este guia vale tanto para **prompts** quanto para **código**.

> Ao contribuir, você concorda com a política de PI ([`docs/PROPRIEDADE-INTELECTUAL.md`](docs/PROPRIEDADE-INTELECTUAL.md))
> e com a norma NIA-001 ([`docs/NIA-001-norma-prompts.md`](docs/NIA-001-norma-prompts.md)).

## 🌿 Fluxo geral

1. Crie uma branch a partir da branch padrão: `feature/<descricao>` ou `prompt/<area>-<slug>`.
2. Faça as alterações seguindo os padrões abaixo.
3. Abra um **Pull Request** preenchendo o template.
4. Aguarde a revisão de um **Manager/Admin** da área (ver `CODEOWNERS`).
5. Após aprovação, o revisor promove/mescla.

## ✍️ Contribuindo com um PROMPT

1. Copie [`prompts/_template/PROMPT_TEMPLATE.md`](prompts/_template/PROMPT_TEMPLATE.md)
   para a pasta da área correspondente.
2. Renomeie seguindo `<AREA>-<NNN>-<slug>.md` (NIA-001 §5).
3. Preencha **todo** o front matter e todas as seções.
4. Inicie com `status: rascunho` (não defina `homologado_por`).
5. Atualize o índice em [`prompts/README.md`](prompts/README.md) se o prompt for promovido.

### Checklist do prompt (obrigatório no PR)
- [ ] Front matter completo e válido (NIA-001 §3)
- [ ] Nomenclatura correta
- [ ] `classificacao_dados` adequada
- [ ] Estrutura padrão (papel, contexto, tarefa, restrições, formato)
- [ ] Exemplo de saída incluído
- [ ] Riscos/cuidados documentados

## 💻 Contribuindo com CÓDIGO

- **Backend (Python)**: siga PEP 8; valide com `python -m compileall backend`.
- Rode os testes: `cd backend && pytest -v`.
- Não commite segredos — use `.env` (veja `.env.example`).

## 📝 Mensagens de commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(prompts): adiciona MID-002 análise de funil
fix(backend): corrige paginação em /prompts
docs(governanca): atualiza fluxo de homologação
```

## 🔐 Segurança

Nunca inclua dados confidenciais de clientes, credenciais ou chaves. Vulnerabilidades
devem ser reportadas conforme [`SECURITY.md`](SECURITY.md).

## ✅ Definição de pronto

Uma contribuição está pronta quando: passa no CI, segue os padrões, foi revisada por
um responsável da área e (para prompts) está em conformidade com a NIA-001.
