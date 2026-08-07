# VANGUARDIAN — Backend API

API RESTful em **Python + FastAPI + SQLAlchemy + SQLite** para governança digital.

## Módulos

| Módulo | Descrição | Endpoint |
|---|---|---|
| Auth | Login JWT, refresh, logout, me | `/auth` |
| Usuários | Controle de acessos e perfis | `/users` |
| Ferramentas | Catálogo de ferramentas digitais | `/tools` |
| Skills | Matriz de competências por time | `/skills` |
| Prompts | Biblioteca institucional de prompts | `/prompts` |
| Dashboard | Estatísticas consolidadas | `/dashboard` |
| Admin | Gestão, auditoria, métricas | `/admin` |
| Integrações | RD Station, ICLIPS, VJOB | `/integrations` |
| Health | Liveness / readiness / metrics | `/health` |

## Instalação

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Servidor: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

## Credenciais demo (seed)

- **Admin:** admin@vanguardian.com / admin123
- **Manager:** ana.souza@empresa.com / 123456

## Variáveis de Ambiente

```env
APP_NAME=VANGUARDIAN API
DEBUG=True
DATABASE_URL=sqlite:///./vanguardian.db
CORS_ORIGINS=["*"]
SECRET_KEY=change-me-in-production
```

## Frontend

Abra `/workspace/index.html` ou acesse a versão publicada.  
A UI funciona standalone (localStorage) e está preparada para integração com a API.

## Autor

JUSSARA NONATA CAVALCANTE
