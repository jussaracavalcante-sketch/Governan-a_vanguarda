# Gestão HEAD de IA — Backend API

API RESTful em **Python + FastAPI + SQLAlchemy** para o app Gestão HEAD de IA.
Banco próprio; **consulta** ao PrMO é somente leitura.

## Módulos

| Módulo | Descrição | Endpoint |
|---|---|---|
| Auth | Login JWT, refresh, me | `/auth` |
| Visão / Dashboard | Indicadores do HEAD + Visão do PrMO | `/head/dashboard` |
| Ativos | Controle de ativos digitais | `/head/assets` |
| Tarefas | Tarefas do dia a dia | `/head/tasks` |
| Indicadores | KPIs (meta vs. realizado) | `/head/indicators` |
| Relatórios | Consolidação mensal | `/head/report/{period}` |
| Licenças | Controle de licenças | `/head/licenses` |
| Processos | Otimização de processos (PDCA) | `/head/processes` |
| Conhecimento | Base de conhecimento | `/head/knowledge` |
| Health | Liveness / readiness / metrics | `/health` |

## Instalação

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Servidor: `http://localhost:8000` · Swagger: `http://localhost:8000/docs`

## Credencial inicial (seed)

- **Admin:** `admin@headia.app` / `admin123` (troque em produção)

## Variáveis de Ambiente

```env
APP_NAME=Gestão HEAD de IA API
DEBUG=True
DATABASE_URL=sqlite:///./head_ia.db
CORS_ORIGINS=["*"]
SECRET_KEY=change-me-in-production
PRMO_BASE_URL=
ADMIN_EMAIL=admin@headia.app
ADMIN_PASSWORD=admin123
```

## Testes

```bash
pytest -v
```
