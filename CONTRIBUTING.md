# Contribuindo — Gestão HEAD de IA

Obrigado por contribuir com o app **Gestão HEAD de IA**.

## Fluxo

1. Crie uma branch a partir da branch padrão: `feature/<descricao>` ou `fix/<descricao>`.
2. Faça commits pequenos e descritivos (Conventional Commits: `feat:`, `fix:`, `docs:`…).
3. Garanta que o CI passa localmente antes de abrir o PR:
   ```bash
   cd backend && pytest -v
   cd frontend && npm run build
   ```
4. Abra o Pull Request descrevendo **o quê** e **por quê**.

## Padrões

- **Backend:** Python + FastAPI + SQLAlchemy. Novos endpoints do app vão em `backend/head/`.
- **Frontend:** React + TypeScript + Vite. Novas telas em `frontend/src/pages/`.
- **PrMO:** o app apenas **consulta** o PrMO (somente leitura). Nada é gravado no PrMO.

## Revisão

Consulte `.github/CODEOWNERS` para os responsáveis por área.
