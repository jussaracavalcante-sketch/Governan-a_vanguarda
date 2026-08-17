"""
PRMO · Gestão HEAD de IA - Conectores de sincronização automática
=================================================================
Puxa as atividades das ferramentas do dia a dia (Jira, Google Drive, Gmail)
diretamente das APIs de cada serviço e grava/atualiza (upsert) na tabela
`head_activities`. Também registra o resultado de cada execução em
`head_sync_state` para a tela mostrar "última atualização".

Projeto para rodar de forma AUTÔNOMA no servidor (Render Cron 3x/dia) e
também sob demanda pelo botão "Sincronizar agora".

Princípios:
- Cada conector é TOLERANTE a falhas: se a credencial não estiver
  configurada, ele apenas registra "não configurado" e segue — nunca
  derruba a sincronização das outras fontes.
- Sem dependências novas pesadas: usa `httpx` (REST) e `jose` (assina o
  JWT da conta de serviço Google), ambos já no requirements.
"""
from __future__ import annotations

import base64
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Iterable

import httpx
from sqlalchemy.orm import Session

from config import get_settings
from head.models import Activity, SyncState

_TIMEOUT = httpx.Timeout(25.0, connect=10.0)


# ─────────────────────────── Upsert de atividade ───────────────────────────
def _dedup_key(source: str, reference: str, url: str, title: str) -> tuple:
    """Chave estável para evitar duplicar a mesma atividade a cada sync."""
    if reference:
        return (source, reference)
    if url:
        return (source, url)
    return (source, title[:120])


def upsert_activity(db: Session, *, source: str, title: str, reference: str = "",
                    category: str = "", status: str = "", priority: str = "",
                    url: str = "", activity_date: str = "") -> bool:
    """Insere ou atualiza uma atividade. Retorna True se foi criada (nova)."""
    title = (title or "").strip()[:300]
    if not title:
        return False

    q = db.query(Activity).filter(Activity.source == source)
    if reference:
        q = q.filter(Activity.reference == reference)
    elif url:
        q = q.filter(Activity.url == url)
    else:
        q = q.filter(Activity.title == title)
    existing = q.first()

    if existing:
        existing.title = title
        existing.category = category or existing.category
        existing.status = status or existing.status
        existing.priority = priority or existing.priority
        existing.url = url or existing.url
        if activity_date:
            existing.activity_date = activity_date
        return False

    db.add(Activity(
        source=source, title=title, reference=reference[:60], category=category[:120],
        status=status[:40], priority=priority[:20], url=url, activity_date=activity_date[:10],
    ))
    return True


def _record_state(db: Session, source: str, *, status: str, count: int, message: str = ""):
    st = db.query(SyncState).filter(SyncState.source == source).first()
    now = datetime.now(timezone.utc)
    if st:
        st.status = status
        st.last_count = count
        st.message = message[:300]
        st.last_run = now
    else:
        db.add(SyncState(source=source, status=status, last_count=count,
                         message=message[:300], last_run=now))


# ─────────────────────────── Jira ───────────────────────────
def sync_jira(db: Session) -> dict:
    s = get_settings()
    base = (s.jira_base_url or "").strip().rstrip("/")
    email = (s.jira_email or s.admin_email or "").strip()
    token = (s.jira_api_token or "").strip()
    if not (base and email and token):
        _record_state(db, "Jira", status="não configurado", count=0,
                      message="Defina JIRA_BASE_URL, JIRA_EMAIL e JIRA_API_TOKEN.")
        return {"source": "Jira", "ok": False, "configured": False, "created": 0}

    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Accept": "application/json"}
    jql = "assignee = currentUser() ORDER BY updated DESC"
    params = {"jql": jql, "maxResults": 30,
              "fields": "summary,status,priority,project,updated,duedate"}
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            r = client.get(f"{base}/rest/api/3/search", headers=headers, params=params)
            r.raise_for_status()
            issues = r.json().get("issues", [])
    except Exception as exc:  # noqa: BLE001
        _record_state(db, "Jira", status="erro", count=0, message=str(exc))
        return {"source": "Jira", "ok": False, "configured": True, "created": 0, "error": str(exc)}

    created = 0
    for it in issues:
        f = it.get("fields", {})
        updated = (f.get("updated") or "")[:10]
        if upsert_activity(
            db, source="Jira", title=f.get("summary", ""),
            reference=it.get("key", ""),
            category=(f.get("project") or {}).get("name", ""),
            status=(f.get("status") or {}).get("name", ""),
            priority=(f.get("priority") or {}).get("name", ""),
            url=f"{base}/browse/{it.get('key', '')}",
            activity_date=updated,
        ):
            created += 1
    _record_state(db, "Jira", status="ok", count=len(issues),
                  message=f"{len(issues)} itens ({created} novos)")
    return {"source": "Jira", "ok": True, "configured": True, "created": created, "total": len(issues)}


# ─────────────────────────── Google (token da conta de serviço) ───────────────────────────
def _google_access_token(scopes: Iterable[str]) -> str:
    """Obtém um access token do Google via JWT Bearer de uma conta de serviço
    com delegação em todo o domínio (impersona o usuário institucional)."""
    from jose import jwt  # dependência já presente (python-jose[cryptography])

    s = get_settings()
    raw = (s.google_sa_json or "").strip()
    if not raw:
        raise RuntimeError("GOOGLE_SA_JSON não configurado")
    info = json.loads(raw)
    subject = (s.google_impersonate_subject or s.admin_email or "").strip()
    private_key = info["private_key"].replace("\\n", "\n")

    now = int(time.time())
    claims = {
        "iss": info["client_email"],
        "sub": subject,
        "scope": " ".join(scopes),
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
    }
    assertion = jwt.encode(claims, private_key, algorithm="RS256")
    with httpx.Client(timeout=_TIMEOUT) as client:
        r = client.post("https://oauth2.googleapis.com/token", data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        })
        r.raise_for_status()
        return r.json()["access_token"]


