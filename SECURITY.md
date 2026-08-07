# Política de Segurança — VANGUARDIAN

## Reporte de vulnerabilidades

Encontrou uma vulnerabilidade ou exposição de dados? **Não abra uma issue pública.**

Reporte de forma privada à **Diretoria de Inteligência Artificial · Vanguarda Martech**,
com:
- Descrição do problema e impacto potencial;
- Passos para reproduzir;
- Componente afetado (`prompts/`, `backend/`, `frontend/`).

## Dados sensíveis

- Nunca commite credenciais, tokens ou dados de cliente. Use `.env` (ver `.env.example`).
- Dados `confidencial`/`restrito` só podem trafegar por ferramentas homologadas.
- Segredos vazados devem ser **rotacionados imediatamente** e o incidente reportado.

## Boas práticas aplicadas

- Autenticação JWT com access/refresh tokens e RBAC.
- Auditoria de operações sensíveis (`backend/audit/`).
- `.gitignore` bloqueia `.env`, chaves (`*.pem`, `*.key`) e bancos locais.

## Versões suportadas

A branch padrão recebe correções de segurança. Versões antigas não são suportadas.
