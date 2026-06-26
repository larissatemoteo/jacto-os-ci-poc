# Jacto OS — Prova de Conceito de IA na Esteira de CI

Prova de conceito (PoC) que demonstra a integração de Inteligência Artificial (Claude) na esteira de Continuous Integration, no contexto do projeto **Jacto Drones Operating System v0.1** (módulo ESMD10, Engenharia de Software, Inteli — Turma T13, Grupo 03).

## O que é este repositório

Este repositório é um **ambiente isolado de demonstração**. Ele prova, na prática, que é viável colocar uma camada de IA dentro da esteira de engenharia, com três aplicações distintas: revisão automática de código, escrutínio reforçado de itens de configuração críticos, e análise automatizada de logs de voo.

O código aqui é **sintético e representativo**. Não há código proprietário, dados reais ou propriedade intelectual da Jacto Drones, em conformidade com as restrições do TAPI do projeto.

## Relação com o projeto oficial

A esteira oficial do projeto está no **GitLab institucional do Inteli**, organizada em 7 stages (`smoke → lint → security → quality → redteam → integration → deploy`), rodando em runners Docker próprios com PX4-SITL.

Esta PoC vive no **GitHub** por uma razão técnica: a action oficial da Anthropic (`anthropics/claude-code-action`) roda nativamente em GitHub Actions, não em GitLab. Em vez de forçar a integração no GitLab institucional (onde o grupo não tem permissão de administrador para a configuração necessária), a prova de conceito foi isolada aqui, sem expor material da parceira.

No ambiente real da Jacto, que opera GitLab self-hosted com permissão de administrador, esta camada de IA plugaria diretamente nos stages da esteira. A limitação é do ambiente acadêmico, não da solução.

A análise completa de viabilidade está documentada no repositório oficial (GitLab), em `docs/viabilidade-ia-esteira.md`.

## Os três casos de uso de IA

### 1. Claude Code Review — revisão genérica

Revisa automaticamente o código de **todo** pull request, procurando bugs e problemas de lógica, e comenta no PR.

É deliberadamente **conservador**: usa um sistema de múltiplos agentes que só sinaliza problemas de alta confiança, para evitar falsos positivos. Estilo e melhorias sutis são ignorados por design.

Workflow: `.github/workflows/claude-code-review.yml`

### 2. Critical IC Guardian — guardião de item de configuração crítico

Dispara **apenas** quando um PR toca código crítico (`firmware/`). Faz análise reforçada de segurança, limites de operação, tratamento de erro e integridade de voo, e exige reconhecimento humano formal antes do merge, com um checklist obrigatório.

Materializa a **seção 2.6.3 do documento principal** do projeto, que propôs alerta inteligente em itens de configuração críticos. Ao contrário do review genérico, usa um prompt customizado e incisivo.

Onde se encaixaria na esteira real: como gate condicional no início, disparado pelo diff em caminhos críticos de firmware, exigindo aprovação antes de avançar.

Workflow: `.github/workflows/critical-ic-guardian.yml`

### 3. Flight Log Analysis — análise de log de voo

Quando há mudança na pasta de análise (ou por disparo manual), roda uma esteira que extrai a telemetria de um log de voo, manda um resumo para a IA, e gera um relatório de diagnóstico automático.

Responde à **Dor 1 do projeto**: na operação real da Jacto, a análise manual de log de voo leva de 1 a 3 dias. Esta esteira faz em segundos.

A arquitetura é em duas etapas desacopladas:

```
log.ulg  ──[extract_flight_summary.py]──►  resumo.json  ──[IA]──►  relatorio
 (23 MB)        extração + redução          (poucos KB)    análise    (texto)
```

A extração é determinística e barata (roda sem IA), e só o resumo enxuto vai para o modelo. Isso controla custo e evita enviar o log bruto de 23 MB para a IA.

Onde se encaixaria na esteira real: logo após o stage `integration`, que é onde o PX4-SITL roda e gera o log. Hoje a esteira descarta o log ao derrubar o container (`docker compose down -v`); bastaria um `docker cp` no `after_script` para persistir o log como artefato e habilitar a análise.

Workflow: `.github/workflows/flight-log-analysis.yml`

## Estrutura do repositório

```
.
├── README.md                       # Este arquivo
├── firmware/                       # Código representativo da Frente 1 (firmware embarcado)
│   ├── src/pid_saturation.c
│   └── tests/test_pid_saturation.c
├── data/                           # Código representativo da Frente 3 (dados e BI)
│   ├── telemetry_parser.py
│   └── test_telemetry_parser.py
├── flight-log-analysis/            # Análise de log de voo por IA
│   ├── extract_flight_summary.py   # Extrator (ULog -> resumo JSON)
│   ├── analyze_flight.py           # Analisador via API (referência)
│   ├── requirements.txt
│   ├── README.md
│   └── sample-logs/                # Log de voo real de exemplo (PX4-SITL)
└── .github/workflows/              # Os três workflows de IA + assistente @claude
```

## Como reproduzir

### Análise de log (local)

```bash
cd flight-log-analysis
pip install -r requirements.txt

# Extrair o resumo do log (roda sem IA)
python extract_flight_summary.py sample-logs/sitl_takeoff_rtl_2026-06-13.ulg --out resumo.json
```

A análise por IA roda automaticamente na esteira (GitHub Actions) quando um PR toca a pasta `flight-log-analysis/`, ou pode ser disparada manualmente pelo workflow.

### Ver os workflows em ação

Os PRs do repositório demonstram os três casos de uso disparando. Abrir um PR que toca `firmware/` e `flight-log-analysis/` aciona os três workflows simultaneamente.

## Autenticação e custo

Na PoC, a autenticação usa o token OAuth do Claude Max (assinatura existente), com custo zero. Para uso em produção na Jacto, seria a API corporativa da Anthropic, com custo por uso proporcional ao volume. A arquitetura foi desenhada para minimizar esse custo (resumo enxuto na análise de log, em vez do log bruto).

## Restrições

Código sintético, criado exclusivamente para demonstração. Não processa dados reais nem expõe propriedade intelectual da Jacto Drones, conforme o TAPI do projeto.
