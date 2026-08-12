"""
PRMO · Gestão HEAD de IA - Seed
Popula dados de exemplo do módulo HEAD de IA quando as tabelas estão vazias.
"""
from datetime import date
from sqlalchemy.orm import Session

from head.models import Asset, DailyTask, License, Indicator, KnowledgeArticle


def seed_head_data(db: Session):
    if db.query(Asset).first() or db.query(DailyTask).first():
        return

    period = date.today().strftime("%Y-%m")
    today = date.today().isoformat()

    assets = [
        Asset(name="GPT-4o (OpenAI)", asset_type="Modelo LLM", vendor="OpenAI", owner="HEAD de IA",
              status="Ativo", environment="Produção", criticality="Alta", monthly_cost=1800.0,
              description="Modelo principal para geração de conteúdo e atendimento.", acquisition_date="2024-06-01"),
        Asset(name="Claude (Anthropic)", asset_type="Modelo LLM", vendor="Anthropic", owner="HEAD de IA",
              status="Ativo", environment="Produção", criticality="Alta", monthly_cost=1200.0,
              description="Modelo para análise de documentos longos e code review.", acquisition_date="2024-09-15"),
        Asset(name="Agente de Atendimento VBOT", asset_type="Agente", vendor="Vanguarda", owner="Squad IA",
              status="Ativo", environment="Produção", criticality="Crítica", monthly_cost=0.0,
              description="Agente conversacional de atendimento ao cliente.", acquisition_date="2025-01-10"),
        Asset(name="Automação de Relatórios n8n", asset_type="Automação", vendor="n8n", owner="Ops IA",
              status="Ativo", environment="Produção", criticality="Média", monthly_cost=250.0,
              description="Pipeline de geração automática de relatórios mensais.", acquisition_date="2025-03-20"),
        Asset(name="Integração Google Ads MCP", asset_type="Integração", vendor="Google", owner="Squad Dados",
              status="Em avaliação", environment="Homologação", criticality="Média", monthly_cost=0.0,
              description="Conector de métricas de campanhas para o painel de IA.", acquisition_date="2026-07-01"),
    ]
    db.add_all(assets)

    tasks = [
        DailyTask(title="Revisão de brand safety dos prompts", description="Auditoria semanal dos prompts de atendimento.",
                  responsible="HEAD de IA", category="Governança", status="Concluída", priority="Alta",
                  task_date=today, hours_spent=2.0),
        DailyTask(title="Ajuste de custo de tokens - GPT-4o", description="Otimização de context window para reduzir custo.",
                  responsible="Squad IA", category="FinOps", status="Em andamento", priority="Média",
                  task_date=today, hours_spent=1.5),
        DailyTask(title="Treinamento base de conhecimento VBOT", description="Atualizar respostas do agente de atendimento.",
                  responsible="Ops IA", category="Operação", status="Pendente", priority="Alta",
                  task_date=today, hours_spent=0.0),
        DailyTask(title="Análise de incidente de latência", description="Investigar picos de latência na API.",
                  responsible="Squad IA", category="Confiabilidade", status="Bloqueada", priority="Crítica",
                  task_date=today, hours_spent=3.0),
    ]
    db.add_all(tasks)

    licenses = [
        License(software="OpenAI API", vendor="OpenAI", plan="Enterprise", seats_total=25, seats_used=18,
                monthly_cost=1800.0, status="Ativa", renewal_date="2026-12-01", owner="HEAD de IA"),
        License(software="Anthropic Claude", vendor="Anthropic", plan="Team", seats_total=15, seats_used=11,
                monthly_cost=1200.0, status="Ativa", renewal_date="2026-11-15", owner="HEAD de IA"),
        License(software="GitHub Copilot", vendor="GitHub", plan="Business", seats_total=30, seats_used=27,
                monthly_cost=570.0, status="Em renovação", renewal_date="2026-09-30", owner="Engenharia"),
        License(software="Midjourney", vendor="Midjourney", plan="Pro", seats_total=5, seats_used=3,
                monthly_cost=300.0, status="Ativa", renewal_date="2026-10-05", owner="Criação"),
    ]
    db.add_all(licenses)

    indicators = [
        Indicator(name="Uptime dos agentes de IA", category="Operacional", period=period, unit="%",
                  target=99.5, actual=99.8, trend="Estável"),
        Indicator(name="Custo por mil interações", category="Financeiro", period=period, unit="R$",
                  target=45.0, actual=38.5, trend="Caindo", notes="Redução após otimização de prompts."),
        Indicator(name="Adoção interna de IA", category="Adoção", period=period, unit="%",
                  target=70.0, actual=64.0, trend="Subindo"),
        Indicator(name="Satisfação (CSAT) do atendimento IA", category="Qualidade", period=period, unit="%",
                  target=90.0, actual=92.3, trend="Subindo"),
        Indicator(name="Incidentes de segurança/vazamento", category="Risco", period=period, unit="un",
                  target=0.0, actual=0.0, trend="Estável"),
    ]
    db.add_all(indicators)

    articles = [
        KnowledgeArticle(title="Política de uso responsável de IA", category="Governança",
                         summary="Diretrizes de uso ético e seguro de IA generativa na Vanguarda.",
                         content="1. Não inserir dados sensíveis em prompts.\n2. Revisar saídas antes de publicar.\n3. Registrar decisões automatizadas.",
                         tags="governança,ética,segurança", author="HEAD de IA", status="Publicado", updated_date=today),
        KnowledgeArticle(title="Runbook: incidente de latência de API", category="Operação",
                         summary="Passo a passo para diagnóstico e mitigação de latência.",
                         content="Verificar status do provedor, rate limits, tamanho de contexto e fallback de modelo.",
                         tags="runbook,operação,latência", author="Squad IA", status="Publicado", updated_date=today),
        KnowledgeArticle(title="Guia de otimização de custos de tokens", category="FinOps",
                         summary="Boas práticas para reduzir custo de tokens sem perder qualidade.",
                         content="Usar caching, comprimir contexto, escolher o modelo certo por tarefa.",
                         tags="finops,custo,tokens", author="Ops IA", status="Rascunho", updated_date=today),
    ]
    db.add_all(articles)

    db.commit()
