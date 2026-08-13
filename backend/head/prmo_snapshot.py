"""
Visão do PrMO — snapshot CONSULTIVO (somente leitura).

Retrato organizado dos dados de governança do PrMO, para exibição no painel
Gestão HEAD de IA. É uma consulta (o Head não grava nada no PrMO). Os números
refletem o estado do PrMO na data de referência abaixo; para atualizar, basta
regerar este snapshot a partir do banco de governança do PrMO.
"""

PRMO_SNAPSHOT = {
    "as_of": "2026-08-13",
    "source": "PrMO · Governança de IA (consulta)",
    "registry": {
        "total": 258,
        "by_type": [
            {"label": "Ativos de IA", "count": 93},
            {"label": "Base de conhecimento", "count": 52},
            {"label": "Diagnósticos", "count": 45},
            {"label": "Riscos", "count": 33},
            {"label": "Plano 30 dias", "count": 27},
            {"label": "Oportunidades", "count": 8},
        ],
    },
    "adoption": [
        {"area": "Criação & Conteúdo", "percent": 91},
        {"area": "Atendimento", "percent": 84},
        {"area": "Mídia & Performance", "percent": 78},
        {"area": "Comercial", "percent": 66},
    ],
    "initiatives": [
        {"name": "Padronização de briefs inteligentes", "area": "Atendimento + Planejamento + Criação", "status": "Em validação", "hours_saved": 0},
        {"name": "Agente de performance para mídia paga", "area": "Dados + Mídia · métricas e insights", "status": "Em produção", "hours_saved": 318},
        {"name": "Base de conhecimento de marca", "area": "Brand book, tom de voz e restrições", "status": "Risco: dados", "hours_saved": 0},
        {"name": "Automação de relatórios executivos", "area": "BI + Account Management", "status": "Em homologação", "hours_saved": 0},
    ],
    "incidents": [
        {"title": "Biblioteca de prompts — revisão de versão", "area": "Planejamento", "criticality": "Baixa", "status": "Conforme"},
        {"title": "Solicitação de ferramenta externa", "area": "Criação", "criticality": "Média", "status": "Em análise"},
        {"title": "Uso de dados confidenciais fora do fluxo", "area": "Conta Nexo", "criticality": "Alta", "status": "Ação necessária"},
    ],
    "clients": [
        {"name": "Vanguarda Institucional", "segment": "Conhecimento corporativo", "stage": "active", "ai_usage": "Playbook ativo"},
        {"name": "Conta Atlas", "segment": "Performance & conteúdo", "stage": "active", "ai_usage": "7 fluxos"},
        {"name": "Conta Aurora", "segment": "Social & audiovisual", "stage": "onboarding", "ai_usage": "Em onboarding"},
        {"name": "Conta Nexo", "segment": "Comercial B2B", "stage": "at-risk", "ai_usage": "1 pendência"},
    ],
    "hours_saved_total": 318,
}
