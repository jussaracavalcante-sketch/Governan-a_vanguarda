#!/usr/bin/env python3
"""
Validador da Biblioteca de Prompts (NIA-001).

Verifica, para cada prompt em prompts/<area>/*.md:
  - presença e formato do front matter YAML;
  - campos obrigatórios (NIA-001 §3);
  - valores válidos de `status` e `classificacao_dados`;
  - `homologado_por` preenchido quando `status: homologado`;
  - coerência entre o `id` do front matter e o nome do arquivo.

Uso:
    python scripts/validate_prompts.py

Sai com código 1 se houver qualquer não conformidade.
Não requer dependências externas (parser de front matter simplificado).
"""
from __future__ import annotations

import sys
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

REQUIRED_FIELDS = [
    "id", "titulo", "area", "categoria", "versao", "status",
    "modelo_alvo", "classificacao_dados", "autor",
    "data_criacao", "data_revisao", "tags",
]
VALID_STATUS = {"rascunho", "em-revisao", "homologado", "descontinuado"}
VALID_CLASSIF = {"publico", "uso-interno", "confidencial", "restrito"}

# Arquivos que não são prompts (catálogos/índices por pasta).
IGNORE_NAMES = {"README.md"}
IGNORE_DIRS = {"_template"}


def parse_front_matter(text: str) -> dict | None:
    """Parser mínimo de front matter YAML (chave: valor, uma por linha)."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return None
    fm: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return None  # fechamento '---' ausente


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    fm = parse_front_matter(path.read_text(encoding="utf-8"))
    if fm is None:
        return [f"{path}: front matter YAML ausente ou malformado"]

    for field in REQUIRED_FIELDS:
        if not fm.get(field):
            errors.append(f"{path}: campo obrigatório ausente/vazio: '{field}'")

    status = fm.get("status", "")
    if status and status not in VALID_STATUS:
        errors.append(f"{path}: status inválido '{status}' (use {sorted(VALID_STATUS)})")

    classif = fm.get("classificacao_dados", "")
    if classif and classif not in VALID_CLASSIF:
        errors.append(
            f"{path}: classificacao_dados inválida '{classif}' (use {sorted(VALID_CLASSIF)})"
        )

    if status == "homologado" and not fm.get("homologado_por"):
        errors.append(f"{path}: 'homologado_por' é obrigatório quando status=homologado")

    prompt_id = fm.get("id", "")
    if prompt_id and not path.name.startswith(prompt_id + "-"):
        errors.append(
            f"{path}: nome do arquivo deve começar com o id '{prompt_id}-'"
        )

    return errors


def main() -> int:
    if not PROMPTS_DIR.exists():
        print(f"Diretório não encontrado: {PROMPTS_DIR}")
        return 1

    all_errors: list[str] = []
    count = 0
    for md in sorted(PROMPTS_DIR.rglob("*.md")):
        if md.name in IGNORE_NAMES or any(part in IGNORE_DIRS for part in md.parts):
            continue
        count += 1
        all_errors.extend(validate_file(md))

    if all_errors:
        print(f"❌ {len(all_errors)} não conformidade(s) em {count} prompt(s):\n")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"✅ {count} prompt(s) validado(s) — todos em conformidade com a NIA-001.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
