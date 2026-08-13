"""
Gestão HEAD de IA — Seed
Popula os módulos com os dados do Projeto Executivo Head de IA
(Grupo Vanguarda · jul–dez/2026): fases, entregáveis e Indicadores de Sucesso.
Roda apenas quando as tabelas estão vazias.
"""
from datetime import date
from sqlalchemy.orm import Session

from head.models import Asset, DailyTask, License, Indicator, KnowledgeArticle, ProcessImprovement


def seed_head_data(db: Session):
    if db.query(Asset).first() or db.query(DailyTask).first() or db.query(Indicator).first():
        return

    today = date.today().isoformat()

    # ─────────────────── Ativos (stack e agentes por área) ───────────────────
    assets = [
        Asset(name="GPT-4o (OpenAI)", asset_type="Modelo LLM", vendor="OpenAI", owner="HEAD de IA",
              status="Ativo", environment="Produção", criticality="Alta", monthly_cost=1800.0,
              description="Modelo principal para geração de conteúdo e atendimento.", acquisition_date="2026-07-15"),
        Asset(name="Claude (Anthropic)", asset_type="Modelo LLM", vendor="Anthropic", owner="HEAD de IA",
              status="Ativo", environment="Produção", criticality="Alta", monthly_cost=1200.0,
              description="Análise de documentos longos, code review e governança.", acquisition_date="2026-07-15"),
        Asset(name="Agente de Atendimento", asset_type="Agente", vendor="Vanguarda", owner="Atendimento",
              status="Ativo", environment="Produção", criticality="Crítica", monthly_cost=0.0,
              description="Triagem e resposta de atendimento ao cliente (Fase 3).", acquisition_date="2026-08-01"),
        Asset(name="Agente de Mídia & Performance", asset_type="Agente", vendor="Vanguarda", owner="Mídia",
              status="Em avaliação", environment="Homologação", criticality="Alta", monthly_cost=0.0,
              description="Conexão de métricas de campanhas e geração de insights.", acquisition_date="2026-08-05"),
        Asset(name="Automação de Relatórios (n8n)", asset_type="Automação", vendor="n8n", owner="Ops IA",
              status="Ativo", environment="Produção", criticality="Média", monthly_cost=250.0,
              description="Pipeline de geração automática de relatórios executivos.", acquisition_date="2026-08-08"),
        Asset(name="Base de Conhecimento Corporativa", asset_type="Plataforma", vendor="Vanguarda", owner="HEAD de IA",
              status="Ativo", environment="Produção", criticality="Média", monthly_cost=0.0,
              description="Biblioteca de prompts, playbooks e trilhas (Fase 2).", acquisition_date="2026-08-01"),
    ]
    db.add_all(assets)

    # ─────────────────── Tarefas por fase do projeto ───────────────────
    tasks = [
        # Fase 1 — Diagnóstico e Governança (13–31 jul) — concluída
        DailyTask(title="Diagnóstico de maturidade em IA dos setores", description="Avaliação de 100% dos setores da agência.",
                  responsible="HEAD de IA", category="Fase 1 · Diagnóstico", status="Concluída", priority="Alta", task_date="2026-07-20", hours_spent=24.0),
        DailyTask(title="Mapa corporativo de processos críticos", description="Mapeamento e oportunidades de automação.",
                  responsible="HEAD de IA", category="Fase 1 · Diagnóstico", status="Concluída", priority="Alta", task_date="2026-07-23", hours_spent=18.0),
        DailyTask(title="Inventário de ferramentas de IA", description="Levantamento das ferramentas em uso pelas equipes.",
                  responsible="Ops IA", category="Fase 1 · Diagnóstico", status="Concluída", priority="Média", task_date="2026-07-25", hours_spent=10.0),
        DailyTask(title="Definição da stack tecnológica oficial", description="Arquitetura de IA oficial da empresa.",
                  responsible="HEAD de IA", category="Fase 1 · Arquitetura", status="Concluída", priority="Alta", task_date="2026-07-28", hours_spent=12.0),
        DailyTask(title="Política Corporativa de Uso de IA", description="Validada pela Diretoria.",
                  responsible="HEAD de IA", category="Fase 1 · Governança", status="Concluída", priority="Crítica", task_date="2026-07-30", hours_spent=16.0),
        DailyTask(title="Instituição do Comitê de Governança em IA", description="Comitê formalizado.",
                  responsible="HEAD de IA", category="Fase 1 · Governança", status="Concluída", priority="Alta", task_date="2026-07-31", hours_spent=6.0),
        # Fase 2 — Padronização e Capacitação (ago) — em andamento
        DailyTask(title="Implantação do ambiente corporativo de IA", description="Ambiente e ferramentas homologadas por departamento.",
                  responsible="Squad IA", category="Fase 2 · Padronização", status="Em andamento", priority="Alta", task_date=today, hours_spent=8.0),
        DailyTask(title="Criação da biblioteca corporativa de prompts", description="Modelos padronizados por área.",
                  responsible="HEAD de IA", category="Fase 2 · Padronização", status="Em andamento", priority="Alta", task_date=today, hours_spent=12.0),
        DailyTask(title="Trilhas de capacitação dos colaboradores", description="Treinamento e certificação interna.",
                  responsible="RH + HEAD de IA", category="Fase 2 · Capacitação", status="Em andamento", priority="Alta", task_date=today, hours_spent=10.0),
        DailyTask(title="Critérios de segurança da informação e compliance", description="Regras de segurança e conformidade no uso de IA.",
                  responsible="Segurança", category="Fase 2 · Compliance", status="Pendente", priority="Crítica", task_date=today, hours_spent=0.0),
        # Fase 3 — Automações (set–out) — planejada
        DailyTask(title="Automação dos fluxos de Atendimento e Criação", description="Integração de IA aos processos operacionais.",
                  responsible="Squad IA", category="Fase 3 · Automação", status="Pendente", priority="Alta", task_date="2026-09-05", hours_spent=0.0),
        DailyTask(title="Dashboards executivos em tempo real", description="Indicadores operacionais para as lideranças.",
                  responsible="BI + HEAD de IA", category="Fase 3 · BI", status="Pendente", priority="Média", task_date="2026-09-15", hours_spent=0.0),
    ]
    db.add_all(tasks)

    # ─────────────────── Licenças (stack homologada) ───────────────────
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

    # ─────────────────── Indicadores de Sucesso (KPIs) por fase ───────────────────
    indicators = [
        # Fase 1 — concluída (metas atingidas)
        Indicator(name="Setores avaliados (maturidade em IA)", category="Fase 1 · Governança", period="2026-07", unit="%",
                  target=100.0, actual=100.0, trend="Concluído", notes="Diagnóstico de 100% dos setores."),
        Indicator(name="Processos críticos mapeados", category="Fase 1 · Governança", period="2026-07", unit="%",
                  target=100.0, actual=100.0, trend="Concluído"),
        Indicator(name="Stack tecnológica oficial aprovada", category="Fase 1 · Arquitetura", period="2026-07", unit="%",
                  target=100.0, actual=100.0, trend="Concluído"),
        Indicator(name="Política de IA validada pela Diretoria", category="Fase 1 · Governança", period="2026-07", unit="%",
                  target=100.0, actual=100.0, trend="Concluído"),
        # Fase 2 — em andamento (agosto)
        Indicator(name="Colaboradores treinados em IA", category="Fase 2 · Capacitação", period="2026-08", unit="%",
                  target=100.0, actual=58.0, trend="Subindo"),
        Indicator(name="Departamentos com ferramentas homologadas", category="Fase 2 · Padronização", period="2026-08", unit="%",
                  target=100.0, actual=70.0, trend="Subindo"),
        Indicator(name="Biblioteca corporativa de prompts implantada", category="Fase 2 · Padronização", period="2026-08", unit="%",
                  target=100.0, actual=80.0, trend="Subindo"),
        Indicator(name="Adoção efetiva da IA", category="Fase 2 · Adoção", period="2026-08", unit="%",
                  target=80.0, actual=72.0, trend="Subindo", notes="Meta mínima: 80%."),
        # Fase 3 — automações (set–out)
        Indicator(name="Processos críticos automatizados", category="Fase 3 · Automação", period="2026-09", unit="%",
                  target=50.0, actual=12.0, trend="Subindo", notes="Meta mínima: 50%."),
        Indicator(name="Redução do tempo operacional", category="Fase 3 · Eficiência", period="2026-09", unit="%",
                  target=25.0, actual=6.0, trend="Subindo", notes="Meta mínima: 25%."),
        Indicator(name="Redução de retrabalho", category="Fase 3 · Eficiência", period="2026-09", unit="%",
                  target=20.0, actual=4.0, trend="Subindo", notes="Meta mínima: 20%."),
        Indicator(name="Dashboards executivos ativos", category="Fase 3 · BI", period="2026-09", unit="%",
                  target=100.0, actual=25.0, trend="Subindo"),
        # Fase 4 — consolidação (out–nov)
        Indicator(name="Colaboradores usando IA na rotina", category="Fase 4 · Consolidação", period="2026-11", unit="%",
                  target=90.0, actual=0.0, trend="Planejado"),
        Indicator(name="Redução de tempo (processos priorizados)", category="Fase 4 · Eficiência", period="2026-11", unit="%",
                  target=30.0, actual=0.0, trend="Planejado"),
        Indicator(name="Aumento de produtividade das equipes", category="Fase 4 · Consolidação", period="2026-11", unit="%",
                  target=25.0, actual=0.0, trend="Planejado"),
        Indicator(name="Satisfação interna com as soluções", category="Fase 4 · Qualidade", period="2026-11", unit="%",
                  target=85.0, actual=0.0, trend="Planejado"),
    ]
    db.add_all(indicators)

    # ─────────────────── Base de Conhecimento (entregáveis) ───────────────────
    articles = [
        KnowledgeArticle(title="Relatório de Maturidade em IA", category="Fase 1 · Diagnóstico",
                         summary="Resultado do diagnóstico de maturidade em IA de todos os setores.",
                         content="Diagnóstico por setor, nível de maturidade, lacunas e oportunidades de automação.",
                         tags="diagnóstico,maturidade,setores", author="HEAD de IA", status="Publicado", updated_date="2026-07-25"),
        KnowledgeArticle(title="Manual de Governança em IA", category="Fase 1 · Governança",
                         summary="Diretrizes, comitê e política corporativa de uso responsável de IA.",
                         content="1. Uso ético e seguro.\n2. Não inserir dados sensíveis em prompts.\n3. Registro de decisões automatizadas.\n4. Comitê de Governança em IA.",
                         tags="governança,política,compliance", author="HEAD de IA", status="Publicado", updated_date="2026-07-30"),
        KnowledgeArticle(title="Inventário de Ferramentas de IA", category="Fase 1 · Diagnóstico",
                         summary="Ferramentas de IA em uso e stack tecnológica oficial homologada.",
                         content="Lista de ferramentas por área, status de homologação e stack oficial.",
                         tags="ferramentas,stack,inventário", author="Ops IA", status="Publicado", updated_date="2026-07-28"),
        KnowledgeArticle(title="Roadmap Executivo do Programa de IA", category="Fase 1 · Estratégia",
                         summary="Cronograma executivo das 4 fases (jul–dez/2026).",
                         content="Fase 1 Diagnóstico · Fase 2 Padronização · Fase 3 Automações · Fase 4 Consolidação.",
                         tags="roadmap,fases,cronograma", author="HEAD de IA", status="Publicado", updated_date="2026-07-31"),
        KnowledgeArticle(title="Manual de Boas Práticas de IA", category="Fase 2 · Padronização",
                         summary="Boas práticas de uso da IA por departamento.",
                         content="Padrões de prompts, revisão de saídas, brand safety e segurança da informação.",
                         tags="boas-práticas,prompts,segurança", author="HEAD de IA", status="Publicado", updated_date=today),
        KnowledgeArticle(title="Base de Conhecimento Corporativa", category="Fase 2 · Capacitação",
                         summary="Trilhas de capacitação e certificação interna dos colaboradores.",
                         content="Trilhas por nível, materiais de treinamento e critérios de certificação.",
                         tags="capacitação,trilhas,certificação", author="RH + HEAD de IA", status="Rascunho", updated_date=today),
        KnowledgeArticle(title="Plano Diretor de IA 2027", category="Fase 4 · Estratégia",
                         summary="Plano estratégico de evolução da IA para 2027 (agentes autônomos, preditiva).",
                         content="Diretrizes 2027–2030: agentes autônomos, inteligência preditiva e hiperautomação.",
                         tags="2027,plano-diretor,estratégia", author="HEAD de IA", status="Rascunho", updated_date=today),
    ]
    db.add_all(articles)

    # ─────────────────── Otimização de Processos (Fase 3) ───────────────────
    processes = [
        ProcessImprovement(
            name="Automação de relatórios executivos", area="Mídia & BI", owner="HEAD de IA",
            stage="Medição", status="Em andamento", impact="Alto", effort="Baixo", ai_automation="Total",
            problem="Analistas gastam ~12h/mês compilando relatórios manualmente.",
            proposal="Coleta via integrações + geração de relatório com IA e envio automático.",
            time_before=12.0, time_after=1.5, cost_before=1800.0, cost_after=300.0,
            responsible="Ops IA", due_date="2026-09-15", notes="Quick win: alto impacto, baixo esforço."),
        ProcessImprovement(
            name="Automação do fluxo de Atendimento", area="Atendimento", owner="Squad IA",
            stage="Implementação", status="Em andamento", impact="Alto", effort="Médio", ai_automation="Parcial",
            problem="Tempo de primeira resposta acima do SLA em horários de pico.",
            proposal="Agente faz triagem e responde FAQs, escalando apenas casos complexos.",
            time_before=8.0, time_after=3.0, cost_before=0.0, cost_after=0.0,
            responsible="Squad IA", due_date="2026-10-01"),
        ProcessImprovement(
            name="Automação de rotinas Financeiras", area="Financeiro", owner="HEAD de IA",
            stage="Diagnóstico", status="Pendente", impact="Médio", effort="Médio", ai_automation="Parcial",
            problem="Conciliações e relatórios financeiros manuais e repetitivos.",
            proposal="Automação de conciliação e geração de relatórios com IA.",
            time_before=10.0, time_after=3.0, cost_before=0.0, cost_after=0.0,
            responsible="Financeiro + IA", due_date="2026-10-20"),
        ProcessImprovement(
            name="Padronização de prompts (governança)", area="Governança", owner="HEAD de IA",
            stage="Padronizado", status="Concluído", impact="Médio", effort="Baixo", ai_automation="Parcial",
            problem="Prompts entravam em produção sem revisão de brand safety.",
            proposal="Checklist + revisão padronizada antes da publicação (POP no SGQ).",
            time_before=4.0, time_after=1.0, cost_before=0.0, cost_after=0.0,
            responsible="HEAD de IA", due_date="2026-07-30", notes="Padronizado como POP no SGQ (ISO 9001)."),
    ]
    db.add_all(processes)

    db.commit()
