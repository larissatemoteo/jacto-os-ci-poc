# Jacto OS — Prova de Conceito de CI com Revisão por IA

Repositório de demonstração da integração de Inteligência Artificial
(Claude) no pipeline de Continuous Integration via GitHub Actions.

## Contexto

Prova de conceito desenvolvida no módulo ESMD10 (Engenharia de Software,
Inteli T13) no âmbito do Projeto Parceiro com a Jacto Drones. O objetivo
é validar tecnicamente a viabilidade de usar um LLM como revisor
automático de código dentro da esteira de CI proposta no projeto
Jacto Drones Operating System v0.1.

## Importante

Este repositório contém apenas código sintético e representativo, criado
exclusivamente para demonstração da esteira de CI. Não há código
proprietário, dados reais ou propriedade intelectual da Jacto Drones,
em conformidade com as restrições do TAPI do projeto.

## Estrutura

- `firmware/` — Código representativo da Frente 1 (software embarcado),
  em C. Função de saturação de controlador, sem relação com algoritmos
  reais de voo.
- `data/` — Código representativo da Frente 3 (dados e BI), em Python.
  Parser de log de telemetria sintético.
- `.github/workflows/` — Configuração do pipeline de CI com revisão
  automática por IA.

## Frentes representadas

| Frente | Linguagem | Arquivo |
|---|---|---|
| Firmware embarcado | C | `firmware/src/pid_saturation.c` |
| Dados e BI | Python | `data/telemetry_parser.py` |
