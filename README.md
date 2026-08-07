# VANGUARDIAN — Governança de IA, Prompts & Propriedade Intelectual

> **Repositório corporativo de prompts e propriedade intelectual da Vanguarda Martech.**
> *Uma única inteligência. Múltiplas aplicações. Resultados exponenciais.*

🔗 Protótipo / documentação: <https://govdigital.tess.page/>

---

## 📋 Visão Geral

O **VANGUARDIAN** transforma iniciativas isoladas de Inteligência Artificial em um
ecossistema **integrado, versionado, auditável e governado**. Este repositório é a
**fonte da verdade** dos ativos de IA da agência:

- 📚 **Biblioteca de prompts** versionada em arquivos ([`prompts/`](prompts/)) — o coração do repositório.
- 🛡️ **Propriedade intelectual** protegida e classificada ([`docs/PROPRIEDADE-INTELECTUAL.md`](docs/PROPRIEDADE-INTELECTUAL.md)).
- 🏛️ **Governança** com norma NIA-001, RBAC e trilha de auditoria ([`docs/`](docs/)).
- 🖥️ **Plataforma** de governança: SPA de dashboard + API FastAPI.

| Desafio | Solução VANGUARDIAN |
|---------|---------------------|
| Prompts perdidos em chats | **Biblioteca corporativa** versionada e homologada (NIA-001) |
| PI não protegida | **Classificação de dados** + licença proprietária + cadeia de custódia por `git` |
| Ferramentas de IA dispersas | **Stack homologada** com processo de aprovação |
| Falta de visibilidade | **Dashboard** de adoção, ROI e conformidade |

---

## 🗂️ Estrutura do repositório

```
Governan-a_vanguarda/
├── prompts/            # 📚 Biblioteca de prompts (fonte da verdade da PI)
│   ├── _template/      #    Modelo padrão NIA-001
│   ├── criacao/  atendimento/  midia/  comercial/  dados-bi/  governanca/
│   └── README.md       #    Catálogo, taxonomia e índice de homologados
├── docs/               # 📖 Governança e PI
│   ├── PROPRIEDADE-INTELECTUAL.md
│   ├── NIA-001-norma-prompts.md
│   ├── GOVERNANCA.md
│   ├── ARQUITETURA.md
│   └── SUPABASE.md     #    Banco de produção (infra externa)
├── backend/            # ⚙️ API FastAPI (auth, admin, prompts, observabilidade, integrações)
│   ├── Dockerfile
│   └── tests/          #    Testes smoke
├── frontend/           # 🖥️ Protótipo de governança (HTML estático, autocontido)
├── scripts/
│   └── validate_prompts.py   # Linter da biblioteca (rodado no CI)
├── .github/            # CI/CD, CODEOWNERS, templates de issue/PR
├── docker-compose.yml  # API + frontend
├── render.yaml         # Deploy backend (Render)
├── CONTRIBUTING.md  SECURITY.md  LICENSE
└── README.md
```

---

## 📚 Biblioteca de Prompts (o essencial)

Cada prompt é um arquivo `.md` com metadados (front matter) e estrutura padrão,
homologado conforme a **[Norma NIA-001](docs/NIA-001-norma-prompts.md)**.

```
prompts/<area>/<AREA>-<NNN>-<slug>.md    # ex.: midia/MID-001-insights-performance.md
```

- **Versionamento** por `git` + SemVer no metadado `versao` → cadeia de custódia da PI.
- **Homologação** via Pull Request revisado por Manager/Admin (ver [CONTRIBUTING](CONTRIBUTING.md)).
- **Classificação de dados** obrigatória: `publico` / `uso-interno` / `confidencial` / `restrito`.

Para criar um prompt: copie [`prompts/_template/PROMPT_TEMPLATE.md`](prompts/_template/PROMPT_TEMPLATE.md),
preencha e abra um PR. O CI valida a conformidade automaticamente:

```bash
python scripts/validate_prompts.py
```

---

## 🚀 Início Rápido

### Backend (API)

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env        # ajuste as variáveis
uvicorn main:app --reload
```

- API: <http://localhost:8000> · Swagger: <http://localhost:8000/docs> · Health: <http://localhost:8000/health/live>

### Frontend (protótipo estático)

O frontend é o protótipo VANGUARDIAN — um `index.html` **autocontido** (CSS/JS inline,
sem dependências, sem build). Abra direto no navegador ou sirva estaticamente:

```bash
cd frontend && python -m http.server 8080   # http://localhost:8080
```

É publicado no GitHub Pages pelo workflow `deploy-frontend-pages.yml` (sem etapa de build).

### Docker (API + frontend)

```bash
docker compose up --build
# API em :8000 · Frontend em :8080
```

### Credenciais de demonstração (seed)

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Admin | `admin@vanguardian.com` | `admin123` |
| Manager | `ana.souza@empresa.com` | `123456` |

---

## 📦 Módulos Funcionais

| Módulo | Frontend | Backend | Descrição |
|--------|:--------:|:-------:|-----------|
| **Dashboard** | ✅ | ✅ | KPIs executivos, adoção por área, atividades |
| **Biblioteca de Prompts** | ✅ | ✅ | Busca, filtro, favoritos, cópia rápida e CRUD |
| **Stack & Ferramentas** | ✅ | ✅ | Ferramentas por time/status, CRUD |
| **Pessoas & Skills** | ✅ | ✅ | Matriz de maturidade por time e competência |
| **Controle de Acessos** | ✅ | ✅ | Usuários, perfis (RBAC) e status |
| **Administração** | ✅ | ✅ | Painel, logs de auditoria, integrações |
| **Integrações** | 🔄 | ✅ | RD Station, ICLIPS, VJOB |

> 🔄 = UI preparada, backend em evolução

---

## 🔐 Segurança e Conformidade

- **Autenticação JWT** (access/refresh) + **RBAC** (Admin, Manager, User).
- **Auditoria** de operações sensíveis (quem, quando, o quê, antes/depois).
- **Classificação de dados** e **LGPD by design**.
- **Política de IA (NIA-001)** aplicada à biblioteca de prompts.
- Segredos **nunca** versionados — ver [`.gitignore`](.gitignore) e [`SECURITY.md`](SECURITY.md).

---

## 🛠️ Stack

| Camada | Tecnologia |
|--------|------------|
| Prompts/PI | Markdown + front matter YAML, versionado por `git`, validado no CI |
| Frontend | HTML5 + CSS3 + JS (protótipo autocontido, sem build) |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic 2, Python 3.11+ |
| Auth | python-jose (JWT), passlib/bcrypt |
| DB | SQLite (dev) / PostgreSQL (prod) |
| Observabilidade | structlog, prometheus-client, health checks |
| Deploy | Docker, Render, GitHub Pages |

---

## 🤝 Contribuindo

Leia o [CONTRIBUTING.md](CONTRIBUTING.md). Em resumo: crie uma branch, siga os padrões
(NIA-001 para prompts), abra um PR usando o template e aguarde a revisão do
responsável da área ([CODEOWNERS](.github/CODEOWNERS)).

---

## 📄 Licença

Proprietário — **Vanguarda Martech**. Uso interno autorizado. Ver [`LICENSE`](LICENSE)
e [`docs/PROPRIEDADE-INTELECTUAL.md`](docs/PROPRIEDADE-INTELECTUAL.md).

## 👥 Autoria

**Jussara Nonata Cavalcante** · Diretoria de Inteligência Artificial · Vanguarda Martech