# ─────────────────────────── Google Drive ───────────────────────────
def sync_drive(db: Session) -> dict:
    s = get_settings()
    if not (s.google_sa_json or "").strip():
        _record_state(db, "Drive", status="não configurado", count=0,
                      message="Defina GOOGLE_SA_JSON (conta de serviço com delegação).")
        return {"source": "Drive", "ok": False, "configured": False, "created": 0}
    try:
        token = _google_access_token(["https://www.googleapis.com/auth/drive.readonly"])
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "orderBy": "modifiedTime desc",
            "pageSize": 25,
            "q": "trashed = false and 'me' in owners",
            "fields": "files(id,name,mimeType,modifiedTime,webViewLink)",
            "corpora": "user",
        }
        with httpx.Client(timeout=_TIMEOUT) as client:
            r = client.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)
            r.raise_for_status()
            files = r.json().get("files", [])
    except Exception as exc:  # noqa: BLE001
        _record_state(db, "Drive", status="erro", count=0, message=str(exc))
        return {"source": "Drive", "ok": False, "configured": True, "created": 0, "error": str(exc)}

    _KIND = {
        "application/vnd.google-apps.document": "Documento",
        "application/vnd.google-apps.spreadsheet": "Planilha",
        "application/vnd.google-apps.presentation": "Apresentação",
        "application/vnd.google-apps.folder": "Pasta",
        "application/pdf": "PDF",
    }
    created = 0
    for fl in files:
        kind = _KIND.get(fl.get("mimeType", ""), "Arquivo")
        if upsert_activity(
            db, source="Drive", title=fl.get("name", ""),
            reference=(fl.get("id", "") or "")[:12],
            category=kind, status="Editado",
            url=fl.get("webViewLink", ""),
            activity_date=(fl.get("modifiedTime") or "")[:10],
        ):
            created += 1
    _record_state(db, "Drive", status="ok", count=len(files),
                  message=f"{len(files)} arquivos ({created} novos)")
    return {"source": "Drive", "ok": True, "configured": True, "created": created, "total": len(files)}


# ─────────────────────────── Gmail ───────────────────────────
def _header(payload: dict, name: str) -> str:
    for h in (payload or {}).get("headers", []):
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def sync_gmail(db: Session) -> dict:
    s = get_settings()
    if not (s.google_sa_json or "").strip():
        _record_state(db, "Gmail", status="não configurado", count=0,
                      message="Defina GOOGLE_SA_JSON (conta de serviço com delegação).")
        return {"source": "Gmail", "ok": False, "configured": False, "created": 0}
    query = (s.gmail_query or "newer_than:30d (compra OR licença OR licenca OR assinatura OR "
             "invoice OR fatura OR renovação OR renovacao OR pagamento)").strip()
    try:
        token = _google_access_token(["https://www.googleapis.com/auth/gmail.readonly"])
        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(timeout=_TIMEOUT) as client:
            lst = client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers=headers, params={"q": query, "maxResults": 20})
            lst.raise_for_status()
            ids = [m["id"] for m in lst.json().get("messages", [])]
            msgs = []
            for mid in ids:
                mr = client.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}",
                    headers=headers,
                    params={"format": "metadata",
                            "metadataHeaders": ["Subject", "From", "Date"]})
                if mr.status_code == 200:
                    msgs.append(mr.json())
    except Exception as exc:  # noqa: BLE001
        _record_state(db, "Gmail", status="erro", count=0, message=str(exc))
        return {"source": "Gmail", "ok": False, "configured": True, "created": 0, "error": str(exc)}

    created = 0
    for m in msgs:
        payload = m.get("payload", {})
        subject = _header(payload, "Subject") or "(sem assunto)"
        sender = _header(payload, "From")
        ts = m.get("internalDate")
        adate = ""
        if ts:
            try:
                adate = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            except Exception:  # noqa: BLE001
                adate = ""
        if upsert_activity(
            db, source="Gmail", title=subject,
            reference=(m.get("id", "") or "")[:16],
            category=sender[:120], status="Recebido",
            url=f"https://mail.google.com/mail/u/0/#all/{m.get('id', '')}",
            activity_date=adate,
        ):
            created += 1
    _record_state(db, "Gmail", status="ok", count=len(msgs),
                  message=f"{len(msgs)} e-mails ({created} novos)")
    return {"source": "Gmail", "ok": True, "configured": True, "created": created, "total": len(msgs)}


# ─────────────────────────── Orquestração ───────────────────────────
def sync_all(db: Session) -> dict:
    """Executa todos os conectores habilitados e faz um único commit."""
    results = []
    for fn in (sync_jira, sync_drive, sync_gmail):
        try:
            results.append(fn(db))
        except Exception as exc:  # noqa: BLE001
            results.append({"source": fn.__name__, "ok": False, "error": str(exc)})
    db.commit()
    created = sum(r.get("created", 0) for r in results)
    return {
        "ok": True,
        "created": created,
        "sources": results,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
