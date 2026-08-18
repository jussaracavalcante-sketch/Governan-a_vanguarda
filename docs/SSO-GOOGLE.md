# Login institucional (SSO) — Google Workspace

O PrMO permite entrar com a **conta Google corporativa** (`@vanguardamartech.com.br`),
além do login por e-mail/senha. O fluxo é **OAuth 2.0 Authorization Code**, tratado no
backend, restrito ao domínio corporativo, e cria o usuário no primeiro acesso (papel *User*).

Enquanto as credenciais **não** estiverem configuradas, o botão "Entrar com conta
institucional" fica **oculto** e o login por e-mail/senha segue funcionando.

## Como funciona
1. Usuário clica em **Entrar com conta institucional** → `GET /auth/google/login` (backend) redireciona ao Google (`hd=vanguardamartech.com.br`).
2. Google autentica e volta em `GET /auth/google/callback` (backend), que:
   - troca o `code` por token e consulta o perfil (`userinfo`);
   - valida `email_verified` e o **domínio** (`@vanguardamartech.com.br` / `hd`);
   - cria/recupera o usuário e emite o **JWT do PrMO**;
   - redireciona de volta ao frontend com `?token=…` (a página guarda o token e limpa a URL).

## Provisionamento (Google Cloud Console)
1. Acesse **console.cloud.google.com** → crie/《selecione um projeto (ex.: "PrMO").
2. **APIs e serviços → Tela de consentimento OAuth**:
   - Tipo: **Interno** (restringe à organização do Workspace).
   - Preencha nome do app, e-mail de suporte e domínios.
3. **APIs e serviços → Credenciais → Criar credenciais → ID do cliente OAuth**:
   - Tipo de aplicativo: **Aplicativo da Web**.
   - **URIs de redirecionamento autorizados**: `https://prmo-api.onrender.com/auth/google/callback`
   - (opcional, origens JS autorizadas): `https://prmo-frontend.vercel.app`
4. Copie o **Client ID** e o **Client Secret**.

## Configuração no backend (Render → serviço `prmo-api` → Environment)
| Variável | Valor |
|----------|-------|
| `GOOGLE_CLIENT_ID` | o Client ID gerado |
| `GOOGLE_CLIENT_SECRET` | o Client Secret gerado (**secreto — só no Render**) |
| `GOOGLE_REDIRECT_URI` | `https://prmo-api.onrender.com/auth/google/callback` |
| `CORPORATE_DOMAIN` | `vanguardamartech.com.br` (padrão) |
| `FRONTEND_URL` | `https://prmo-frontend.vercel.app` (fallback de retorno) |

Após salvar, o Render reinicia sozinho; o endpoint `GET /auth/google/config` passa a
responder `{"enabled": true}` e o botão aparece automaticamente no login (Vercel e Pages).

## Segurança
- O **Client Secret** nunca é commitado — vive apenas nas variáveis de ambiente do Render.
- O `state` do OAuth é **assinado com HMAC** (segredo do app) e expira em 10 min (anti-CSRF).
- Aceita apenas contas do domínio corporativo com e-mail verificado.
- O token do PrMO volta na URL e é imediatamente removido do histórico pela página.
