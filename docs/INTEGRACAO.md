# Integração automática das Atividades (Jira · Google Drive · Gmail)

O módulo **Minhas Atividades** é atualizado **automaticamente 3× ao dia**
(08h, 14h e 20h — horário de Brasília) por um serviço **Cron no Render**
(`app-head-ia-sync`), além do botão **"Sincronizar agora"** na tela.

Cada fonte é **independente e tolerante a falhas**: se a credencial de uma
ferramenta ainda não estiver configurada, ela aparece como *"não
configurado"* e as demais continuam sincronizando normalmente.

Todas as credenciais são definidas no **painel do Render → Environment**
(nunca versionadas no Git). Defina os mesmos valores nos **dois serviços**:
`app-head-ia-api` (web) e `app-head-ia-sync` (cron).

---

## 1) Jira (Atlassian)

Puxa as tarefas/bugs atribuídos a você (`assignee = currentUser()`),
ordenados pela última atualização.

**Como gerar o token:**
1. Acesse https://id.atlassian.com/manage-profile/security/api-tokens
2. **Create API token** → dê um nome (ex.: `head-ia-sync`) → **Copie** o valor.

**Variáveis no Render:**
| Variável | Valor |
|----------|-------|
| `JIRA_BASE_URL` | URL do seu Jira, ex.: `https://vanguardamartech-team-xxxx.atlassian.net` |
| `JIRA_EMAIL` | seu e-mail Atlassian (`jussara.cavalcante@vanguardamartech.com.br`) |
| `JIRA_API_TOKEN` | o token gerado acima |

---

## 2) Google Drive + Gmail (conta de serviço com delegação)

Para o servidor ler o **seu** Drive e Gmail sem abrir uma janela de login a
cada vez, usamos uma **conta de serviço do Google Cloud** com **delegação em
todo o domínio** (domain-wide delegation), que "impersona" o seu usuário
institucional apenas para **leitura**.

**Passo a passo (feito uma única vez, requer admin do Workspace):**

1. **Google Cloud Console** → crie/selecione um projeto.
2. **APIs & Services → Enable APIs**: habilite **Google Drive API** e **Gmail API**.
3. **IAM & Admin → Service Accounts → Create service account**
   (ex.: `head-ia-sync`). Em seguida **Keys → Add key → JSON** e baixe o arquivo.
4. Copie a **Client ID** (número) da conta de serviço.
5. **Admin do Google Workspace** (admin.google.com) →
   **Security → Access and data control → API controls → Domain-wide delegation
   → Add new**:
   - **Client ID**: a Client ID da conta de serviço
   - **Scopes** (somente leitura):
     ```
     https://www.googleapis.com/auth/drive.readonly,
     https://www.googleapis.com/auth/gmail.readonly
     ```

**Variáveis no Render:**
| Variável | Valor |
|----------|-------|
| `GOOGLE_SA_JSON` | **conteúdo completo** do arquivo JSON da conta de serviço |
| `GOOGLE_IMPERSONATE_SUBJECT` | seu e-mail (`jussara.cavalcante@vanguardamartech.com.br`) |
| `GMAIL_QUERY` | *(opcional)* filtro do Gmail. Padrão: e-mails dos últimos 30 dias com termos de compra/licença/fatura |

> Dica: ao colar o `GOOGLE_SA_JSON`, mantenha o JSON em uma única linha OU
> cole exatamente como está — o backend trata as quebras de linha da chave
> privada automaticamente.

---

## 3) Aplicar o serviço Cron no Render

Como o `render.yaml` passou a declarar um **novo serviço** (`app-head-ia-sync`),
o Render mostrará *"new service detected"* no Blueprint. Basta **aprovar/aplicar**
o Blueprint para que o cron seja criado e passe a rodar 3× ao dia.

---

## Como validar

- Botão **"Sincronizar agora"** na tela **Minhas Atividades** (perfil Gestor/Admin).
- Painel de status no topo da tela mostra, por fonte: **ok / erro / não configurado**
  e o horário da última execução.
- Endpoints: `POST /head/sync` (executa) e `GET /head/sync-status` (estado).
