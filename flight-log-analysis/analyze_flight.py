#!/usr/bin/env python3
"""
Analisador de voo por IA.

Pega o resumo estruturado gerado por extract_flight_summary.py e usa a API
da Anthropic (Claude) para produzir um relatorio de analise de voo em
linguagem natural, no papel de um analista de telemetria de drones.

Forma B: analise de voo nominal com identificacao de pontos de atencao reais.

Uso:
    # 1. Extrair o resumo
    python extract_flight_summary.py voo.ulg --out resumo.json
    # 2. Analisar
    python analyze_flight.py resumo.json

Autenticacao: usa a variavel de ambiente ANTHROPIC_API_KEY, ou o token
OAuth do Claude (CLAUDE_CODE_OAUTH_TOKEN) se configurado.

Projeto Jacto Drones OS v0.1 - prova de conceito de analise de voo por IA.
"""

import sys
import json
import argparse
import os

SYSTEM_PROMPT = """Voce e um analista senior de telemetria de voo de drones \
agricolas, atuando na esteira de engenharia da Jacto Drones. Sua tarefa e ler \
um resumo estruturado de um log de voo (extraido de um arquivo ULog do PX4) e \
produzir um relatorio de analise de voo claro, tecnico e acionavel.

Contexto importante:
- O drone e uma aeronave multirrotora agricola.
- O voo foi executado em ambiente de simulacao PX4-SITL.
- Este relatorio substitui parte da analise manual de logs, que hoje leva de \
1 a 3 dias na operacao real da parceira.

Estruture o relatorio em quatro secoes curtas:
1. PERFIL DO VOO: descreva em prosa o que aconteceu, usando as fases e a \
trajetoria de altitude. Seja concreto com os tempos e valores.
2. SAUDE DOS SUBSISTEMAS: comente bateria, GPS, vibracao e atitude, dizendo \
se cada um esta em faixa nominal e por que.
3. PONTOS DE ATENCAO: liste e interprete os pontos de atencao fornecidos. Se \
nao houver pontos criticos, diga isso com clareza, mas aponte qualquer \
observacao fina que mereca acompanhamento.
4. VEREDITO: uma conclusao de uma linha sobre se o voo foi nominal ou requer \
investigacao.

Regras:
- Nao invente dados que nao estao no resumo. Trabalhe apenas com os numeros \
fornecidos.
- Use linguagem tecnica mas legivel, como um engenheiro escreveria para outro.
- Seja honesto: se o voo foi limpo, diga que foi limpo. Nao force gravidade \
onde nao ha."""


def build_user_message(summary):
    return (
        "Analise o voo a seguir, cujo resumo estruturado foi extraido "
        "automaticamente do log ULog:\n\n"
        "```json\n" + json.dumps(summary, indent=2, ensure_ascii=False) + "\n```"
    )


def analyze(summary_path):
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    try:
        from anthropic import Anthropic
    except ImportError:
        print("ERRO: biblioteca 'anthropic' nao instalada.")
        print("Instale com: pip install anthropic")
        sys.exit(1)

    # O cliente usa ANTHROPIC_API_KEY do ambiente automaticamente.
    client = Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(summary)}],
    )

    report = "".join(
        block.text for block in message.content if block.type == "text"
    )
    return report


def main():
    ap = argparse.ArgumentParser(description="Analisa resumo de voo por IA.")
    ap.add_argument("resumo", help="Caminho do JSON gerado pelo extrator")
    ap.add_argument("--out", help="Caminho do relatorio de saida (opcional)")
    args = ap.parse_args()

    report = analyze(args.resumo)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Relatorio salvo em {args.out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
